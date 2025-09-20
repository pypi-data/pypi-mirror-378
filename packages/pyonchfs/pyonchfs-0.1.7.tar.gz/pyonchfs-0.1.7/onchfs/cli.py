#!/usr/bin/env python3
"""OnchFS Command Line Interface.

A command-line tool for uploading and downloading files using OnchFS.
"""

import argparse
import os
import sys
from pathlib import Path

from pytezos import pytezos

from .config import Network
from .deploy import (
    deploy_onchfs_environment,
    deploy_content_store_only,
    deploy_onchfs_only,
)
from .resolver import OnchfsResolver
from .types import OnchfsPrepareOptions, IFile
from .uploader import OnchfsUploader


def get_network_from_string(network_str: str) -> Network:
    """Convert string to Network enum.

    Args:
        network_str: Network name as string.

    Returns:
        Network enum value.

    Raises:
        ValueError: If network string is invalid.
    """
    network_map = {
        "mainnet": Network.MAINNET,
        "ghostnet": Network.GHOSTNET,
        "shadownet": Network.SHADOWNET,
        "localnet": Network.LOCALNET,
    }

    network_lower = network_str.lower()
    if network_lower not in network_map:
        valid_options = ", ".join(network_map.keys())
        raise ValueError(
            f"Invalid network: {network_str}. Valid options: {valid_options}"
        )

    return network_map[network_lower]


def get_secret_key() -> str:
    """Get Tezos secret key from environment variable.

    Returns:
        Secret key string.

    Raises:
        ValueError: If TZ_SK environment variable is not set.
    """
    secret_key = os.getenv("TZ_SK")
    if not secret_key:
        raise ValueError(
            "TZ_SK environment variable not set. "
            "Please set it to your Tezos secret key."
        )
    return secret_key


def upload_command(args) -> None:
    """Handle upload command.

    Args:
        args: Parsed command line arguments.
    """
    try:
        # Get secret key
        secret_key = get_secret_key()

        # Get network
        network = get_network_from_string(args.network)

        # Initialize PyTezos client
        pytezos_client = pytezos.using(key=secret_key, shell=network.value)

        # Initialize uploader
        uploader = OnchfsUploader(pytezos_client, network)

        # Check if path exists
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path {args.path!r} does not exist", file=sys.stderr)
            sys.exit(1)

        # Prepare options
        options = OnchfsPrepareOptions(
            compress=args.compress, chunk_size=args.chunk_size
        )

        file_type = "directory" if path.is_dir() else "file"
        if not args.quiet:
            print(f"Preparing {file_type}: {path}")

        # Prepare for upload
        if path.is_dir():
            directory_inode = uploader.prepare_directory(str(path), options)
            is_single_file = False
        else:
            # For single file, prepare it directly as a file
            file_inode = uploader.prepare_file(str(path), options)
            is_single_file = True

        if is_single_file:
            # Handle single file upload
            from .utils import bytes_to_hex

            file_hash = bytes_to_hex(file_inode.cid)
            if not args.quiet:
                print(f"File hash: {file_hash}")

                # Estimate cost for single file
                total_chunks = len(file_inode.chunks)
                total_size = sum(len(chunk.bytes) for chunk in file_inode.chunks)
                print("Estimated cost:")
                print(f"  Files: 1")
                print(f"  Chunks: {total_chunks}")
                print(f"  Total size: {total_size} bytes")
                print(f"  Estimated gas: {total_chunks * 1000}")
                storage_cost = total_size * 0.001
                print(f"  Estimated storage cost: {storage_cost:.6f} XTZ")

            # Ask for confirmation unless --yes flag is used
            if not args.yes and not args.quiet:
                response = input("\nProceed with upload? (y/N): ")
                if response.lower() not in ["y", "yes"]:
                    print("Upload cancelled.")
                    return

            # Upload single file
            if not args.quiet:
                print("\nStarting upload...")
            result = uploader.upload_file(file_inode, quiet=args.quiet)

            if args.quiet:
                # In quiet mode, only print the onchfs URL
                print(f"onchfs://{result.file_hash}")
            else:
                print("\nUpload completed!")
                print(f"File hash: {result.file_hash}")
                print(f"Operation hash: {result.operation_hash}")
                print(f"Total size: {result.total_size} bytes")
                print(f"Compressed size: {result.compressed_size} bytes")
                onchfs_url = f"onchfs://{result.file_hash}"
                print(f"\nYour file is now accessible at: {onchfs_url}")
        else:
            # Handle directory upload
            directory_hash = uploader.get_directory_hash(directory_inode)
            if not args.quiet:
                print(f"Directory hash: {directory_hash}")

                # Estimate cost
                cost_estimate = uploader.estimate_cost(directory_inode)
                print("Estimated cost:")
                print(f"  Files: {cost_estimate['file_count']}")
                print(f"  Chunks: {cost_estimate['total_chunks']}")
                print(f"  Total size: {cost_estimate['total_size']} bytes")
                print(f"  Estimated gas: {cost_estimate['estimated_gas']}")
                storage_cost = cost_estimate["estimated_storage_cost"]
                print(f"  Estimated storage cost: {storage_cost:.6f} XTZ")

            # Ask for confirmation unless --yes flag is used
            if not args.yes and not args.quiet:
                response = input("\nProceed with upload? (y/N): ")
                if response.lower() not in ["y", "yes"]:
                    print("Upload cancelled.")
                    return

            # Upload directory
            if not args.quiet:
                print("\nStarting upload...")
            result = uploader.upload_directory(directory_inode, quiet=args.quiet)

            if args.quiet:
                # In quiet mode, only print the onchfs URL
                print(f"onchfs://{result.directory_hash}")
            else:
                print("\nUpload completed!")
                print(f"Directory hash: {result.directory_hash}")
                print(f"Operation hash: {result.operation_hash}")
                print(f"Total size: {result.total_size} bytes")
                print(f"Compressed size: {result.compressed_size} bytes")
                onchfs_url = f"onchfs://{result.directory_hash}"
                print(f"\nYour files are now accessible at: {onchfs_url}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def download_command(args) -> None:
    """Handle download command.

    Args:
        args: Parsed command line arguments.
    """
    try:
        # Get network
        network = get_network_from_string(args.network)

        # Initialize resolver
        resolver = OnchfsResolver(network)

        # Parse hash from URL or use directly
        hash_value = args.hash
        if hash_value.startswith("onchfs://"):
            hash_value = hash_value[9:]  # Remove 'onchfs://' prefix

        if not args.quiet:
            print(f"Downloading from hash: {hash_value}")

        # Try to download as a file first
        try:
            if not args.quiet:
                print("Attempting to download as file...")
            # Try to read as a file directly using the hash
            file_inode = resolver.read_file(hash_value)

            # If we get here, it's a single file - extract the content
            file_content = file_inode["content"]

            # Check if file is gzip encoded by decoding metadata
            from hpack import Decoder

            decoder = Decoder()
            hpack_meta = decoder.decode(file_inode["metadata"])

            # Check if file is gzip encoded
            is_gzipped = any(
                header[0] == "content-encoding" and header[1] == "gzip"
                for header in hpack_meta
            )

            if is_gzipped:
                import gzip

                file_content = gzip.decompress(file_content)

            # Write the file content directly
            output_path = Path(args.output)
            with open(output_path, "wb") as f:
                f.write(file_content)

            if not args.quiet:
                print(f"File downloaded to: {output_path}")
            return

        except Exception:
            if not args.quiet:
                print("Not a single file, trying as directory...")

            # Try as directory
            try:
                # First check if directory exists without creating anything
                directory_contents = resolver.read_directory(hash_value)

                # If we get here, it's a valid directory - now create output and extract
                output_path = Path(args.output)
                resolver.extract_directory(hash_value, str(output_path), verbose=not args.quiet)

                if not args.quiet:
                    print(f"Directory downloaded to: {output_path}")
                return

            except Exception:
                print(
                    f"Error: Hash {hash_value} is neither a valid file nor directory",
                    file=sys.stderr,
                )
                sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def deploy_command(args) -> None:
    """Handle deploy command.

    Args:
        args: Parsed command line arguments.
    """
    try:
        # Get network
        network = get_network_from_string(args.network)

        if args.type == "environment":
            # Deploy complete environment (content store + onchfs)
            content_store_address, onchfs_address = deploy_onchfs_environment(
                network=network, quiet=args.quiet
            )

            if args.quiet:
                # In quiet mode, only output the onchfs address
                print(onchfs_address)
            else:
                print(f"\nDeployment Summary:")
                print(f"Content Store: {content_store_address}")
                print(f"OnchFS Contract: {onchfs_address}")

        elif args.type == "content-store":
            # Deploy only content store
            content_store_address = deploy_content_store_only(
                network=network, quiet=args.quiet
            )

            if args.quiet:
                print(content_store_address)
            else:
                print(f"\nContent Store deployed: {content_store_address}")

        elif args.type == "onchfs":
            # Deploy only onchfs contract
            if not args.content_store:
                print(
                    "Error: --content-store address is required when deploying onchfs only",
                    file=sys.stderr,
                )
                sys.exit(1)

            onchfs_address = deploy_onchfs_only(
                network=network,
                content_store_address=args.content_store,
                quiet=args.quiet,
            )

            if args.quiet:
                print(onchfs_address)
            else:
                print(f"\nOnchFS Contract deployed: {onchfs_address}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OnchFS CLI - Upload and download files using OnchFS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload a file
  onchfs upload myfile.txt

  # Upload a directory with compression
  onchfs upload ./my-website --compress

  # Upload to mainnet
  onchfs upload ./docs --network mainnet

  # Upload with quiet mode (only outputs onchfs:// URL)
  onchfs upload myfile.txt --yes --quiet

  # Download files
  onchfs download abc123def456... ./downloaded

  # Download from onchfs URL
  onchfs download onchfs://abc123def456... ./downloaded

  # Download with quiet mode (no output on success)
  onchfs download abc123def456... ./downloaded --quiet

  # Deploy complete OnchFS environment (content store + onchfs contracts)
  onchfs deploy environment

  # Deploy to mainnet
  onchfs deploy environment --network mainnet

  # Deploy with quiet mode (only outputs onchfs contract address)
  onchfs deploy environment --quiet

  # Deploy only content store
  onchfs deploy content-store

  # Deploy only onchfs contract with existing content store
  onchfs deploy onchfs --content-store KT1ABC123...

Environment Variables:
  TZ_SK    Tezos secret key (required for uploads and deployments)
        """,
    )

    # Global options
    parser.add_argument(
        "--network",
        choices=["mainnet", "ghostnet", "shadownet", "localnet"],
        default="ghostnet",
        help="Tezos network to use (default: ghostnet)",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Upload command
    upload_parser = subparsers.add_parser(
        "upload", help="Upload files or directories to OnchFS"
    )
    upload_parser.add_argument("path", help="Path to file or directory to upload")
    upload_parser.add_argument(
        "--compress", action="store_true", help="Enable compression for uploaded files"
    )
    upload_parser.add_argument(
        "--chunk-size",
        type=int,
        default=16384,
        help="Chunk size in bytes (default: 16384)",
    )
    upload_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )
    upload_parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet mode - only output the final onchfs:// URL",
    )

    # Download command
    download_parser = subparsers.add_parser(
        "download", help="Download files from OnchFS"
    )
    download_parser.add_argument(
        "hash", help="Directory hash or onchfs:// URL to download"
    )
    download_parser.add_argument("output", help="Output directory path")
    download_parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet mode - no output on success",
    )

    # Deploy command
    deploy_parser = subparsers.add_parser(
        "deploy", help="Deploy OnchFS contracts to Tezos network"
    )
    deploy_parser.add_argument(
        "type",
        choices=["environment", "content-store", "onchfs"],
        help="Type of deployment: 'environment' (both contracts), 'content-store' (only content store), or 'onchfs' (only onchfs contract)",
    )
    deploy_parser.add_argument(
        "--content-store",
        help="Content store contract address (required when deploying 'onchfs' type)",
    )
    deploy_parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet mode - only output the contract address(es)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == "upload":
        upload_command(args)
    elif args.command == "download":
        download_command(args)
    elif args.command == "deploy":
        deploy_command(args)


if __name__ == "__main__":
    main()
