"""
Peaq Robot SDK - Access Module

Manages access control for robot operations (roles, permissions, assignments).
"""

import hashlib
from typing import Dict, Any, Optional
from substrateinterface.keypair import Keypair
from .wallet import RobotWallet
from .types import RoleReadResult


class RobotAccess:
    """Robot access management (roles, permissions, assignments)."""
    
    def __init__(self, wallet: RobotWallet, keypair: Keypair):
        """
        Initialize robot access manager.
        
        Args:
            wallet (RobotWallet): Wallet instance
            keypair (Keypair): Signing keypair
        """
        self.wallet = wallet
        self.keypair = keypair
        self.address = keypair.ss58_address
    
    def create_role(self, role_name: str, description: str = "") -> str:
        """
        Create a new access role.
        
        Args:
            role_name (str): Role name identifier
            description (str): Human-readable description
            
        Returns:
            str: Transaction hash
            
        Example:
            tx_hash = robot_sdk.access.create_role(
                "ROBOT_OPERATOR", 
                "Advanced Robot Operator"
            )
        """
        role_id = self._format_id(role_name)
        
        return self.wallet.send_transaction(
            module='PeaqRbac',
            function='add_role',
            params={
                'role_id': role_id,
                'name': description or role_name
            },
            keypair=self.keypair
        )
    
    def create_permission(self, permission_name: str, description: str = "") -> str:
        """
        Create a new permission.
        
        Args:
            permission_name (str): Permission name identifier
            description (str): Human-readable description
            
        Returns:
            str: Transaction hash
            
        Example:
            tx_hash = robot_sdk.access.create_permission(
                "ROBOT_CONTROL", 
                "Full Robot Control Access"
            )
        """
        permission_id = self._format_id(permission_name)
        
        return self.wallet.send_transaction(
            module='PeaqRbac',
            function='add_permission',
            params={
                'permission_id': permission_id,
                'name': description or permission_name
            },
            keypair=self.keypair
        )
    
    def grant_role(self, role_name: str, user_identifier: str) -> str:
        """
        Grant role to a user.
        
        Args:
            role_name (str): Role name to grant
            user_identifier (str): User identifier
            
        Returns:
            str: Transaction hash
            
        Example:
            tx_hash = robot_sdk.access.grant_role(
                "ROBOT_OPERATOR", 
                "USER_001"
            )
        """
        role_id = self._format_id(role_name)
        user_id = self._format_id(user_identifier)
        
        return self.wallet.send_transaction(
            module='PeaqRbac',
            function='assign_role_to_user',
            params={
                'role_id': role_id,
                'user_id': user_id
            },
            keypair=self.keypair
        )
    
    def assign_permission_to_role(self, permission_name: str, role_name: str) -> str:
        """
        Assign permission to a role.
        
        Args:
            permission_name (str): Permission to assign
            role_name (str): Role to receive permission
            
        Returns:
            str: Transaction hash
        """
        permission_id = self._format_id(permission_name)
        role_id = self._format_id(role_name)
        
        return self.wallet.send_transaction(
            module='PeaqRbac',
            function='assign_permission_to_role',
            params={
                'permission_id': permission_id,
                'role_id': role_id
            },
            keypair=self.keypair
        )
    
    def revoke_role(self, role_name: str, user_identifier: str) -> str:
        """
        Revoke role from a user.
        
        Args:
            role_name (str): Role name to revoke
            user_identifier (str): User identifier
            
        Returns:
            str: Transaction hash
        """
        role_id = self._format_id(role_name)
        user_id = self._format_id(user_identifier)
        
        return self.wallet.send_transaction(
            module='PeaqRbac',
            function='unassign_role_from_user',
            params={
                'role_id': role_id,
                'user_id': user_id
            },
            keypair=self.keypair
        )
    
    def _format_id(self, identifier: str) -> str:
        """
        Format identifier for access functions.
        
        Args:
            identifier (str): Raw identifier
            
        Returns:
            str: Formatted hex-encoded identifier with 0x prefix
        """
        # Ensure exactly 32 characters, pad with zeros if needed
        padded_id = identifier.ljust(32, '0')[:32]
        
        # Encode as hex with 0x prefix
        return f'0x{padded_id.encode("utf-8").hex()}'
    
    def read_role(self, role_name: str) -> Optional[Dict[str, Any]]:
        """
        Read role information from blockchain.
        
        Args:
            role_name (str): Role name to query
            
        Returns:
            Dict or None: Role information if found
        """
        role_id = self._format_id(role_name)
        
        try:
            api = self.wallet.client
            # Owner-scoped IDs via RPCs; owner is the wallet address
            owner_address = self.address
            
            # Build RPC bytes array for role id (decode 0x-hex to ascii if needed)
            if role_id.startswith('0x'):
                try:
                    ascii_id = bytes.fromhex(role_id[2:]).decode('utf-8')
                except Exception:
                    ascii_id = role_name.ljust(32, '0')[:32]
            else:
                ascii_id = role_id
            role_id_bytes = [ord(c) for c in ascii_id[:32]]
            block_hash = api.get_block_hash(None)
            
            resp = api.rpc_request('peaqrbac_fetchRole', [owner_address, role_id_bytes, block_hash])
            
            if not resp or 'Err' in resp.get('result', {}):
                return {
                    'role_name': role_name,
                    'role_id': role_id,
                    'exists': False,
                    'read_status': 'not_found',
                    'note': 'No role found with this ID'
                }
            
            ok = resp['result']['Ok']
            role_id_str = bytes(ok['id']).decode('utf-8') if isinstance(ok.get('id'), list) else ok.get('id', '')
            role_name_str = bytes(ok['name']).decode('utf-8') if isinstance(ok.get('name'), list) else ok.get('name', '')
            
            role_info = {
                'id': role_id_str,
                'name': role_name_str,
                'enabled': ok.get('enabled', True)
            }
            
            return {
                'role_name': role_name,
                'role_id': role_id,
                'data': role_info,
                'exists': True,
                'read_status': 'success'
            }
                
        except Exception as e:
            print(f"Error reading role: {e}")
            return {
                'role_name': role_name,
                'role_id': role_id,
                'exists': False,
                'read_status': 'error', 
                'error': str(e)
            }
    
    def read_permission(self, permission_name: str) -> Optional[Dict[str, Any]]:
        """
        Read permission information from blockchain.
        
        Args:
            permission_name (str): Permission name to query
            
        Returns:
            Dict or None: Permission information if found
        """
        permission_id = self._format_id(permission_name)
        
        try:
            # Create storage key by hashing the permission_id
            storage_key = hashlib.blake2b(permission_id.encode('utf-8'), digest_size=32).digest()
            
            # Query permission from blockchain
            result = self.wallet.client.query('PeaqRbac', 'PermissionStore', [storage_key])
            
            if result.value:
                return {
                    'permission_name': permission_name,
                    'permission_id': permission_id,
                    'data': result.value,
                    'exists': True
                }
            else:
                return {'exists': False, 'permission_name': permission_name, 'permission_id': permission_id}
                
        except Exception as e:
            print(f"Error reading permission: {e}")
            return None
    
    def read_user_roles(self, user_identifier: str) -> Optional[Dict[str, Any]]:
        """
        Read user role assignments from blockchain.
        
        Args:
            user_identifier (str): User identifier
            
        Returns:
            Dict or None: User role information if found
        """
        user_id = self._format_id(user_identifier)
        
        try:
            # Create storage key by hashing the user_id
            storage_key = hashlib.blake2b(user_id.encode('utf-8'), digest_size=32).digest()
            
            # Query user roles from blockchain
            result = self.wallet.client.query('PeaqRbac', 'UserRoleStore', [storage_key])
            
            if result.value:
                return {
                    'user_identifier': user_identifier,
                    'user_id': user_id,
                    'roles': result.value,
                    'exists': True
                }
            else:
                return {'exists': False, 'user_identifier': user_identifier, 'user_id': user_id}
                
        except Exception as e:
            print(f"Error reading user roles: {e}")
            return None