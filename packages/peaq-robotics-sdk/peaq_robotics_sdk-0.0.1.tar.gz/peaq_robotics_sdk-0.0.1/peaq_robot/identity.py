"""
Peaq Robot SDK - Identity Module

Handles robot identity creation and management using DID documents.
"""

import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Union
from substrateinterface.keypair import Keypair
from . import did_document_format_pb2 as did_proto
from .wallet import RobotWallet
from .types import TxOptions, SubstrateSendResult
from .types import IdentityReadResult, IdentityDecodedDoc
from .utils.encoding import to_hex_utf8, from_prefixed_hex_utf8


class RobotIdentity:
    """Robot identity management using DID documents."""
    
    def __init__(self, wallet: RobotWallet, keypair: Keypair):
        """
        Initialize robot identity manager.
        
        Args:
            wallet (RobotWallet): Wallet instance
            keypair (Keypair): Signing keypair
        """
        self.wallet = wallet
        self.keypair = keypair
        self.address = keypair.ss58_address
    
    def create_identity(
        self, 
        name: str = None,
        did_document: Dict[str, Any] = None,
        **kwargs
    ) -> Union[str, SubstrateSendResult]:
        """
        Create robot identity with fully customizable DID document following Peaq standards.
        
        Args:
            name (str, optional): DID name. Defaults to did:peaq:<address>
            did_document (dict, optional): Complete DID document structure
            **kwargs: Individual field overrides (id, controller, verificationMethods, etc.)
            
        Returns:
            str: Transaction hash
            
        Example:
            # Minimal (uses defaults)
            tx_hash = robot_sdk.id.create_identity()
            
            # With custom name
            tx_hash = robot_sdk.id.create_identity("DID_NAME_001")
            
            # Full customization
            tx_hash = robot_sdk.id.create_identity(
                name="CUSTOM_DID",
                id="did:peaq:custom_address",
                controller="did:peaq:custom_controller",
                services=[{"id": "#ipfs", "type": "peaqStorage", "data": "123"}]
            )
        """
        # Use default name if not provided
        if name is None:
            name = f"did:peaq:{self.address}"
        
        # Create DID document with full customization (filter non-doc kwargs)
        allowed_overrides = {
            'id', 'controller', 'verificationMethods', 'authentications', 'services', 'signature'
        }
        doc_kwargs = {k: v for k, v in kwargs.items() if k in allowed_overrides}

        protobuf_hex, protobuf_hash = self._create_peaq_did_document(
            did_document, **doc_kwargs
        )
        
        # Send transaction with protobuf hex as value (not just hash!)
        return self.wallet.send_transaction(
            module='PeaqDid',
            function='add_attribute',
            params={
                'did_account': self.address,
                'name': name,
                'value': protobuf_hex,  # Full protobuf hex string, not just hash!
                'valid_for': None
            },
            keypair=self.keypair,
            tx_options=kwargs.get('tx_options'),
            on_status=kwargs.get('on_status')
        )
    
    def read_identity(self, did_account: str = None) -> Optional[Dict[str, Any]]:
        """
        Read identity from blockchain.
        
        Args:
            did_account (str, optional): Account to read DID for. Defaults to current address.
            
        Returns:
            Dict or None: DID attribute data if found
        """
        if did_account is None:
            did_account = self.address
        
        did_name = f"did:peaq:{did_account}"
        
        try:
            api = self.wallet.client
            name_encoded = to_hex_utf8(did_name)
            block_hash = api.get_block_hash(None)
            
            resp = api.rpc_request('peaqdid_readAttribute', [did_account, name_encoded, block_hash])
            
            if not resp or resp.get('result') is None:
                return {
                    'did_account': did_account,
                    'name': did_name,
                    'exists': False,
                    'read_status': 'not_found',
                    'note': 'No data found for this account'
                }
            
            result = resp['result']
            raw_name = result.get('name', '')
            raw_value = result.get('value', '')
            validity = result.get('validity', 0)
            created = result.get('created', 0)
            
            decoded_name = from_prefixed_hex_utf8(raw_name) if raw_name else None
            name = decoded_name or did_name
            
            value = ''
            decoded_data = None
            if raw_value:
                outer = from_prefixed_hex_utf8(raw_value)
                if outer:
                    decoded_data = self.decode_identity(outer)
                    value = outer
                else:
                    value = raw_value
            
            return {
                'did_account': did_account,
                'name': name or did_name,
                'value': value,
                'decoded_data': decoded_data,
                'validity': validity,
                'created': created,
                'exists': bool(value),
                'read_status': 'success'
            }
                
        except Exception as e:
            print(f"Error reading identity: {e}")
            return {
                'did_account': did_account,
                'name': did_name,
                'exists': False,
                'read_status': 'error',
                'error': str(e)
            }
    
    def _create_peaq_did_document(
        self, 
        did_document: Dict[str, Any] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        Create DID document following Peaq standards with full customization.
        
        Based on Peaq standards example:
        {
          "id": "did:peaq:0x...",
          "controller": "did:peaq:0x...",
          "verificationMethods": [...],
          "authentications": [...],
          "services": [...],
          "signature": {...}
        }
        
        Returns:
            Tuple[str, str]: (protobuf_hex, protobuf_hash)
        """
        # Create protobuf document
        doc = did_proto.Document()
        
        # Use provided document or build from kwargs with smart defaults
        if did_document:
            document = did_document.copy()
        else:
            document = {}
        
        # Apply individual field overrides
        document.update(kwargs)
        
        # Set required fields with smart defaults
        doc.id = document.get('id', f"did:peaq:{self.address}")
        doc.controller = document.get('controller', f"did:peaq:{self.address}")
        
        # Add verification methods (customizable)
        verification_methods = document.get('verificationMethods', [{
            "id": f"did:peaq:{self.address}#keys-1",
            "type": "Sr25519VerificationKey2020",
            "controller": f"did:peaq:{self.address}",
            "publicKeyMultibase": self.keypair.public_key.hex()
        }])
        
        for vm_data in verification_methods:
            vm = doc.verificationMethod.add()
            vm.id = vm_data.get('id', f"did:peaq:{self.address}#keys-1")
            vm.type = vm_data.get('type', 'Sr25519VerificationKey2020')
            vm.controller = vm_data.get('controller', f"did:peaq:{self.address}")
            vm.publicKeyMultibase = vm_data.get('publicKeyMultibase', self.keypair.public_key.hex())
        
        # Add authentications (customizable)
        authentications = document.get('authentications', [f"did:peaq:{self.address}#keys-1"])
        for auth in authentications:
            doc.authentication.append(auth)
        
        # Add services (customizable, empty by default)
        services = document.get('services', [])
        for svc_data in services:
            svc = doc.service.add()
            svc.id = svc_data.get('id', '#default')
            svc.type = svc_data.get('type', 'DefaultService')
            if svc_data.get('serviceEndpoint'):
                svc.serviceEndpoint = svc_data['serviceEndpoint']
            if svc_data.get('data'):
                svc.data = svc_data['data']
        
        # Add signature (customizable)
        signature_data = document.get('signature', {
            'type': 'Sr25519VerificationKey2020',
            'issuer': self.address,
            'hash': hashlib.sha256(json.dumps(document, sort_keys=True).encode()).hexdigest()
        })
        
        if signature_data:
            sig = did_proto.Signature()
            sig.type = signature_data.get('type', 'Sr25519VerificationKey2020')
            sig.issuer = signature_data.get('issuer', self.address)
            sig.hash = signature_data.get('hash', 'default_hash')
            doc.signature.CopyFrom(sig)
        
        # Serialize and hash
        protobuf_bytes = doc.SerializeToString()
        protobuf_hex = protobuf_bytes.hex()
        protobuf_hash = hashlib.sha256(protobuf_bytes).hexdigest()
        
        return protobuf_hex, protobuf_hash
    
    def _create_minimal_did_document(self) -> Tuple[str, str]:
        """
        Create minimal DID document to avoid protobuf size issues.
        
        Returns:
            Tuple[str, str]: (protobuf_hex, protobuf_hash)
        """
        # Create absolute minimal protobuf document
        doc = did_proto.Document()
        
        # Only required fields
        doc.id = f"did:peaq:{self.address}"
        doc.controller = f"did:peaq:{self.address}"
        
        # Minimal verification method
        vm = doc.verificationMethod.add()
        vm.id = f"did:peaq:{self.address}#key"
        vm.type = 'Sr25519VerificationKey2020'
        vm.controller = f"did:peaq:{self.address}"
        vm.publicKeyMultibase = self.keypair.public_key.hex()[:32]  # Truncate key
        
        # Minimal authentication
        doc.authentication.append(f"did:peaq:{self.address}#key")
        
        # Serialize and hash
        protobuf_bytes = doc.SerializeToString()
        protobuf_hex = protobuf_bytes.hex()
        protobuf_hash = hashlib.sha256(protobuf_bytes).hexdigest()
        
        return protobuf_hex, protobuf_hash
    
    def decode_identity(self, protobuf_hex: str) -> Optional[Dict[str, Any]]:
        """
        Decode DID document from protobuf hex.
        
        Args:
            protobuf_hex (str): Hex-encoded protobuf document
            
        Returns:
            Dict[str, Any]: Parsed document or None if parsing fails
        """
        try:
            protobuf_bytes = bytes.fromhex(protobuf_hex)
            doc = did_proto.Document()
            doc.ParseFromString(protobuf_bytes)
            
            return {
                'id': doc.id,
                'controller': doc.controller,
                'verificationMethods': [{
                    'id': vm.id,
                    'type': vm.type,
                    'controller': vm.controller,
                    'publicKeyMultibase': vm.publicKeyMultibase
                } for vm in doc.verificationMethod],
                'authentications': list(doc.authentication),
                'services': [{
                    'id': svc.id,
                    'type': svc.type,
                    'serviceEndpoint': getattr(svc, 'serviceEndpoint', ''),
                    'data': getattr(svc, 'data', '')
                } for svc in doc.service],
                'signature': {
                    'type': doc.signature.type,
                    'issuer': doc.signature.issuer,
                    'hash': doc.signature.hash
                } if doc.HasField('signature') else None
            }
        except Exception:
            return None