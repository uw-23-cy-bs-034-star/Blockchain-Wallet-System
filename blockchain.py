import json
import os
from datetime import datetime
from crypto import CryptoUtils

class Block:
    
    def __init__(self, index, transaction, signature, timestamp, previous_hash):
        self.index = index
        self.transaction = transaction
        self.signature = signature
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        data = f"{self.index}{self.transaction}{self.signature}{self.timestamp}{self.previous_hash}"
        return CryptoUtils.calculate_hash(data)
    
    def to_dict(self):
        return {
            'index': self.index,
            'transaction': self.transaction,
            'signature': self.signature,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }


class Blockchain:
    
    BLOCKCHAIN_FILE = 'data/blockchain.json'
    
    @classmethod
    def initialize(cls):
        os.makedirs('data', exist_ok=True)
        
        if not os.path.exists(cls.BLOCKCHAIN_FILE):
            genesis_block = Block(0, "Genesis Block", "genesis_signature", str(datetime.now()), "0")
            
            with open(cls.BLOCKCHAIN_FILE, 'w') as f:
                json.dump([genesis_block.to_dict()], f, indent=4)
    
    @classmethod
    def get_chain(cls):
        cls.initialize()
        with open(cls.BLOCKCHAIN_FILE, 'r') as f:
            return json.load(f)
    
    @classmethod
    def add_block(cls, transaction_data, sender, receiver, amount, signature):
        chain = cls.get_chain()
        
        new_block = Block(
            index=len(chain),
            transaction=transaction_data,
            signature=signature,
            timestamp=str(datetime.now()),
            previous_hash=chain[-1]['hash']
        )
        
        chain.append(new_block.to_dict())
        
        with open(cls.BLOCKCHAIN_FILE, 'w') as f:
            json.dump(chain, f, indent=4)
        
        return new_block
    
    @classmethod
    def verify_chain(cls):
        chain = cls.get_chain()
        
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i-1]
            
            if current['previous_hash'] != previous['hash']:
                return False, f"Block {i} has invalid previous hash"
            
            block = Block(
                current['index'],
                current['transaction'],
                current['signature'],
                current['timestamp'],
                current['previous_hash']
            )
            
            if current['hash'] != block.calculate_hash():
                return False, f"Block {i} has invalid hash"
        
        return True, "Blockchain is valid"
    
    @classmethod
    def get_transaction_history(cls):
        chain = cls.get_chain()
        return chain[1:]


class TransactionSystem:
    
    @staticmethod
    def create_transaction(sender, receiver, amount, private_key):
        """Create and sign a transaction"""
        transaction_data = f"{sender} sends {amount} BTC to {receiver}"
        signature = CryptoUtils.sign_transaction(transaction_data, private_key)
        
        return {
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'transaction_data': transaction_data,
            'signature': signature,
            'private_key': private_key
        }
    
    @staticmethod
    def verify_and_process_transaction(transaction, sender_wallet, receiver_wallet):
        """
        Verify transaction signature and process if valid
        """
        sender = transaction['sender']
        receiver = transaction['receiver']
        amount = transaction['amount']
        signature = transaction['signature']
        transaction_data = transaction['transaction_data']
        private_key = transaction['private_key']
        
        # Check 1: Sufficient balance
        if sender_wallet['balance'] < amount:
            return False, f"Insufficient balance. Available: {sender_wallet['balance']} BTC", None
        
        # Check 2: Verify signature using the private key
        expected_signature = CryptoUtils.sign_transaction(transaction_data, private_key)
        
        if signature != expected_signature:
            return False, "Invalid signature! Transaction rejected.", None
        
        # Check 3: Verify that private key matches the wallet
        if sender_wallet['private_key'] != private_key:
            return False, "Private key does not match wallet!", None
        
        # All checks passed - add to blockchain
        new_block = Blockchain.add_block(
            transaction_data,
            sender,
            receiver,
            amount,
            signature
        )
        
        return True, "Transaction verified and added to blockchain", new_block