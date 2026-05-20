import hashlib
import random

class CryptoUtils:
    
    @staticmethod
    def generate_key_pair(username, password):
        """Generate private and public key pair"""
        # Private key from username + password
        private_key = hashlib.sha256(f"{username}_{password}_private".encode()).hexdigest()
        
        # Public key derived from private key (consistent relationship)
        public_key = hashlib.sha256(f"{private_key}_public".encode()).hexdigest()
        
        return private_key, public_key
    
    @staticmethod
    def sign_transaction(transaction_data, private_key):
        """
        DIGITAL SIGNATURE SYSTEM
        Sign a transaction using sender's private key
        """
        # Create signature by hashing transaction + private key
        message = f"{transaction_data}{private_key}"
        signature = hashlib.sha256(message.encode()).hexdigest()
        return signature
    
    @staticmethod
    def verify_signature(transaction_data, signature, public_key, private_key=None):
        """
        VERIFICATION SYSTEM
        Verify transaction signature using public key
        """
        # Method 1: If we have the private key, we can verify directly
        if private_key:
            expected_signature = hashlib.sha256(f"{transaction_data}{private_key}".encode()).hexdigest()
            return signature == expected_signature
        
        # Method 2: Verify using public key (simplified for demo)
        # In real blockchain, you'd use asymmetric encryption
        # For demo, we'll use a deterministic relationship
        derived_key = hashlib.sha256(f"{public_key}_derived".encode()).hexdigest()[:20]
        signature_prefix = signature[:20]
        
        return signature_prefix == derived_key
    
    @staticmethod
    def diffie_hellman_exchange():
        """Diffie-Hellman key exchange demonstration"""
        p = 29  # Prime number
        g = 3   # Base/generator
        
        alice_private = random.randint(2, 20)
        bob_private = random.randint(2, 20)
        
        alice_public = pow(g, alice_private, p)
        bob_public = pow(g, bob_private, p)
        
        alice_shared = pow(bob_public, alice_private, p)
        bob_shared = pow(alice_public, bob_private, p)
        
        return {
            'p': p,
            'g': g,
            'alice_private': alice_private,
            'bob_private': bob_private,
            'alice_public': alice_public,
            'bob_public': bob_public,
            'shared_secret': alice_shared,
            'success': alice_shared == bob_shared
        }
    
    @staticmethod
    def calculate_hash(data):
        """Calculate SHA-256 hash of data"""
        return hashlib.sha256(str(data).encode()).hexdigest()
    
    @staticmethod
    def hash_password(password):
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()