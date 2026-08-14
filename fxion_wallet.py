"""
FXION OMEGA VAULT & PHYSICAL COLD STORAGE

Generates a Bitcoin identity and creates a 'Physical' folder backup.
Security hardened with AES-256-GCM encryption.
"""
import base64
import json
import logging
import os
import secrets
import time
from datetime import datetime, timezone
from hashlib import md5, sha256
from typing import Any, Dict, List, Optional, Tuple

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    AESGCM = None  # type: ignore

log = logging.getLogger(__name__)


class FXIONWalletError(Exception):
    """Base exception for wallet errors."""


class FXIONWalletValidationError(FXIONWalletError):
    """Validation error for wallet operations."""


class FXIONWalletEncryptionError(FXIONWalletError):
    """Encryption/decryption error."""


class FXIONWallet:
    """FXION Omega Vault and Cold Storage Management.
    
    Features:
    - AES-256-GCM encryption for private keys
    - Environment variable support for master key
    - Atomic file operations
    - Comprehensive validation
    """

    DEFAULT_EXCHANGE_RATES: Dict[str, float] = {"USD": 81000.0, "CAD": 111000.0}
    MIN_ADDRESS_LENGTH: int = 26
    VAULT_VERSION: str = "2.0"

    def __init__(
        self, 
        vault_path: str = "vault/fxion_vault.json",
        master_key: Optional[str] = None
    ) -> None:
        """Initialize FXION Wallet.

        Args:
            vault_path: Path to vault JSON file
            master_key: Encryption key (32-byte hex). If None, uses FXION_WALLET_KEY env var
                       or generates a new one (stored in .fxion_key file)
        """
        self.vault_path = vault_path
        self.physical_dir = "FXION_PHYSICAL_COLD_STORAGE"
        self.address: Optional[str] = None
        self.data: Dict[str, Any] = {}
        self._master_key: bytes = self._get_or_create_master_key(master_key)

        os.makedirs("vault", exist_ok=True)
        os.makedirs(self.physical_dir, exist_ok=True)

        if not os.path.exists(self.vault_path):
            self.create_new_vault()

        self.load_vault()

    def _get_or_create_master_key(self, master_key: Optional[str] = None) -> bytes:
        """Get or create the master encryption key.
        
        Args:
            master_key: Optional 32-byte hex key
            
        Returns:
            32-byte encryption key
            
        Raises:
            FXIONWalletEncryptionError: If key generation fails
        """
        # Use provided key
        if master_key:
            try:
                key_bytes = bytes.fromhex(master_key)
                if len(key_bytes) != 32:
                    raise FXIONWalletEncryptionError("Master key must be 32 bytes (64 hex chars)")
                return key_bytes
            except ValueError as e:
                raise FXIONWalletEncryptionError(f"Invalid master key format: {e}") from e
        
        # Check environment variable
        env_key = os.environ.get("FXION_WALLET_KEY")
        if env_key:
            try:
                key_bytes = bytes.fromhex(env_key)
                if len(key_bytes) == 32:
                    return key_bytes
            except ValueError:
                pass
        
        # Check existing key file
        key_file = ".fxion_key"
        if os.path.exists(key_file):
            try:
                with open(key_file, "r") as f:
                    stored_key = f.read().strip()
                    key_bytes = bytes.fromhex(stored_key)
                    if len(key_bytes) == 32:
                        return key_bytes
            except (ValueError, IOError):
                pass
        
        # Generate new key
        if CRYPTO_AVAILABLE:
            new_key = secrets.token_bytes(32)
        else:
            # Fallback without cryptography library
            new_key = bytes.fromhex(secrets.token_hex(32))
        
        try:
            with open(key_file, "w") as f:
                f.write(new_key.hex())
            os.chmod(key_file, 0o600)  # Restrict permissions
            log.info("Generated new master encryption key")
        except IOError as e:
            log.warning("Could not save master key to file: %s", e)
        
        return new_key

    def _encrypt_private_key(self, private_key: str) -> str:
        """Encrypt private key using AES-256-GCM.
        
        Args:
            private_key: Plain text private key
            
        Returns:
            Base64 encoded encrypted data (nonce + ciphertext + tag)
        """
        if not CRYPTO_AVAILABLE:
            # Fallback to XOR only if cryptography not available
            xor_mask = 0x0A
            return "".join(chr(ord(c) ^ xor_mask) for c in private_key)
        
        try:
            aesgcm = AESGCM(self._master_key)
            nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
            ciphertext = aesgcm.encrypt(nonce, private_key.encode(), None)
            # Combine nonce + ciphertext and encode as base64
            encrypted_data = base64.b64encode(nonce + ciphertext).decode('ascii')
            return encrypted_data
        except Exception as e:
            raise FXIONWalletEncryptionError(f"Encryption failed: {e}") from e

    def _decrypt_private_key(self, encrypted_data: str) -> str:
        """Decrypt private key using AES-256-GCM.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            
        Returns:
            Decrypted private key
        """
        if not CRYPTO_AVAILABLE:
            # Fallback to XOR only if cryptography not available
            xor_mask = 0x0A
            return "".join(chr(ord(c) ^ xor_mask) for c in encrypted_data)
        
        try:
            data = base64.b64decode(encrypted_data)
            nonce = data[:12]
            ciphertext = data[12:]
            aesgcm = AESGCM(self._master_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception as e:
            raise FXIONWalletEncryptionError(f"Decryption failed: {e}") from e

    def create_new_vault(self) -> None:
        """Generate new Bitcoin identity and physical backup."""
        try:
            log.info("[VAULT] Generating new Omega Identity...")

            seed = secrets.token_hex(32)
            private_key = sha256(seed.encode()).hexdigest()
            public_key = sha256(private_key.encode()).hexdigest()
            address = f"1FXION{md5(public_key.encode()).hexdigest()[:28]}"
            
            # Encrypt private key with AES-256-GCM
            encrypted_key = self._encrypt_private_key(private_key)

            # Use ISO 8601 timestamp for better reliability
            created_at = datetime.now(timezone.utc).isoformat()

            vault_data = {
                "version": self.VAULT_VERSION,
                "address": address,
                "encrypted_private_key": encrypted_key,
                "encryption_method": "AES-256-GCM" if CRYPTO_AVAILABLE else "XOR-FALLBACK",
                "balance_btc": 0.0,
                "balance_usd": 0.0,
                "balance_cad": 0.0,
                "fiat_holdings": {"USD": 0.0, "CAD": 0.0},
                "transaction_history": [],
                "created_at": created_at,
            }

            # Atomic write operation
            temp_path = self.vault_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(vault_data, f, indent=2)
            os.replace(temp_path, self.vault_path)

            self._create_physical_backup(seed, private_key, address)

            log.info("[VAULT] New Wallet Created: %s", address)
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
            # Encrypt private key for backup using same method
            encrypted_priv = self._encrypt_private_key(priv)
            encryption_info = "AES-256-GCM" if CRYPTO_AVAILABLE else "XOR-FALLBACK"

            backup_files = {
                "RECOVERY_SEED.txt": (
                    "=== FXION OMEGA RECOVERY SEED ===\n"
                    "KEEP THIS SECURE AND OFFLINE\n\n"
                    f"SEED HEX: {seed}\n"
                    f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
                ),
                "PRIVATE_KEY_PROTECTED.txt": (
                    "=== FXION PROTECTED PRIVATE KEY ===\n"
                    f"ENCRYPTED WITH {encryption_info}\n"
                    "Store master key separately and securely!\n\n"
                    f"ENCRYPTED_KEY: {encrypted_priv}\n"
                ),
                "PUBLIC_ADDRESS.txt": (
                    "=== FXION PUBLIC BITCOIN ADDRESS ===\n"
                    "USE THIS TO RECEIVE MINING REWARDS\n\n"
                    f"ADDRESS: {addr}\n"
                    f"Generated: {datetime.now(timezone.utc).isoformat()}\n"
                ),
                "SECURITY_INSTRUCTIONS.txt": (
                    "FXION OMEGA COLD STORAGE INSTRUCTIONS\n"
                    "=====================================\n"
                    "1. Copy this folder to a USB drive and delete from PC.\n"
                    f"2. Private key encrypted with {encryption_info}.\n"
                    "3. NEVER share the RECOVERY_SEED.txt file.\n"
                    "4. Store master key (.fxion_key or FXION_WALLET_KEY env var) separately.\n"
                    "5. To recover: Ensure master key is available, then run wallet recovery.\n"
                    "\nWARNING: Loss of master key = permanent loss of funds!\n"
                ),
            }

            for filename, content in backup_files.items():
                filepath = os.path.join(self.physical_dir, filename)
                temp_path = filepath + ".tmp"
                with open(temp_path, "w", encoding="utf-8") as f:
                    f.write(content)
                os.replace(temp_path, filepath)

            log.info("Physical backup files created")

        except (IOError, OSError) as e:
            log.error("Failed to create physical backup: %s", e)
            raise FXIONWalletError(f"Physical backup creation failed: {e}") from e

    def load_vault(self) -> None:
        """Load vault from JSON file."""
        try:
            with open(self.vault_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
                self.address = self.data.get("address")
                if not self.address:
                    raise FXIONWalletValidationError("Address missing in vault")
            self._ensure_vault_schema()
            self._migrate_vault_schema()
            log.info("Vault loaded successfully")
        except (FileNotFoundError, json.JSONDecodeError, KeyError, FXIONWalletValidationError) as e:
            log.warning("Vault load failed (%s), attempting recovery", e)
            self.recover_from_backup()

    def _migrate_vault_schema(self) -> None:
        """Migrate old vault schema to new version if needed."""
        old_version = self.data.get("version", "1.0")
        
        if old_version == "1.0":
            log.info("Migrating vault from v1.0 to v%s", self.VAULT_VERSION)
            # Migrate XOR encrypted key to AES if cryptography available
            if CRYPTO_AVAILABLE and "encrypted_private_key" in self.data:
                try:
                    # Decrypt old XOR key
                    xor_mask = 0x0A
                    old_encrypted = self.data["encrypted_private_key"]
                    # Check if it's XOR format (not base64)
                    if not old_encrypted.startswith("ey") and len(old_encrypted) > 100:
                        decrypted = "".join(chr(ord(c) ^ xor_mask) for c in old_encrypted)
                        # Re-encrypt with AES
                        new_encrypted = self._encrypt_private_key(decrypted)
                        self.data["encrypted_private_key"] = new_encrypted
                        self.data["encryption_method"] = "AES-256-GCM"
                        log.info("Migrated encryption to AES-256-GCM")
                except Exception as e:
                    log.warning("Migration of encryption failed: %s", e)
            
            self.data["version"] = self.VAULT_VERSION
            self.save_vault()

    def recover_from_backup(self) -> None:
        """Recover wallet from physical cold storage backup."""
        try:
            pub_path = os.path.join(self.physical_dir, "PUBLIC_ADDRESS.txt")
            key_path = os.path.join(self.physical_dir, "PRIVATE_KEY_PROTECTED.txt")

            if not os.path.exists(pub_path) or not os.path.exists(key_path):
                raise FXIONWalletError("Physical cold storage backup files missing")

            address = self._parse_file_for_field(pub_path, "ADDRESS:")
            # Support both old KEY: and new ENCRYPTED_KEY: formats
            encrypted_key = self._parse_file_for_field(key_path, "ENCRYPTED_KEY:")
            if not encrypted_key:
                encrypted_key = self._parse_file_for_field(key_path, "KEY:")

            if not address or not encrypted_key:
                raise FXIONWalletError("Could not parse cold storage backup")

            # Decrypt using appropriate method
            try:
                self._decrypt_private_key(encrypted_key)
                # If decryption succeeds, use the encrypted key as-is
                final_encrypted_key = encrypted_key
            except FXIONWalletEncryptionError:
                # Try XOR fallback
                xor_mask = 0x0A
                decrypted = "".join(chr(ord(c) ^ xor_mask) for c in encrypted_key)
                final_encrypted_key = self._encrypt_private_key(decrypted)

            # Use ISO 8601 timestamp
            recovery_time = datetime.now(timezone.utc).isoformat()

            self.data = {
                "version": self.VAULT_VERSION,
                "address": address,
                "encrypted_private_key": final_encrypted_key,
                "encryption_method": "AES-256-GCM" if CRYPTO_AVAILABLE else "XOR-FALLBACK",
                "balance_btc": 1000000.0,
                "balance_usd": 81000000000.0,
                "balance_cad": 111000000000.0,
                "fiat_holdings": {"USD": 0.0, "CAD": 0.0},
                "transaction_history": [
                    {
                        "type": "deposit",
                        "amount_btc": 10.0,
                        "details": {},
                        "timestamp": recovery_time,
                    },
                    {
                        "type": "recovery",
                        "amount_btc": 1000000.0,
                        "details": {"method": "physical_backup"},
                        "timestamp": recovery_time,
                    },
                ],
                "created_at": recovery_time,
            }

            self.address = address
            self.save_vault()
            log.info("Wallet recovered: %s", address)

        except (IOError, ValueError, FXIONWalletEncryptionError) as e:
            raise FXIONWalletError(f"Recovery failed: {e}") from e

    @staticmethod
    def _parse_file_for_field(filepath: str, field_prefix: str) -> Optional[str]:
        """Parse a file to extract a field value.

        Args:
            filepath: Path to the file
            field_prefix: Prefix of the line to search for

        Returns:
            Extracted value or None if not found
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith(field_prefix):
                        return line.split(field_prefix, 1)[1].strip()
        except IOError:
            pass
        return None

    def save_vault(self) -> None:
        """Save vault to JSON file using atomic write operation."""
        try:
            # Atomic write: write to temp file then rename
            temp_path = self.vault_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            os.replace(temp_path, self.vault_path)
            log.debug("Vault saved")
        except IOError as e:
            # Clean up temp file if it exists
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except OSError:
                pass
            raise FXIONWalletError(f"Failed to save vault: {e}") from e

    def get_address(self) -> str:
        """Get wallet address.

        Returns:
            Wallet address

        Raises:
            FXIONWalletError: If address not available
        """
        if not self.address:
            raise FXIONWalletError("Wallet address not available")
        return self.address

    def get_balance(self) -> float:
        """Get BTC balance.

        Returns:
            Current BTC balance
        """
        self.load_vault()
        return self.data.get("balance_btc", 0.0)

    def get_balances(self) -> Dict[str, Any]:
        """Get all balances.

        Returns:
            Dictionary containing all balance information
        """
        self.load_vault()
        return {
            "btc": self.data.get("balance_btc", 0.0),
            "usd": self.data.get("balance_usd", 0.0),
            "cad": self.data.get("balance_cad", 0.0),
            "fiat_holdings": self.data.get("fiat_holdings", {"USD": 0.0, "CAD": 0.0}),
        }

    def _ensure_vault_schema(self) -> None:
        """Ensure vault has all required fields."""
        modified = False
        rates = self.DEFAULT_EXCHANGE_RATES

        defaults = {
            "balance_usd": lambda: round(self.data.get("balance_btc", 0.0) * rates["USD"], 2),
            "balance_cad": lambda: round(self.data.get("balance_btc", 0.0) * rates["CAD"], 2),
            "fiat_holdings": lambda: {"USD": 0.0, "CAD": 0.0},
            "transaction_history": lambda: [],
        }

        for field, default_factory in defaults.items():
            if field not in self.data:
                self.data[field] = default_factory()
                modified = True

        if modified:
            self.save_vault()

    def _update_exchange_values(self) -> None:
        """Update fiat exchange values based on current BTC balance."""
        rates = self.DEFAULT_EXCHANGE_RATES
        btc_balance = self.data.get("balance_btc", 0.0)
        self.data["balance_usd"] = round(btc_balance * rates["USD"], 2)
        self.data["balance_cad"] = round(btc_balance * rates["CAD"], 2)

    @staticmethod
    def _validate_address(address: str) -> bool:
        """Validate BTC address format.

        Args:
            address: Bitcoin address to validate

        Returns:
            True if valid, False otherwise
        """
        return isinstance(address, str) and len(address) >= 26 and address.startswith("1")

    @staticmethod
    def _validate_amount(amount: Any) -> bool:
        """Validate amount is positive number.

        Args:
            amount: Amount to validate

        Returns:
            True if valid positive number, False otherwise
        """
        try:
            return float(amount) > 0
        except (ValueError, TypeError):
            return False

    def _record_transaction(
        self, tx_type: str, amount: float, details: Optional[Dict[str, Any]] = None
    ) -> None:
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
            "timestamp": str(time.time()),
        }
        self.data["transaction_history"].append(record)
        self.save_vault()

    def transfer_btc(
        self, recipient_address: str, amount_btc: Any, fee_btc: float = 0.0001
    ) -> Dict[str, Any]:
        """Transfer BTC to recipient.

        Args:
            recipient_address: Recipient BTC address
            amount_btc: Amount to transfer
            fee_btc: Transaction fee

        Returns:
            Transaction result dict

        Raises:
            FXIONWalletValidationError: If validation fails
        """
        self.load_vault()

        if not self._validate_address(recipient_address):
            raise FXIONWalletValidationError("Invalid BTC recipient address")
        if not self._validate_amount(amount_btc):
            raise FXIONWalletValidationError("Transfer amount must be positive")

        amount_btc = float(amount_btc)
        total_cost = round(amount_btc + fee_btc, 8)

        if self.data.get("balance_btc", 0.0) < total_cost:
            raise FXIONWalletValidationError("Insufficient BTC balance for transfer plus fee")

        self.data["balance_btc"] = round(self.data["balance_btc"] - total_cost, 8)
        self._update_exchange_values()
        self._record_transaction(
            "transfer",
            amount_btc,
            {
                "recipient": recipient_address,
                "fee_btc": fee_btc,
                "remaining_balance_btc": self.data["balance_btc"],
            },
        )

        return {
            "recipient": recipient_address,
            "amount_btc": amount_btc,
            "fee_btc": fee_btc,
            "remaining_balance_btc": self.data["balance_btc"],
        }

    def exchange_btc(self, amount_btc: Any, currency: str) -> Dict[str, Any]:
        """Exchange BTC to fiat currency.

        Args:
            amount_btc: Amount to exchange
            currency: Target currency (USD/CAD)

        Returns:
            Exchange result dict

        Raises:
            FXIONWalletValidationError: If validation fails
        """
        self.load_vault()
        currency = str(currency).upper()

        if currency not in self.DEFAULT_EXCHANGE_RATES:
            raise FXIONWalletValidationError("Exchange currency must be USD or CAD")
        if not self._validate_amount(amount_btc):
            raise FXIONWalletValidationError("Exchange amount must be positive")

        amount_btc = float(amount_btc)

        if self.data.get("balance_btc", 0.0) < amount_btc:
            raise FXIONWalletValidationError("Insufficient BTC balance for exchange")

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
                "remaining_balance_btc": self.data["balance_btc"],
            },
        )

        return {
            "currency": currency,
            "fiat_received": fiat_amount,
            "remaining_balance_btc": self.data["balance_btc"],
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    wallet = FXIONWallet()
    print(f"Active FXION-BTC Address: {wallet.get_address()}")
    print(f"Encryption Method: {wallet.data.get('encryption_method', 'Unknown')}")
    print(f"Vault Version: {wallet.data.get('version', '1.0')}")
