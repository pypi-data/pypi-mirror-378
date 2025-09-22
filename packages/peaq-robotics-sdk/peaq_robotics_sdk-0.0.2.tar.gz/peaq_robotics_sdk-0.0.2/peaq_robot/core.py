"""
Peaq Robot SDK - Core Module

Main entry point for the Peaq Robot SDK providing standardized access 
to blockchain functions through clean, intuitive interfaces.
"""

from substrateinterface.keypair import Keypair
from .wallet import RobotWallet
from .identity import RobotIdentity
from .storage import RobotStorage
from .access import RobotAccess
from .utils.config import get_default_keystore_path, DEFAULT_NETWORK
from .utils.keystore import save_keystore, load_keystore


class PeaqRobot:
    """
    Main Peaq Robot SDK class providing access to all blockchain functions.
    
    Usage:
        # Using default test wallet
        robot_sdk = PeaqRobot()
        
        # Using custom mnemonic
        robot_sdk = PeaqRobot(mnemonic="your mnemonic")
        
        # Creating new wallet
        robot_sdk = PeaqRobot.create_wallet()
        
        # Identity management
        tx_hash = robot_sdk.id.create_identity(name, config)
        
        # Data storage
        tx_hash = robot_sdk.store.add_data(type, data)
        
        # Additional features will be available in future versions
    """
    
    def __init__(self, mnemonic: str = None, private_key: str = None, network: str = None, keystore_path: str = None):
        """
        Initialize Peaq Robot SDK.
        
        Args:
            mnemonic (str, optional): Wallet mnemonic.
            private_key (str, optional): Private key hex string.
            network (str, optional): Blockchain network endpoint.
            keystore_path (str, optional): Path to keystore file. Defaults to ~/.peaq_robot/wallet.json
        """
        keystore_path = keystore_path or get_default_keystore_path()
        
        # Load or create keypair
        if mnemonic:
            self.keypair = Keypair.create_from_mnemonic(mnemonic)
        elif private_key:
            self.keypair = Keypair.create_from_private_key(private_key)
        else:
            # Try keystore; if missing, generate new and persist
            try:
                secret_type, payload = load_keystore(keystore_path)
                if secret_type == "mnemonic":
                    self.keypair = Keypair.create_from_mnemonic(payload)
                else:
                    self.keypair = Keypair.create_from_private_key(payload)
            except Exception:
                generated = Keypair.create_from_mnemonic(Keypair.generate_mnemonic())
                self.keypair = generated
                save_keystore(keystore_path, generated.mnemonic, "mnemonic")

        # Create wallet connection
        self.wallet = RobotWallet(network)
        self.network = network
        
        # Initialize modules
        self.id = RobotIdentity(self.wallet, self.keypair)
        self.store = RobotStorage(self.wallet, self.keypair)
        self.access = RobotAccess(self.wallet, self.keypair)
    
    @classmethod
    def create_wallet(cls, network: str = None, keystore_path: str = None):
        """
        Create a new robot wallet with generated mnemonic.
        
        Args:
            network (str): Blockchain network endpoint
            
        Returns:
            PeaqRobot: SDK instance with new wallet persisted to keystore
        """
        from substrateinterface.keypair import Keypair
        keystore_path = keystore_path or get_default_keystore_path()

        # Generate new keypair and persist mnemonic to keystore
        keypair = Keypair.create_from_mnemonic(Keypair.generate_mnemonic())
        mnemonic = keypair.mnemonic
        save_keystore(keystore_path, mnemonic, "mnemonic")

        print(f"🔑 New Robot Wallet Created:")
        print(f"   Address: {keypair.ss58_address}")
        print(f"   Mnemonic stored in keystore: {keystore_path}")
        print(f"   ⚠️  Protect your keystore password (PEAQ_ROBOT_KEY_PASSWORD)!")

        return cls(mnemonic=mnemonic, network=network, keystore_path=keystore_path)
    
    @classmethod  
    def from_private_key(cls, private_key: str, network: str = DEFAULT_NETWORK):
        """
        Create SDK instance from private key.
        
        Args:
            private_key (str): Private key hex string
            network (str): Blockchain network endpoint
            
        Returns:
            PeaqRobot: SDK instance
        """
        keypair = Keypair.create_from_private_key(private_key)
        return cls(mnemonic=keypair.mnemonic, network=network)
    
    @property
    def address(self) -> str:
        """Get wallet address."""
        return self.keypair.ss58_address
    
    @property
    def balance(self) -> float:
        """Get wallet balance in AGUNG."""
        return self.wallet.get_balance(self.keypair.ss58_address)
    
    def __repr__(self):
        return f"PeaqRobot(address='{self.address}', balance={self.balance:.6f} AGUNG)"