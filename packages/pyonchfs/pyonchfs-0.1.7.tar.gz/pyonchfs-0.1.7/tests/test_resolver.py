"""Tests for OnchfsResolver core functionality."""

import gzip
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from onchfs.resolver import OnchfsResolver
from onchfs import Network


class TestOnchfsResolverCore:
    """Test OnchfsResolver core methods."""

    @patch("onchfs.resolver.pytezos")
    @patch("onchfs.resolver.validate_directory_hash", return_value=True)
    def test_read_directory_success(
        self, mock_validate, mock_pytezos, mock_directory_data
    ):
        """Test successful directory reading."""
        # Set up mocks
        mock_client = Mock()
        mock_contract = Mock()
        mock_pytezos.using.return_value = mock_client
        mock_client.contract.return_value = mock_contract
        mock_contract.read_directory.return_value.run_view.return_value = (
            mock_directory_data["directory_contents"]
        )

        # Create resolver and test
        resolver = OnchfsResolver(network=Network.MAINNET)
        sample_directory_hash = (
            "f8020273fba472a3e87baf6eb0f3929915edabace0fa409a261c4c4fa6684b21"
        )

        result = resolver.read_directory(sample_directory_hash)

        # Verify the contract call
        mock_contract.read_directory.assert_called_once_with(sample_directory_hash)

        # Verify the result
        assert result == mock_directory_data["directory_contents"]
        assert "index.html" in result
        assert "image.png" in result
        assert "compressed.txt" in result

    @patch("onchfs.resolver.pytezos")
    @patch("onchfs.resolver.validate_directory_hash", return_value=False)
    def test_read_directory_invalid_hash(self, mock_validate, mock_pytezos):
        """Test reading directory with invalid hash."""
        mock_client = Mock()
        mock_pytezos.using.return_value = mock_client

        resolver = OnchfsResolver(network=Network.MAINNET)
        invalid_hash = "invalid"

        with pytest.raises(ValueError, match="Invalid directory hash"):
            resolver.read_directory(invalid_hash)

    @patch("onchfs.resolver.pytezos")
    @patch("onchfs.resolver.validate_directory_hash", return_value=True)
    def test_read_directory_contract_error(self, mock_validate, mock_pytezos):
        """Test reading directory when contract raises error."""
        mock_client = Mock()
        mock_contract = Mock()
        mock_pytezos.using.return_value = mock_client
        mock_client.contract.return_value = mock_contract
        mock_contract.read_directory.return_value.run_view.side_effect = Exception(
            "Contract error"
        )

        resolver = OnchfsResolver(network=Network.MAINNET)
        sample_directory_hash = (
            "f8020273fba472a3e87baf6eb0f3929915edabace0fa409a261c4c4fa6684b21"
        )

        with pytest.raises(RuntimeError, match="Failed to read directory"):
            resolver.read_directory(sample_directory_hash)

    @patch("onchfs.resolver.pytezos")
    def test_read_file_with_string_hash(self, mock_pytezos, mock_directory_data):
        """Test reading file with string hash."""
        mock_client = Mock()
        mock_contract = Mock()
        mock_pytezos.using.return_value = mock_client
        mock_client.contract.return_value = mock_contract

        file_hash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
        expected_inode = mock_directory_data["file_inodes"][file_hash]
        mock_contract.read_file.return_value.run_view.return_value = expected_inode

        resolver = OnchfsResolver(network=Network.MAINNET)
        result = resolver.read_file(file_hash)

        # Verify the contract call was made with bytes
        mock_contract.read_file.assert_called_once()
        call_args = mock_contract.read_file.call_args[0][0]
        assert isinstance(call_args, bytes)

        # Verify the result
        assert result == expected_inode

    @patch("onchfs.resolver.pytezos")
    def test_read_file_with_bytes_hash(self, mock_pytezos, mock_directory_data):
        """Test reading file with bytes hash."""
        mock_client = Mock()
        mock_contract = Mock()
        mock_pytezos.using.return_value = mock_client
        mock_client.contract.return_value = mock_contract

        file_hash = bytes.fromhex(
            "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
        )
        expected_inode = mock_directory_data["file_inodes"][file_hash.hex()]
        mock_contract.read_file.return_value.run_view.return_value = expected_inode

        resolver = OnchfsResolver(network=Network.MAINNET)
        result = resolver.read_file(file_hash)

        # Verify the contract call
        mock_contract.read_file.assert_called_once_with(file_hash)

        # Verify the result
        assert result == expected_inode

    @patch("onchfs.resolver.pytezos")
    def test_read_file_contract_error(self, mock_pytezos):
        """Test reading file when contract raises error."""
        mock_client = Mock()
        mock_contract = Mock()
        mock_pytezos.using.return_value = mock_client
        mock_client.contract.return_value = mock_contract
        mock_contract.read_file.return_value.run_view.side_effect = Exception(
            "Contract error"
        )

        resolver = OnchfsResolver(network=Network.MAINNET)
        file_hash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"

        with pytest.raises(RuntimeError, match="Failed to read file"):
            resolver.read_file(file_hash)


class TestOnchfsResolverExtraction:
    """Test OnchfsResolver file extraction functionality."""

    def test_extract_directory_success(
        self, mock_resolver, sample_directory_hash, temp_dir, mock_directory_data
    ):
        """Test successful directory extraction."""
        # Mock the read methods to return our test data
        mock_resolver.read_directory.return_value = mock_directory_data[
            "directory_contents"
        ]

        def mock_read_file(file_hash):
            if isinstance(file_hash, bytes):
                file_hash = file_hash.hex()
            return mock_directory_data["file_inodes"].get(file_hash, {})

        mock_resolver.read_file.side_effect = mock_read_file

        # Test extraction
        result = mock_resolver.extract_directory(
            sample_directory_hash, temp_dir, verbose=False
        )

        # Verify calls were made
        mock_resolver.read_directory.assert_called_once_with(sample_directory_hash)
        assert mock_resolver.read_file.call_count == 3  # Three files in test data

        # Verify result structure
        assert isinstance(result, dict)
        assert len(result) == 3
        assert "index.html" in result
        assert "image.png" in result
        assert "compressed.txt" in result

        # Verify files were created
        for filename, filepath in result.items():
            assert Path(filepath).exists()

    def test_extract_directory_with_gzip_decompression(
        self, mock_resolver, sample_directory_hash, temp_dir, mock_directory_data
    ):
        """Test directory extraction with gzip decompression."""
        # Create a directory with only the compressed file
        compressed_directory = {
            "compressed.txt": mock_directory_data["directory_contents"][
                "compressed.txt"
            ]
        }

        mock_resolver.read_directory.return_value = compressed_directory

        def mock_read_file(file_hash):
            if isinstance(file_hash, bytes):
                file_hash = file_hash.hex()
            return mock_directory_data["file_inodes"].get(file_hash, {})

        mock_resolver.read_file.side_effect = mock_read_file

        # Test extraction
        result = mock_resolver.extract_directory(
            sample_directory_hash, temp_dir, verbose=False
        )

        # Verify the compressed file was processed
        assert "compressed.txt" in result
        compressed_file_path = Path(result["compressed.txt"])
        assert compressed_file_path.exists()

        # Verify the content was decompressed (should contain "foo")
        content = compressed_file_path.read_text()
        assert "foo" in content

    def test_extract_directory_file_processing_error(
        self, mock_resolver, sample_directory_hash, temp_dir, mock_directory_data
    ):
        """Test directory extraction when file processing fails."""
        mock_resolver.read_directory.return_value = mock_directory_data[
            "directory_contents"
        ]

        # Mock read_file to raise an error for one file
        def mock_read_file_with_error(file_hash):
            if isinstance(file_hash, bytes):
                file_hash = file_hash.hex()
            if (
                file_hash
                == "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
            ):
                raise Exception("File processing error")
            return mock_directory_data["file_inodes"].get(file_hash, {})

        mock_resolver.read_file.side_effect = mock_read_file_with_error

        # Test extraction (should continue despite error)
        result = mock_resolver.extract_directory(
            sample_directory_hash, temp_dir, verbose=False
        )

        # Should have processed 2 out of 3 files (skipped the error one)
        assert len(result) == 2
        assert "index.html" not in result  # This one failed
        assert "image.png" in result
        assert "compressed.txt" in result

    def test_extract_directory_creates_target_directory(
        self, mock_resolver, sample_directory_hash, temp_dir, mock_directory_data
    ):
        """Test that extract_directory creates the target directory if it doesn't exist."""
        # Use a subdirectory that doesn't exist yet
        target_dir = Path(temp_dir) / "new_subdir" / "nested"

        mock_resolver.read_directory.return_value = {"test.txt": b"hash"}
        mock_resolver.read_file.return_value = {
            "content": b"test content",
            "metadata": b"\x00\x00\x00\x00",  # Empty HPACK metadata
        }

        # Test extraction
        result = mock_resolver.extract_directory(
            sample_directory_hash, str(target_dir), verbose=False
        )

        # Verify the directory was created
        assert target_dir.exists()
        assert target_dir.is_dir()


class TestOnchfsResolverFileOperations:
    """Test OnchfsResolver individual file operations."""

    def test_get_file_content_success(
        self,
        mock_resolver,
        sample_directory_hash,
        mock_directory_data,
        sample_text_file_content,
    ):
        """Test successful file content retrieval."""
        mock_resolver.read_directory.return_value = mock_directory_data[
            "directory_contents"
        ]

        def mock_read_file(file_hash):
            if isinstance(file_hash, bytes):
                file_hash = file_hash.hex()
            return mock_directory_data["file_inodes"].get(file_hash, {})

        mock_resolver.read_file.side_effect = mock_read_file

        result = mock_resolver.get_file_content(sample_directory_hash, "index.html")

        # Verify calls
        mock_resolver.read_directory.assert_called_once_with(sample_directory_hash)

        # Verify result
        assert result == sample_text_file_content

    def test_get_file_content_with_gzip(
        self, mock_resolver, sample_directory_hash, mock_directory_data
    ):
        """Test file content retrieval with gzip decompression."""
        mock_resolver.read_directory.return_value = mock_directory_data[
            "directory_contents"
        ]

        def mock_read_file(file_hash):
            if isinstance(file_hash, bytes):
                file_hash = file_hash.hex()
            return mock_directory_data["file_inodes"].get(file_hash, {})

        mock_resolver.read_file.side_effect = mock_read_file

        result = mock_resolver.get_file_content(sample_directory_hash, "compressed.txt")

        # Verify the content was decompressed
        assert result == b"foo"

    def test_get_file_content_file_not_found(
        self, mock_resolver, sample_directory_hash, mock_directory_data
    ):
        """Test file content retrieval when file doesn't exist."""
        mock_resolver.read_directory.return_value = mock_directory_data[
            "directory_contents"
        ]

        with pytest.raises(
            FileNotFoundError, match="File not_found.txt not found in directory"
        ):
            mock_resolver.get_file_content(sample_directory_hash, "not_found.txt")

    def test_get_file_metadata_success(
        self, mock_resolver, sample_directory_hash, mock_directory_data
    ):
        """Test successful file metadata retrieval."""
        mock_resolver.read_directory.return_value = mock_directory_data[
            "directory_contents"
        ]

        def mock_read_file(file_hash):
            if isinstance(file_hash, bytes):
                file_hash = file_hash.hex()
            return mock_directory_data["file_inodes"].get(file_hash, {})

        mock_resolver.read_file.side_effect = mock_read_file

        result = mock_resolver.get_file_metadata(sample_directory_hash, "index.html")

        # Verify calls
        mock_resolver.read_directory.assert_called_once_with(sample_directory_hash)

        # Verify result structure
        assert isinstance(result, dict)
        assert "content-type" in result
        assert result["content-type"] == "text/html"

    def test_get_file_metadata_file_not_found(
        self, mock_resolver, sample_directory_hash, mock_directory_data
    ):
        """Test metadata retrieval when file doesn't exist."""
        mock_resolver.read_directory.return_value = mock_directory_data[
            "directory_contents"
        ]

        with pytest.raises(
            FileNotFoundError, match="File not_found.txt not found in directory"
        ):
            mock_resolver.get_file_metadata(sample_directory_hash, "not_found.txt")


class TestOnchfsResolverInitialization:
    """Test OnchfsResolver initialization."""

    @patch("onchfs.resolver.pytezos")
    def test_resolver_initialization_default(self, mock_pytezos):
        """Test resolver initialization with default parameters."""
        mock_client = Mock()
        mock_contract = Mock()
        mock_client.contract.return_value = mock_contract
        mock_pytezos.using.return_value = mock_client

        resolver = OnchfsResolver()

        assert resolver.network == Network.MAINNET
        assert resolver.contract_address is not None
        assert resolver.client == mock_client
        assert resolver.contract == mock_contract

    @patch("onchfs.resolver.pytezos")
    def test_resolver_initialization_custom_network(self, mock_pytezos):
        """Test resolver initialization with custom network."""
        mock_client = Mock()
        mock_pytezos.using.return_value = mock_client

        resolver = OnchfsResolver(network=Network.GHOSTNET)

        assert resolver.network == Network.GHOSTNET
        mock_pytezos.using.assert_called_once_with(shell=Network.GHOSTNET.value)

    @patch("onchfs.resolver.pytezos")
    def test_resolver_initialization_custom_contract(self, mock_pytezos):
        """Test resolver initialization with custom contract address."""
        mock_client = Mock()
        mock_pytezos.using.return_value = mock_client
        custom_address = "KT1CustomContractAddress"

        resolver = OnchfsResolver(contract_address=custom_address)

        assert resolver.contract_address == custom_address
        mock_client.contract.assert_called_once_with(custom_address)
