import json
import os
from crypto import CryptoUtils

class Wallet:
    
    WALLETS_FILE = 'data/wallets.json'
    
    @classmethod
    def initialize(cls):
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(cls.WALLETS_FILE):
            default_wallets = {
                "alice": {
                    "name": "Alice Johnson",
                    "password": CryptoUtils.hash_password("alice123"),
                    "balance": 50.0,
                    "private_key": CryptoUtils.generate_key_pair("alice", "alice123")[0],
                    "public_key": CryptoUtils.generate_key_pair("alice", "alice123")[1],
                    "created_at": "2024-01-01"
                },
                "bob": {
                    "name": "Bob Smith",
                    "password": CryptoUtils.hash_password("bob123"),
                    "balance": 30.0,
                    "private_key": CryptoUtils.generate_key_pair("bob", "bob123")[0],
                    "public_key": CryptoUtils.generate_key_pair("bob", "bob123")[1],
                    "created_at": "2024-01-01"
                },
                "charlie": {
                    "name": "Charlie Brown",
                    "password": CryptoUtils.hash_password("charlie123"),
                    "balance": 20.0,
                    "private_key": CryptoUtils.generate_key_pair("charlie", "charlie123")[0],
                    "public_key": CryptoUtils.generate_key_pair("charlie", "charlie123")[1],
                    "created_at": "2024-01-01"
                }
            }
            with open(cls.WALLETS_FILE, 'w') as f:
                json.dump(default_wallets, f, indent=4)
    
    @classmethod
    def get_all_wallets(cls):
        cls.initialize()
        with open(cls.WALLETS_FILE, 'r') as f:
            return json.load(f)
    
    @classmethod
    def authenticate(cls, username, password):
        wallets = cls.get_all_wallets()
        username = username.lower()
        
        if username not in wallets:
            return False, "Invalid credentials"
        
        if wallets[username]["password"] != CryptoUtils.hash_password(password):
            return False, "Invalid credentials"
        
        return True, wallets[username]
    
    @classmethod
    def get_wallet(cls, username):
        wallets = cls.get_all_wallets()
        return wallets.get(username.lower())
    
    @classmethod
    def create_wallet(cls, name, username, password, initial_balance=0):
        wallets = cls.get_all_wallets()
        username = username.lower()
        
        if username in wallets:
            return False, "Username already exists"
        
        private_key, public_key = CryptoUtils.generate_key_pair(username, password)
        
        wallets[username] = {
            "name": name,
            "password": CryptoUtils.hash_password(password),
            "balance": float(initial_balance),
            "private_key": private_key,
            "public_key": public_key,
            "created_at": "2024-01-01"
        }
        
        with open(cls.WALLETS_FILE, 'w') as f:
            json.dump(wallets, f, indent=4)
        
        return True, "Wallet created successfully"
    
    @classmethod
    def update_balance(cls, username, amount):
        wallets = cls.get_all_wallets()
        username = username.lower()
        
        if username not in wallets:
            return False
        
        wallets[username]["balance"] += amount
        
        with open(cls.WALLETS_FILE, 'w') as f:
            json.dump(wallets, f, indent=4)
        
        return True
    
    @classmethod
    def get_balance(cls, username):
        wallet = cls.get_wallet(username)
        return wallet["balance"] if wallet else 0