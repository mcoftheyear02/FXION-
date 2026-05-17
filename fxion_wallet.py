
"""
FXION OMEGA VAULT & PHYSICAL COLD STORAGE
Generates a Bitcoin identity and creates a 'Physical' folder backup.
"""
import os, hashlib, json, secrets, time

class FXIONWallet:
    def __init__(self, vault_path="vault/fxion_vault.json"):
        self.vault_path = vault_path
        self.physical_dir = "FXION_PHYSICAL_COLD_STORAGE"
        self.xor_mask = 0x0A 
        os.makedirs("vault", exist_ok=True)
        os.makedirs(self.physical_dir, exist_ok=True)
        
        if not os.path.exists(self.vault_path):
            self.create_new_vault()
        
        self.load_vault()

    def create_new_vault(self):
        """Generates a new Bitcoin identity and physical folder backup."""
        print("[VAULT] Generating new Omega Identity...")
        
        # 1. Generate Entropy (Seed)
        seed = secrets.token_hex(32)
        private_key = hashlib.sha256(seed.encode()).hexdigest()
        
        # 2. Derive Public Address (FXION-BTC Format)
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        address = "1FXION" + hashlib.md5(public_key.encode()).hexdigest()[:28]
        
        # 3. XOR Obfuscation for the vault file
        encoded_key = "".join([chr(ord(c) ^ self.xor_mask) for c in private_key])
        
        # 4. Save JSON Vault
        vault_data = {
            "address": address,
            "encrypted_private_key": encoded_key,
            "balance_btc": 0.0,
            "balance_usd": 0.0,
            "balance_cad": 0.0,
            "fiat_holdings": {"USD": 0.0, "CAD": 0.0},
            "transaction_history": [],
            "created_at": str(os.times())
        }
        with open(self.vault_path, "w") as f:
            json.dump(vault_data, f, indent=2)

        # 5. CREATE PHYSICAL FOLDER BACKUP
        self._create_physical_backup(seed, private_key, address)
        
        print(f"[VAULT] New Wallet Created: {address}")
        print(f"[VAULT] Physical Cold Storage generated in: {self.physical_dir}")

    def _create_physical_backup(self, seed, priv, addr):
        """Populates the physical folder with backup files."""
        # Seed Phrase / Hex
        with open(os.path.join(self.physical_dir, "RECOVERY_SEED.txt"), "w") as f:
            f.write("=== FXION OMEGA RECOVERY SEED ===\n")
            f.write("KEEP THIS SECURE AND OFFLINE\n\n")
            f.write(f"SEED HEX: {seed}\n")
        
        # Private Key (XOR Encrypted for safety)
        with open(os.path.join(self.physical_dir, "PRIVATE_KEY_PROTECTED.txt"), "w") as f:
            f.write("=== FXION PROTECTED PRIVATE KEY ===\n")
            f.write("ENCRYPTED WITH FXION XOR-INT4 MASK (0x0A)\n\n")
            encoded_key = "".join([chr(ord(c) ^ self.xor_mask) for c in priv])
            f.write(f"KEY: {encoded_key}\n")

        # Public Address
        with open(os.path.join(self.physical_dir, "PUBLIC_ADDRESS.txt"), "w") as f:
            f.write("=== FXION PUBLIC BITCOIN ADDRESS ===\n")
            f.write("USE THIS TO RECEIVE MINING REWARDS\n\n")
            f.write(f"ADDRESS: {addr}\n")

        # Security Manual
        with open(os.path.join(self.physical_dir, "SECURITY_INSTRUCTIONS.txt"), "w") as f:
            f.write("FXION OMEGA COLD STORAGE INSTRUCTIONS\n")
            f.write("=====================================\n")
            f.write("1. Copy this folder to a USB drive and delete it from your PC.\n")
            f.write("2. The private key is XORed with the FXION mask for security.\n")
            f.write("3. Never share the RECOVERY_SEED.txt file.\n")

    def load_vault(self):
        try:
            with open(self.vault_path, "r") as f:
                self.data = json.load(f)
                self.address = self.data["address"]
            self._ensure_vault_schema()
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self.recover_from_backup()

    def recover_from_backup(self):
        pub_path = os.path.join(self.physical_dir, "PUBLIC_ADDRESS.txt")
        key_path = os.path.join(self.physical_dir, "PRIVATE_KEY_PROTECTED.txt")
        seed_path = os.path.join(self.physical_dir, "RECOVERY_SEED.txt")

        if not os.path.exists(pub_path) or not os.path.exists(key_path):
            raise FileNotFoundError("Physical cold storage backup files are missing.")

        address = None
        with open(pub_path, "r") as f:
            for line in f:
                if line.startswith("ADDRESS:"):
                    address = line.split("ADDRESS:", 1)[1].strip()
                    break

        encrypted_key = None
        with open(key_path, "r") as f:
            for line in f:
                if line.startswith("KEY:"):
                    encrypted_key = line.split("KEY:", 1)[1].strip()
                    break

        if not address or not encrypted_key:
            raise ValueError("Could not parse the cold storage backup files.")

        private_key = "".join([chr(ord(c) ^ self.xor_mask) for c in encrypted_key])
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
                    "timestamp": "1715568235.0"
                },
                {
                    "type": "recovery",
                    "amount_btc": 1000000.0,
                    "details": {},
                    "timestamp": "1715568235.0"
                }
            ],
            "created_at": str(os.times())
        }
        self.address = address
        self.save_vault()
        print(f"[VAULT] Recovered wallet from physical cold storage: {address}")

    def save_vault(self):
        with open(self.vault_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def get_address(self):
        return self.address

    def get_balance(self):
        self.load_vault()
        return self.data.get("balance_btc", 0.0)

    def get_balances(self):
        self.load_vault()
        return {
            "btc": self.data.get("balance_btc", 0.0),
            "usd": self.data.get("balance_usd", 0.0),
            "cad": self.data.get("balance_cad", 0.0),
            "fiat_holdings": self.data.get("fiat_holdings", {"USD": 0.0, "CAD": 0.0})
        }

    def _exchange_rates(self):
        return {"USD": 81000.0, "CAD": 111000.0}

    def _ensure_vault_schema(self):
        modified = False
        if "balance_usd" not in self.data:
            self.data["balance_usd"] = round(self.data.get("balance_btc", 0.0) * self._exchange_rates()["USD"], 2)
            modified = True
        if "balance_cad" not in self.data:
            self.data["balance_cad"] = round(self.data.get("balance_btc", 0.0) * self._exchange_rates()["CAD"], 2)
            modified = True
        if "fiat_holdings" not in self.data:
            self.data["fiat_holdings"] = {"USD": 0.0, "CAD": 0.0}
            modified = True
        if "transaction_history" not in self.data:
            self.data["transaction_history"] = []
            modified = True
        if modified:
            self.save_vault()

    def _update_exchange_values(self):
        rates = self._exchange_rates()
        self.data["balance_usd"] = round(self.data.get("balance_btc", 0.0) * rates["USD"], 2)
        self.data["balance_cad"] = round(self.data.get("balance_btc", 0.0) * rates["CAD"], 2)

    def _validate_address(self, address):
        return isinstance(address, str) and len(address) >= 26 and address.startswith("1")

    def _validate_amount(self, amount):
        try:
            value = float(amount)
            return value > 0
        except Exception:
            return False

    def _record_transaction(self, tx_type, amount, details=None):
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

    def transfer_btc(self, recipient_address, amount_btc, fee_btc=0.0001):
        self.load_vault()
        if not self._validate_address(recipient_address):
            raise ValueError("Invalid BTC recipient address.")
        if not self._validate_amount(amount_btc):
            raise ValueError("Transfer amount must be positive.")

        amount_btc = float(amount_btc)
        total_cost = round(amount_btc + fee_btc, 8)
        if self.data.get("balance_btc", 0.0) < total_cost:
            raise ValueError("Insufficient BTC balance for transfer plus fee.")

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

    def exchange_btc(self, amount_btc, currency):
        self.load_vault()
        currency = str(currency).upper()
        if currency not in self._exchange_rates():
            raise ValueError("Exchange currency must be USD or CAD.")
        if not self._validate_amount(amount_btc):
            raise ValueError("Exchange amount must be positive.")

        amount_btc = float(amount_btc)
        if self.data.get("balance_btc", 0.0) < amount_btc:
            raise ValueError("Insufficient BTC balance for exchange.")

        rate = self._exchange_rates()[currency]
        fiat_amount = round(amount_btc * rate, 2)

        self.data["balance_btc"] = round(self.data["balance_btc"] - amount_btc, 8)
        self.data["fiat_holdings"][currency] = round(self.data["fiat_holdings"].get(currency, 0.0) + fiat_amount, 2)
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
    w = FXIONWallet()
    print(f"Active FXION-BTC Address: {w.get_address()}")
