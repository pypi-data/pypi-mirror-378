"""
Peaq Robot SDK - Storage Module

Handles robot data storage on the blockchain.
"""

import json
import hashlib
from typing import Dict, Any, Union, Optional
from substrateinterface.keypair import Keypair
from .wallet import RobotWallet
from .types import TxOptions, SubstrateSendResult
from .types import StorageReadResult
from .utils.validation import ensure_max_length
from .utils.encoding import to_hex_utf8, from_prefixed_hex_utf8


class RobotStorage:
    """Robot data storage management."""
    
    def __init__(self, wallet: RobotWallet, keypair: Keypair):
        """
        Initialize robot storage manager.
        
        Args:
            wallet (RobotWallet): Wallet instance
            keypair (Keypair): Signing keypair
        """
        self.wallet = wallet
        self.keypair = keypair
        self.address = keypair.ss58_address
    
    def add_data(self, data_type: str, data: Union[Dict[str, Any], str], *, tx_options: TxOptions = None, on_status=None) -> Union[str, SubstrateSendResult]:
        """
        Store robot data on blockchain.
        
        Args:
            data_type (str): Type identifier for the data (max 64 chars)
            data (dict or str): Data to store (max 256 chars when serialized)
            
        Returns:
            str: Transaction hash
            
        Raises:
            ValueError: If data exceeds size limits
            
        Example:
            tx_hash = robot_sdk.store.add_data(
                "TELEMETRY_001", 
                {"battery": 87.3, "status": "operational"}
            )
        """
        # Validate data_type length (no logic change; centralized helper)
        ensure_max_length(data_type, 64, "Data type")
        
        # Convert data to string if needed
        if isinstance(data, dict):
            data_str = json.dumps(data, separators=(',', ':'))
        else:
            data_str = str(data)
        
        # Validate data length
        if len(data_str) > 256:
            raise ValueError(f"Data size {len(data_str)} exceeds 256 character limit")
        
        # Send transaction
        return self.wallet.send_transaction(
            module='PeaqStorage',
            function='add_item',
            params={
                'item_type': data_type,
                'item': data_str
            },
            keypair=self.keypair,
            tx_options=tx_options,
            on_status=on_status,
        )
    
    def add_telemetry(self, robot_id: str, telemetry: Dict[str, Any]) -> str:
        """
        Store robot telemetry data.
        
        Args:
            robot_id (str): Robot identifier
            telemetry (dict): Telemetry data
            
        Returns:
            str: Transaction hash
        """
        # Create compact telemetry format to fit 256 char limit
        compact_telemetry = self._compact_telemetry(telemetry)
        data_type = f"TELEMETRY_{robot_id}"
        
        return self.add_data(data_type, compact_telemetry)
    
    def add_configuration(self, robot_id: str, config: Dict[str, Any]) -> str:
        """
        Store robot configuration data.
        
        Args:
            robot_id (str): Robot identifier
            config (dict): Configuration data
            
        Returns:
            str: Transaction hash
        """
        data_type = f"CONFIG_{robot_id}"
        return self.add_data(data_type, config)
    
    def _compact_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create compact telemetry format for blockchain storage.
        
        Args:
            telemetry (dict): Original telemetry data
            
        Returns:
            dict: Compacted telemetry data
        """
        compact = {}
        
        # Map long keys to short ones
        key_mapping = {
            'timestamp': 'ts',
            'battery_level': 'bat',
            'location': 'loc',
            'sensors': 'sen',
            'status': 'stat',
            'temperature': 'temp',
            'voltage': 'v',
            'level': 'lv',
            'position': 'pos',
            'orientation': 'ori'
        }
        
        def compact_dict(data):
            if isinstance(data, dict):
                result = {}
                for key, value in data.items():
                    new_key = key_mapping.get(key, key[:4])  # Limit to 4 chars
                    result[new_key] = compact_dict(value)
                return result
            elif isinstance(data, list):
                return [compact_dict(item) for item in data]
            else:
                return data
        
        return compact_dict(telemetry)
    
    def read_data(self, data_type: str, account: str = None) -> Optional[Dict[str, Any]]:
        """
        Read stored data from blockchain.
        
        Args:
            data_type (str): Data type identifier
            account (str, optional): Account to read from. Defaults to current address.
            
        Returns:
            Dict or None: Stored data if found
        """
        if account is None:
            account = self.address
        
        try:
            api = self.wallet.client
            item_type_hex = to_hex_utf8(data_type)
            block_hash = api.get_block_hash(None)
            
            resp = api.rpc_request('peaqstorage_readAttribute', [account, item_type_hex, block_hash])
            
            if not resp or resp.get('result') is None:
                return {
                    'account': account,
                    'data_type': data_type,
                    'exists': False,
                    'read_status': 'not_found',
                    'note': 'No data found for this key'
                }
            
            raw_item = resp['result'].get('item', None)
            if raw_item is None:
                return {
                    'account': account,
                    'data_type': data_type,
                    'exists': False,
                    'read_status': 'not_found',
                    'note': 'No data found for this key'
                }
            
            # raw_item is hex-prefixed bytes, decode to utf-8 string
            decoded = from_prefixed_hex_utf8(raw_item)
            stored_data = decoded if decoded is not None else raw_item
            
            # Try to parse JSON
            try:
                parsed_data = json.loads(stored_data)
            except json.JSONDecodeError:
                parsed_data = stored_data
            
            return {
                'account': account,
                'data_type': data_type,
                'data': parsed_data,
                'raw': stored_data,
                'exists': True,
                'read_status': 'success'
            }
                
        except Exception as e:
            print(f"Error reading storage: {e}")
            return {
                'account': account,
                'data_type': data_type,
                'exists': False,
                'read_status': 'error',
                'error': str(e)
            }