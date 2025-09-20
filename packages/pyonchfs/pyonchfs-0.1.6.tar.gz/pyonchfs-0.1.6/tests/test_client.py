"""Tests for OnchfsClient download functionality."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from onchfs import OnchfsClient, Network
from onchfs.resolver import OnchfsResolver


class TestOnchfsClientDownload:
    """Test OnchfsClient download methods."""

    def test_download_directory_success(
        self, mock_onchfs_client, sample_directory_hash, temp_dir
    ):
        """Test successful directory download."""

        # Mock the extract_directory method to actually create files
        def mock_extract(directory_hash, target_dir, verbose=True):
            target_path = Path(target_dir)
            target_path.mkdir(parents=True, exist_ok=True)

            # Create mock files
            files = {
                "index.html": target_path / "index.html",
                "image.png": target_path / "image.png",
                "compressed.txt": target_path / "compressed.txt",
            }

            for filename, filepath in files.items():
                filepath.write_text(f"Mock content for {filename}")

            return {filename: str(filepath) for filename, filepath in files.items()}

        mock_onchfs_client.resolver.extract_directory.side_effect = mock_extract

        # Test the download
        result = mock_onchfs_client.download_directory(sample_directory_hash, temp_dir)

        # Verify the call was made correctly
        mock_onchfs_client.resolver.extract_directory.assert_called_once_with(
            sample_directory_hash, temp_dir, True
        )

        # Verify the result
        assert isinstance(result, dict)
        assert len(result) == 3
        assert "index.html" in result
        assert "image.png" in result
        assert "compressed.txt" in result

    def test_download_directory_with_verbose_false(
        self, mock_onchfs_client, sample_directory_hash, temp_dir
    ):
        """Test directory download with verbose=False."""
        mock_onchfs_client.download_directory(
            sample_directory_hash, temp_dir, verbose=False
        )

        mock_onchfs_client.resolver.extract_directory.assert_called_once_with(
            sample_directory_hash, temp_dir, False
        )

    def test_get_file_success(
        self, mock_onchfs_client, sample_directory_hash, sample_text_file_content
    ):
        """Test successful file retrieval."""
        # Mock the get_file_content method
        mock_onchfs_client.resolver.get_file_content.return_value = (
            sample_text_file_content
        )

        result = mock_onchfs_client.get_file(sample_directory_hash, "index.html")

        # Verify the call
        mock_onchfs_client.resolver.get_file_content.assert_called_once_with(
            sample_directory_hash, "index.html"
        )

        # Verify the result
        assert result == sample_text_file_content

    def test_get_file_not_found(self, mock_onchfs_client, sample_directory_hash):
        """Test file retrieval when file doesn't exist."""
        # Mock the resolver to raise FileNotFoundError
        mock_onchfs_client.resolver.get_file_content.side_effect = FileNotFoundError(
            "File not_found.txt not found in directory"
        )

        with pytest.raises(
            FileNotFoundError, match="File not_found.txt not found in directory"
        ):
            mock_onchfs_client.get_file(sample_directory_hash, "not_found.txt")

    def test_get_file_metadata_success(self, mock_onchfs_client, sample_directory_hash):
        """Test successful file metadata retrieval."""
        expected_metadata = {
            "content-type": "text/html",
            "content-length": "100",
        }
        mock_onchfs_client.resolver.get_file_metadata.return_value = expected_metadata

        result = mock_onchfs_client.get_file_metadata(
            sample_directory_hash, "index.html"
        )

        # Verify the call
        mock_onchfs_client.resolver.get_file_metadata.assert_called_once_with(
            sample_directory_hash, "index.html"
        )

        # Verify the result
        assert result == expected_metadata

    def test_get_file_metadata_not_found(
        self, mock_onchfs_client, sample_directory_hash
    ):
        """Test metadata retrieval when file doesn't exist."""
        mock_onchfs_client.resolver.get_file_metadata.side_effect = FileNotFoundError(
            "File not_found.txt not found in directory"
        )

        with pytest.raises(
            FileNotFoundError, match="File not_found.txt not found in directory"
        ):
            mock_onchfs_client.get_file_metadata(sample_directory_hash, "not_found.txt")

    def test_list_directory_success(
        self, mock_onchfs_client, sample_directory_hash, mock_directory_data
    ):
        """Test successful directory listing."""
        expected_contents = mock_directory_data["directory_contents"]

        result = mock_onchfs_client.list_directory(sample_directory_hash)

        # Verify the call
        mock_onchfs_client.resolver.read_directory.assert_called_once_with(
            sample_directory_hash
        )

        # Verify the result
        assert result == expected_contents

    def test_list_directory_invalid_hash(self, mock_onchfs_client):
        """Test directory listing with invalid hash."""
        invalid_hash = "invalid_hash"
        mock_onchfs_client.resolver.read_directory.side_effect = ValueError(
            f"Invalid directory hash: {invalid_hash}"
        )

        with pytest.raises(ValueError, match="Invalid directory hash"):
            mock_onchfs_client.list_directory(invalid_hash)

    def test_download_directory_resolver_error(
        self, mock_onchfs_client, sample_directory_hash, temp_dir
    ):
        """Test download directory when resolver raises an error."""
        mock_onchfs_client.resolver.extract_directory.side_effect = RuntimeError(
            "Failed to read directory"
        )

        with pytest.raises(RuntimeError, match="Failed to read directory"):
            mock_onchfs_client.download_directory(sample_directory_hash, temp_dir)


class TestOnchfsClientInitialization:
    """Test OnchfsClient initialization and configuration."""

    def test_client_initialization_default(self):
        """Test client initialization with default parameters."""
        client = OnchfsClient()

        assert client.network == Network.MAINNET
        assert client.contract_address is not None
        assert isinstance(client.resolver, OnchfsResolver)

    def test_client_initialization_custom_network(self):
        """Test client initialization with custom network."""
        client = OnchfsClient(network=Network.GHOSTNET)

        assert client.network == Network.GHOSTNET
        assert client.contract_address is not None

    @patch("onchfs.client.OnchfsResolver")
    @patch("onchfs.client.OnchfsUploader")
    @patch("onchfs.client.pytezos")
    def test_client_initialization_custom_contract(
        self, mock_pytezos, mock_uploader, mock_resolver
    ):
        """Test client initialization with custom contract address."""
        custom_address = "KT1CustomContractAddress"
        mock_pytezos_client = Mock()
        mock_pytezos.using.return_value = mock_pytezos_client

        client = OnchfsClient(contract_address=custom_address)

        assert client.contract_address == custom_address

    @patch("onchfs.client.pytezos")
    def test_client_initialization_custom_pytezos(self, mock_pytezos):
        """Test client initialization with custom PyTezos client."""
        mock_client = Mock()
        client = OnchfsClient(pytezos_client=mock_client)

        assert client.pytezos_client == mock_client

    def test_get_network_info(self):
        """Test getting network information."""
        client = OnchfsClient(network=Network.MAINNET)

        info = client.get_network_info()

        assert isinstance(info, dict)
        assert "network" in info
        assert "rpc_url" in info
        assert "contract_address" in info
        assert "client_address" in info
        assert info["network"] == "MAINNET"

    def test_set_network(self):
        """Test switching networks."""
        client = OnchfsClient(network=Network.MAINNET)
        original_address = client.contract_address

        client.set_network(Network.GHOSTNET)

        assert client.network == Network.GHOSTNET
        assert client.contract_address != original_address

    @patch("onchfs.client.OnchfsResolver")
    @patch("onchfs.client.OnchfsUploader")
    def test_set_network_custom_contract(self, mock_uploader, mock_resolver):
        """Test switching networks with custom contract."""
        client = OnchfsClient(network=Network.MAINNET)
        custom_address = "KT1CustomGhostnetContract"

        client.set_network(Network.GHOSTNET, custom_address)

        assert client.network == Network.GHOSTNET
        assert client.contract_address == custom_address
