from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from wallet import Wallet
from blockchain import Blockchain, TransactionSystem
from crypto import CryptoUtils

app = Flask(__name__)
app.secret_key = "blockchain_wallet_secret_key_2024"

# Initialize systems
Wallet.initialize()
Blockchain.initialize()

@app.route('/')
def index():
    """Redirect to login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, user_data = Wallet.authenticate(username, password)
        
        if success:
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        password = request.form.get('password')
        deposit = request.form.get('deposit', 0)
        
        if not fullname or not username or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
        
        success, message = Wallet.create_wallet(fullname, username, password, float(deposit))
        
        if success:
            flash('Wallet created successfully. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    wallet = Wallet.get_wallet(session['username'])
    
    if not wallet:
        session.clear()
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('login'))
    
    transactions = Blockchain.get_transaction_history()
    chain = Blockchain.get_chain()
    valid, _ = Blockchain.verify_chain()
    
    blockchain_stats = {
        'total_blocks': len(chain),
        'transactions': len(chain) - 1,
        'valid': valid
    }
    
    return render_template('dashboard.html', 
                         wallet=wallet, 
                         transactions=transactions,
                         blockchain_stats=blockchain_stats,
                         session=session)

@app.route('/send')
def send():
    """Display send transaction page"""
    if 'username' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    wallet = Wallet.get_wallet(session['username'])
    
    if not wallet:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('send.html', wallet=wallet, session=session)

@app.route('/send_transaction', methods=['POST'])
def send_transaction():
    """Process transaction with digital signature"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request data'})
    
    sender = data.get('sender')
    receiver = data.get('receiver')
    amount = float(data.get('amount', 0))
    private_key = data.get('private_key')
    
    # Validate inputs
    if not receiver:
        return jsonify({'success': False, 'message': 'Recipient is required'})
    
    if amount <= 0:
        return jsonify({'success': False, 'message': 'Amount must be greater than 0'})
    
    if not private_key:
        return jsonify({'success': False, 'message': 'Private key is required'})
    
    # Get wallets
    sender_wallet = Wallet.get_wallet(sender)
    receiver_wallet = Wallet.get_wallet(receiver)
    
    if not sender_wallet:
        return jsonify({'success': False, 'message': 'Sender wallet not found'})
    
    if not receiver_wallet:
        return jsonify({'success': False, 'message': f'Recipient "{receiver}" not found'})
    
    # Verify private key matches wallet
    if sender_wallet['private_key'] != private_key:
        return jsonify({
            'success': False, 
            'message': 'Invalid private key. Please use the correct private key for this wallet.'
        })
    
    # Check balance
    if sender_wallet['balance'] < amount:
        return jsonify({
            'success': False, 
            'message': f'Insufficient balance. Available: {sender_wallet["balance"]} BTC'
        })
    
    # Create and sign transaction
    transaction = TransactionSystem.create_transaction(sender, receiver, amount, private_key)
    
    # Verify and process
    success, message, block = TransactionSystem.verify_and_process_transaction(
        transaction, sender_wallet, receiver_wallet
    )
    
    if success:
        # Update balances
        Wallet.update_balance(sender, -amount)
        Wallet.update_balance(receiver, amount)
        
        return jsonify({
            'success': True,
            'message': message,
            'transaction': transaction['transaction_data'],
            'signature': transaction['signature'][:32] + '...',
            'block_index': block.index if block else 0
        })
    else:
        return jsonify({'success': False, 'message': message})

@app.route('/blockchain')
def blockchain_view():
    if 'username' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    chain = Blockchain.get_chain()
    valid, message = Blockchain.verify_chain()
    
    return render_template('blockchain_view.html', 
                         blockchain=chain,
                         status_message=message,
                         session=session)

@app.route('/dh_demo')
def dh_demo():
    if 'username' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    return render_template('dh_demo.html', session=session)

@app.route('/api/diffie_hellman')
def api_diffie_hellman():
    result = CryptoUtils.diffie_hellman_exchange()
    return jsonify(result)

@app.route('/api/verify_chain')
def api_verify_chain():
    valid, message = Blockchain.verify_chain()
    return jsonify({'valid': valid, 'message': message})

@app.route('/api/balance')
def api_balance():
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    wallet = Wallet.get_wallet(session['username'])
    return jsonify({
        'username': session['username'],
        'balance': wallet['balance'] if wallet else 0
    })

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("=" * 50)
    print("Blockchain Wallet System")
    print("=" * 50)
    print("Server running at: http://127.0.0.1:5000")
    print("\nDemo Accounts:")
    print("  Username: alice   | Password: alice123   | Balance: 50 BTC")
    print("  Username: bob     | Password: bob123     | Balance: 30 BTC")
    print("  Username: charlie | Password: charlie123 | Balance: 20 BTC")
    print("=" * 50)
    app.run(debug=True, port=5000)