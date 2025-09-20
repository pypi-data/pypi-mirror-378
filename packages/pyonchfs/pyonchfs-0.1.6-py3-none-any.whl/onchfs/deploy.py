"""OnchFS deployment module.

This module provides functionality to deploy OnchFS contracts to Tezos networks.
"""

import os
from pathlib import Path
from typing import Optional, Tuple

from pytezos import pytezos
from pytezos.crypto.key import Key
from pytezos.contract.interface import ContractInterface

from .config import Network


def get_wallet_from_env() -> Key:
    """Get wallet from environment variable.

    Returns:
        Key: Tezos wallet key.

    Raises:
        ValueError: If TZ_SK environment variable is not set.
    """
    secret_key = os.getenv("TZ_SK")
    if not secret_key:
        raise ValueError(
            "TZ_SK environment variable not set. "
            "Please set it to your Tezos secret key."
        )
    return Key.from_encoded_key(secret_key)


def extract_first_originated_contract(opg_result: dict) -> str:
    """Extract the first originated contract address from operation result.

    Args:
        opg_result: Operation group result from PyTezos.

    Returns:
        str: Contract address.
    """
    return opg_result["contents"][0]["metadata"]["operation_result"][
        "originated_contracts"
    ][0]


def get_contract_path(contract_name: str) -> Path:
    """Get the path to a contract file.

    Args:
        contract_name: Name of the contract file (e.g., 'content_store.tz').

    Returns:
        Path: Path to the contract file.

    Raises:
        FileNotFoundError: If contract file is not found.
    """
    # Get the directory where this module is located
    module_dir = Path(__file__).parent
    contract_path = module_dir / contract_name

    if not contract_path.exists():
        raise FileNotFoundError(f"Contract file not found: {contract_path}")

    return contract_path


def deploy_onchfs_environment(
    network: Network, wallet: Optional[Key] = None, quiet: bool = False
) -> Tuple[str, str]:
    """Deploy a complete OnchFS environment (content store + onchfs contracts).

    Args:
        network: Target network for deployment.
        wallet: Tezos wallet key. If None, will get from TZ_SK environment variable.
        quiet: If True, suppress output except for final addresses.

    Returns:
        Tuple[str, str]: (content_store_address, onchfs_address)

    Raises:
        ValueError: If wallet is not provided and TZ_SK is not set.
        FileNotFoundError: If contract files are not found.
    """
    if wallet is None:
        wallet = get_wallet_from_env()

    # Initialize PyTezos client
    pt = pytezos.using(key=wallet.secret_key(), shell=network.value)

    if not quiet:
        print(f"Deploying OnchFS environment to {network.name.lower()}...")
        print(f"Using wallet: {wallet.public_key_hash()}")

    # Deploy content store contract
    if not quiet:
        print("Deploying content store contract...")

    content_store_path = get_contract_path("content_store.tz")
    content_store = ContractInterface.from_file(str(content_store_path))
    operation_group = pt.origination(script=content_store.script()).send(
        min_confirmations=1
    )
    content_store_address = extract_first_originated_contract(
        operation_group.opg_result
    )

    if not quiet:
        print(f"Content store deployed at: {content_store_address}")

    # Deploy onchfs contract
    if not quiet:
        print("Deploying onchfs contract...")

    onchfs_path = get_contract_path("onchfs.tz")
    onchfs = ContractInterface.from_file(str(onchfs_path))
    initial_storage = {"content_store": content_store_address, "inodes": {}}
    operation_group = pt.origination(
        script=onchfs.script(initial_storage=initial_storage)
    ).send(min_confirmations=1)
    onchfs_address = extract_first_originated_contract(operation_group.opg_result)

    if not quiet:
        print(f"OnchFS contract deployed at: {onchfs_address}")
        print("Deployment completed successfully!")

    return content_store_address, onchfs_address


def deploy_content_store_only(
    network: Network, wallet: Optional[Key] = None, quiet: bool = False
) -> str:
    """Deploy only the content store contract.

    Args:
        network: Target network for deployment.
        wallet: Tezos wallet key. If None, will get from TZ_SK environment variable.
        quiet: If True, suppress output except for final address.

    Returns:
        str: Content store contract address.

    Raises:
        ValueError: If wallet is not provided and TZ_SK is not set.
        FileNotFoundError: If contract file is not found.
    """
    if wallet is None:
        wallet = get_wallet_from_env()

    # Initialize PyTezos client
    pt = pytezos.using(key=wallet.secret_key(), shell=network.value)

    if not quiet:
        print(f"Deploying content store to {network.name.lower()}...")
        print(f"Using wallet: {wallet.public_key_hash()}")

    # Deploy content store contract
    content_store_path = get_contract_path("content_store.tz")
    content_store = ContractInterface.from_file(str(content_store_path))
    operation_group = pt.origination(script=content_store.script()).send(
        min_confirmations=1
    )
    content_store_address = extract_first_originated_contract(
        operation_group.opg_result
    )

    if not quiet:
        print(f"Content store deployed at: {content_store_address}")

    return content_store_address


def deploy_onchfs_only(
    network: Network,
    content_store_address: str,
    wallet: Optional[Key] = None,
    quiet: bool = False,
) -> str:
    """Deploy only the onchfs contract with an existing content store.

    Args:
        network: Target network for deployment.
        content_store_address: Address of existing content store contract.
        wallet: Tezos wallet key. If None, will get from TZ_SK environment variable.
        quiet: If True, suppress output except for final address.

    Returns:
        str: OnchFS contract address.

    Raises:
        ValueError: If wallet is not provided and TZ_SK is not set.
        FileNotFoundError: If contract file is not found.
    """
    if wallet is None:
        wallet = get_wallet_from_env()

    # Initialize PyTezos client
    pt = pytezos.using(key=wallet.secret_key(), shell=network.value)

    if not quiet:
        print(f"Deploying onchfs contract to {network.name.lower()}...")
        print(f"Using wallet: {wallet.public_key_hash()}")
        print(f"Using content store: {content_store_address}")

    # Deploy onchfs contract
    onchfs_path = get_contract_path("onchfs.tz")
    onchfs = ContractInterface.from_file(str(onchfs_path))
    initial_storage = {"content_store": content_store_address, "inodes": {}}
    operation_group = pt.origination(
        script=onchfs.script(initial_storage=initial_storage)
    ).send(min_confirmations=1)
    onchfs_address = extract_first_originated_contract(operation_group.opg_result)

    if not quiet:
        print(f"OnchFS contract deployed at: {onchfs_address}")

    return onchfs_address
