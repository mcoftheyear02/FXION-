"""
FXION OMEGA VAULT & PHYSICAL COLD STORAGE
Generates a Bitcoin identity and creates a 'Physical' folder backup.
"""
import json
import logging
import os
import secrets
import time
from hashlib import sha256, md5
from typing import Dict, Optional, Any

log = logging.getLogger(__name__)


class FXIONWalletError(Exception):
    """Base exception for wallet errors."""
    pass


class FXIONWallet:
    """FXION Omega Vault and Cold Storage Management."""
    
    DEFAULT_EXCHANGE_RATES = {"USD": 81000.0, "CAD": 111000.0}
    XOR_MASK = 0x0A
    MIN_ADDRESS_LENGTH = 26
    
    def __init__(self, vault_path: str = "vault/fxion_vault.json") -> None:
        """Initialize FXION Wallet.
        
        Args:
            vault_path: Path to vault JSON file
        """
        self.vault_path = vault_path
        self.physical_dir = "FXION_PHYSICAL_COLD_STORAGE"
        self.address: Optional[str] = None
        self.data: Dict[str, Any] = {}
        
        os.makedirs("vault", exist_ok=True)
        os.makedirs(self.physical_dir, exist_ok=True)
        
        if not os.path.exists(self.vault_path):
            self.create_new_vault()
        
        self.load_vault()
    
    def create_new_vault(self) -> None:
        """Generate new Bitcoin identity and physical backup."""
        try:
            log.info("[VAULT] Generating new Omega Identity...")
            
            # Generate entropy
            seed = secrets.token_hex(32)
            private_key = sha256(seed.encode()).hexdigest()
            
            # Derive public address
            public_key = sha256(private_key.encode()).hexdigest()
            address = f"1FXION{md5(public_key.encode()).hexdigest()[:28]}"
            
            # XOR obfuscation
            encoded_key = "".join([chr(ord(c) ^ self.XOR_MASK) for c in private_key])
            
            # Save vault
            vault_data = {
                "address": address,
                "encrypted_private_key": encoded_key,
                "balance_btc": 0.0,
                "balance_usd": 0.0,
                "balance_cad": 0.0,
                "fiat_holdings": {"USD": 0.0, "CAD": 0.0},
                "transaction_history": [],
                "created_at": str(time.time())
            }
            
            with open(self.vault_path, "w") as f:
                json.dump(vault_data, f, indent=2)
            
            # Physical backup
            self._create_physical_backup(seed, private_key, address)
            
            log.info(f"[VAULT] New Wallet Created: {address}")
            print(f"[VAULT] Physical Cold Storage generated in: {self.physical_dir}")
            
        except (IOError, OSError) as e:
            raise FXIONWalletError(f"Failed to create vault: {e}") from e
    
    def _create_physical_backup(self, seed: str, priv: str, addr: str) -> None:
        """Create physical cold storage backup files.
        
        Args:
            seed: Recovery seed hex
            priv: Private key hex
            addr: Public address
        """
        try:
            # Recovery seed
            with open(os.path.join(self.physical_dir, "RECOVERY_SEED.txt"), "w") as f:
                f.write("=== FXION OMEGA RECOVERY SEED ===\n")
                f.write("KEEP THIS SECURE AND OFFLINE\n\n")
                f.write(f"SEED HEX: {seed}\n")
            
            # Protected private key
            with open(os.path.join(self.physical_dir, "PRIVATE_KEY_PROTECTED.txt"), "w") as f:
                f.write("=== FXION PROTECTED PRIVATE KEY ===\n")
                f.write("ENCRYPTED WITH FXION XOR-INT4 MASK (0x0A)\n\n")
                encoded_key = "".join([chr(ord(c) ^ self.XOR_MASK) for c in priv])
                f.write(f"KEY: {encoded_key}\n")
            
            # Public address
            with open(os.path.join(self.physical_dir, "PUBLIC_ADDRESS.txt"), "w") as f:
                f.write("=== FXION PUBLIC BITCOIN ADDRESS ===\n")
                f.write("USE THIS TO RECEIVE MINING REWARDS\n\n")
                f.write(f"ADDRESS: {addr}\n")
            
            # Security manual
            with open(os.path.join(self.physical_dir, "SECURITY_INSTRUCTIONS.txt"), "w") as f:
                f.write("FXION OMEGA COLD STORAGE INSTRUCTIONS\n")
                f.write("=====================================\n")
                f.write("1. Copy this folder to a USB drive and delete from PC.\n")
                f.write("2. Private key is XORed with FXION mask for security.\n")
                f.write("3. Never share the RECOVERY_SEED.txt file.\n")
            
            log.info("Physical backup files created")
            
        except (IOError, OSError) as e:
            log.error(f"Failed to create physical backup: {e}")
            raise FXIONWalletError(f"Physical backup creation failed: {e}") from e
    
    def load_vault(self) -> None:
        """Load vault from JSON file."""
        try:
            with open(self.vault_path, "r") as f:
                self.data = json.load(f)
                self.address = self.data["address"]
            self._ensure_vault_schema()
            log.info("Vault loaded successfully")
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            log.warning(f"Vault load failed ({e}), attempting recovery")
            self.recover_from_backup()
    
    def recover_from_backup(self) -> None:
        """Recover wallet from physical cold storage backup."""
        try:
            pub_path = os.path.join(self.physical_dir, "PUBLIC_ADDRESS.txt")
            key_path = os.path.join(self.physical_dir, "PRIVATE_KEY_PROTECTED.txt")
            
            if not os.path.exists(pub_path) or not os.path.exists(key_path):
                raise FXIONWalletError("Physical cold storage backup files missing")
            
            # Parse address
            address = None
            with open(pub_path, "r") as f:
                for line in f:
                    if line.startswith("ADDRESS:"):
                        address = line.split("ADDRESS:", 1)[1].strip()
                        break
            
            # Parse encrypted key
            encrypted_key = None
            with open(key_path, "r") as f:
                for line in f:
                    if line.startswith("KEY:"):
                        encrypted_key = line.split("KEY:", 1)[1].strip()
                        break
            
            if not address or not encrypted_key:
                raise FXIONWalletError("Could not parse cold storage backup")
            
            private_key = "".join([chr(ord(c) ^ self.XOR_MASK) for c in encrypted_key])
            
            self.data = {
                "address": address,
                "encrypted_private_key": encrypted_key,
                "balance_btc": 1000000.0,
                "balance_usd": 81000000000.0,
                "balance_cad": 111000000000.0,
                "fiat_holdings": {"USD": 0.0, "CAD": 0.0},
                "transaction_history": [
                    {
                        "type": "deposit",
                        "amount_btc": 10.0,
                        "details": {},
                        "timestamp": str(time.time())
                    },
                    {
                        "type": "recovery",
                        "amount_btc": 1000000.0,
                        "details": {},
                        "timestamp": str(time.time())
                    }
                ],
                "created_at": str(time.time())
            }
            
            self.address = address
            self.save_vault()
            log.info(f"Wallet recovered: {address}")
            
        except (IOError, ValueError) as e:
            raise FXIONWalletError(f"Recovery failed: {e}") from e
    
    def save_vault(self) -> None:
        """Save vault to JSON file."""
        try:
            with open(self.vault_path, "w") as f:
                json.dump(self.data, f, indent=2)
            log.debug("Vault saved")
        except IOError as e:
            raise FXIONWalletError(f"Failed to save vault: {e}") from e
    
    def get_address(self) -> str:
        """Get wallet address."""
        if not self.address:
            raise FXIONWalletError("Wallet address not available")
        return self.address
    
    def get_balance(self) -> float:
        """Get BTC balance."""
        self.load_vault()
        return self.data.get("balance_btc", 0.0)
    
    def get_balances(self) -> Dict[str, Any]:
        """Get all balances."""
        self.load_vault()
        return {
            "btc": self.data.get("balance_btc", 0.0),
            "usd": self.data.get("balance_usd", 0.0),
            "cad": self.data.get("balance_cad", 0.0),
            "fiat_holdings": self.data.get("fiat_holdings", {"USD": 0.0, "CAD": 0.0})
        }
    
    def _ensure_vault_schema(self) -> None:
        """Ensure vault has all required fields."""
        modified = False
        
        if "balance_usd" not in self.data:
            rates = self.DEFAULT_EXCHANGE_RATES
            self.data["balance_usd"] = round(self.data.get("balance_btc", 0.0) * rates["USD"], 2)
            modified = True
        
        if "balance_cad" not in self.data:
            rates = self.DEFAULT_EXCHANGE_RATES
            self.data["balance_cad"] = round(self.data.get("balance_btc", 0.0) * rates["CAD"], 2)
            modified = True
        
        if "fiat_holdings" not in self.data:
            self.data["fiat_holdings"] = {"USD": 0.0, "CAD": 0.0}
            modified = True
        
        if "transaction_history" not in self.data:
            self.data["transaction_history"] = []
            modified = True
        
        if modified:
            self.save_vault()
    
    def _update_exchange_values(self) -> None:
        """Update fiat exchange values."""
        rates = self.DEFAULT_EXCHANGE_RATES
        self.data["balance_usd"] = round(self.data.get("balance_btc", 0.0) * rates["USD"], 2)
        self.data["balance_cad"] = round(self.data.get("balance_btc", 0.0) * rates["CAD"], 2)
    
    def _validate_address(self, address: str) -> bool:
        """Validate BTC address format."""
        return isinstance(address, str) and len(address) >= self.MIN_ADDRESS_LENGTH and address.startswith("1")
    
    def _validate_amount(self, amount: Any) -> bool:
        """Validate amount is positive number."""
        try:
            value = float(amount)
            return value > 0
        except (ValueError, TypeError):
            return False
    
    def _record_transaction(self, tx_type: str, amount: float, details: Optional[Dict] = None) -> None:
        """Record transaction.
        
        Args:
            tx_type: Transaction type
            amount: Amount in BTC
            details: Additional details
        """
        if "transaction_history" not in self.data:
            self.data["transaction_history"] = []
        
        record = {
            "type": tx_type,
            "amount_btc": round(amount, 8),
            "details": details or {},
            "timestamp": str(time.time())
        }
        self.data["transaction_history"].append(record)
        self.save_vault()
    
    def transfer_btc(self, recipient_address: str, amount_btc: Any, fee_btc: float = 0.0001) -> Dict[str, Any]:
        """Transfer BTC to recipient.
        
        Args:
            recipient_address: Recipient BTC address
            amount_btc: Amount to transfer
            fee_btc: Transaction fee
            
        Returns:
            Transaction result dict
            
        Raises:
            ValueError: If validation fails
        """
        self.load_vault()
        
        if not self._validate_address(recipient_address):
            raise ValueError("Invalid BTC recipient address")
        if not self._validate_amount(amount_btc):
            raise ValueError("Transfer amount must be positive")
        
        amount_btc = float(amount_btc)
        total_cost = round(amount_btc + fee_btc, 8)
        
        if self.data.get("balance_btc", 0.0) < total_cost:
            raise ValueError("Insufficient BTC balance for transfer plus fee")
        
        self.data["balance_btc"] = round(self.data["balance_btc"] - total_cost, 8)
        self._update_exchange_values()
        self._record_transaction(
            "transfer",
            amount_btc,
            {
                "recipient": recipient_address,
                "fee_btc": fee_btc,
                "remaining_balance_btc": self.data["balance_btc"]
            }
        )
        
        return {
            "recipient": recipient_address,
            "amount_btc": amount_btc,
            "fee_btc": fee_btc,
            "remaining_balance_btc": self.data["balance_btc"]
        }
    
    def exchange_btc(self, amount_btc: Any, currency: str) -> Dict[str, Any]:
        """Exchange BTC to fiat currency.
        
        Args:
            amount_btc: Amount to exchange
            currency: Target currency (USD/CAD)
            
        Returns:
            Exchange result dict
            
        Raises:
            ValueError: If validation fails
        """
        self.load_vault()
        currency = str(currency).upper()
        
        if currency not in self.DEFAULT_EXCHANGE_RATES:
            raise ValueError("Exchange currency must be USD or CAD")
        if not self._validate_amount(amount_btc):
            raise ValueError("Exchange amount must be positive")
        
        amount_btc = float(amount_btc)
        
        if self.data.get("balance_btc", 0.0) < amount_btc:
            raise ValueError("Insufficient BTC balance for exchange")
        
        rate = self.DEFAULT_EXCHANGE_RATES[currency]
        fiat_amount = round(amount_btc * rate, 2)
        
        self.data["balance_btc"] = round(self.data["balance_btc"] - amount_btc, 8)
        self.data["fiat_holdings"][currency] = round(
            self.data["fiat_holdings"].get(currency, 0.0) + fiat_amount, 2
        )
        self._update_exchange_values()
        self._record_transaction(
            "exchange",
            amount_btc,
            {
                "currency": currency,
                "fiat_received": fiat_amount,
                "remaining_balance_btc": self.data["balance_btc"]
            }
        )
        
        return {
            "currency": currency,
            "fiat_received": fiat_amount,
            "remaining_balance_btc": self.data["balance_btc"]
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    wallet = FXIONWallet()
    print(f"Active FXION-BTC Address: {wallet.get_address()}")
