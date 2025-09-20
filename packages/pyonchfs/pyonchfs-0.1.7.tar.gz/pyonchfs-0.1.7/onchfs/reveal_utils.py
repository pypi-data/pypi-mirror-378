"""Utility functions for handling Tezos account reveal operations.

This module provides functionality to check if an account is revealed
and perform the reveal operation if necessary before sending transactions.
"""

from typing import Any, Set


# Cache to store revealed account addresses to avoid repeated checks
_revealed_accounts: Set[str] = set()


def ensure_account_revealed(pt: Any, quiet: bool = False) -> None:
    """Ensure the account is revealed before performing operations.
    
    This function checks if the account associated with the PyTezos client
    is revealed on the blockchain. If not, it performs a reveal operation.
    Uses caching to avoid repeated checks for the same account.
    
    Args:
        pt: PyTezos client instance
        quiet: If True, suppress output messages
        
    Raises:
        Exception: If the reveal operation fails
    """
    try:
        # Get the account address for caching
        account_address = pt.key.public_key_hash()
        
        # If we've already revealed this account, skip the check
        if account_address in _revealed_accounts:
            return
        
        # Check account status
        account_info = pt.account()
        
        # If account is not revealed, perform reveal operation
        if not account_info.get('revealed', False):
            if not quiet:
                print("Account not revealed, performing reveal operation...")
            reveal_op = pt.reveal().send(min_confirmations=1)
            if not quiet:
                print(f"Account revealed successfully. Operation hash: {reveal_op.hash()}")
        
        # Cache this account as revealed
        _revealed_accounts.add(account_address)
        
    except Exception as e:
        if not quiet:
            print(f"Error checking/revealing account: {e}")
        raise
