#import hashlib
import json
from textwrap import dedent
from Crypto.Hash import SHA512
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from urllib.parse import urlparse
import requests
from DSASignandVerify import DSA
from RSASignandVerify import RSAClass
from user import User, list_of_users

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.currTransacs = []

        # create a genesis block
        self.create_block(prev_hash=-1, proof=-1)

        self.nodes = set()

    def create_block(self, proof, prev_hash=None):
        # Create a new Block to add to the chain
        # param proof: <int> proof given by proof of work algorithm
        # param prev_hash: <str> hash of previous block
        # return: <dict> a new block

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.currTransacs,
            'proof': proof,
            'previous_hash': prev_hash or self.hash_block(self.chain[-1]), 
        }

        # reset the current list of transactions for the new block
        self.currTransacs = []

        self.chain.append(block)
        return block
        
    def create_transc(self, sender, receiver, amount, dsa_rsa, signature):
        # Create a new transaction to add to the list of transactions
        # param sender: <str> contains the address of the sender
        # param receiver: <str> contains the address of the receiver
        # param amount: <int> amount
        #return: <int> the index of the block that will hold this transacation


        self.currTransacs.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'dsa_rsa': dsa_rsa,
            'signature': signature,
        })
        for i in list_of_users:
            if i.address == sender and i.amount >= amount:
                i.amount -= amount
                for j in list_of_users:
                    if j.address == receiver:
                        j.amount += amount
                return self.final_block['index'] + 1
            elif i.address == sender and i.amount < amount:
                return 0

    def reg_node(self, address):
        # Add a new node to the list of nodes
        # param address: <str> address of the node --> eg: 'http://192.123.0.3:5001'
        # return: None

        parse_url = urlparse(address)
        #print(parse_url)
        self.nodes.add(parse_url.netloc)

    def verify_chain(self, chain):
        # Determine if the blockchain is valid
        # param chain: <list> blockchain
        # return: <bool> True if valid, False otherwise

        rear_block = chain[0]
        curr_indx = 1

        while curr_indx < len(chain):
            block = chain[curr_indx]
            # Verify that the hash of this block is valid/correct
            if block['previous_hash'] != self.hash_block(rear_block):
                return False
            # Verify that the proof is correct
            if not self.verify_p(rear_block['proof'], block['proof']):
                return False

            rear_block = block
            curr_indx += 1
        return True

    def longest_chain_conflict(self):
        # Resolves conflicting chains by choosing the longest chain
        # return: <bool> True if our chain was replaced, False otherwise

        confliciing_nodes = self.nodes
        #print("Here are the nodes" + str(confliciing_nodes))
        new_chain = None

        # Get the length of our chain
        max_len = len(self.chain)

        # Verify all the chains from the nodes in our network
        for node in confliciing_nodes:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                curr_len = response.json()['length of chain']

                chain = response.json()['chain']

                print("verify_chain: " + str(self.verify_chain(chain)))

                # Check if the current chain is valid and potentially longer then our chain
                if curr_len > max_len and self.verify_chain(chain):
                    max_len = curr_len
                    new_chain = chain
        # if we found a longer and valid chain, we can replace our chain with the longer chain
        if new_chain is not None:
            self.chain = new_chain
            return True
        
        # Otherwise, we will keep our current chain and return false
        return False


    
    def proof_of_work(self, rear_proof):
        # simple proof of work algorithm:
        # find a number p; such that hash(pp') contains leading 4 zeroes, where p = previous p'
        # p is the previous proof
        # p' is the new proof
        # param rear_proof: <int>
        # return: <int>

        proof = 0
        while self.verify_p(rear_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def verify_p(rear_proof, proof):
        # verify the authenticity of the proof
        # the hash needs to contain the 8 leading zeroes
        # param rear_proof: <int> previous proof
        # param proof: <int> current proof
        
        check = f'{rear_proof}{proof}'.encode()
        check_hash = SHA512.new(check).hexdigest()
        return check_hash[:4] == "0000"


    @staticmethod
    def hash_block(block):
        # hash a block using SHA-256 (similar method from project 3 || pycrypto)
        # param block: <dict> Block
        # return <str>

        # need to check that the dictionary is ordered (if false, this can create inconsistent hashes)
        block_str = json.dumps(block, sort_keys=True).encode()

        return SHA512.new(block_str).hexdigest()

    @property
    def final_block(self):
        # Return the last block in the chain
        return self.chain[-1]
    
    def get_signature(self, sender, receiver, amount, dsa_rsa):
        # Combine sender, receiver, and amount info to digitally sign
        data = sender + receiver + str(amount)
        for i in list_of_users:
            if i.address == sender:
                key = i.priv_key
                print(key)
        if dsa_rsa == "dsa":
            print("DSA is chosen")
            dsa_sign = DSA(283, 47, 60, data, 'sign', key, 0, 0)
            return dsa_sign.sign()
        elif dsa_rsa == "rsa":
            print("RSA is chosen")
            #keyPath = input("What filename is your privKey in?")
            rsa_sign = RSAClass(key, '', data)
            signKey = rsa_sign.loadKey()
            rsa_sign.signature = rsa_sign.getSignature(signKey)
            return rsa_sign.signature

    def verify_new_transaction(self, sender, receiver, amount, dsa_rsa, signature):
        # Combine sender, receiver, and amount info to digitally sign
        data = sender + receiver + str(amount)
        print('VERIFYING TRANSACTION')
        for i in list_of_users:
            if i.address == sender:
                key = i.pub_key
                print(key)
        if dsa_rsa == "dsa":
            print("DSA is chosen")
            dsa_verify = DSA(283, 47, 60, data, 'verify', key, signature[0], signature[1])
            return dsa_verify.verify()
        elif dsa_rsa == "rsa":
            print("RSA is chosen")
            #keyPath = input("What filename is your privKey in?")
            rsa_verify = RSAClass(key, signature, data)
            signKey = rsa_verify.loadKey()
            keyTuple = rsa_verify.loadSig()
            return rsa_verify.verifyFileSig(signKey, keyTuple)

    def create_new_user(self, address, privKey, pubKey):
        temp = User(address, privKey, pubKey)
        if temp in list_of_users:
            return True
        else:
            return False

    def wallet(self, address):
        amount = 0
        for i in list_of_users:
            if i.address == address:
                amount = i.amount
        return amount


# Instantiate server node
app = Flask(__name__)

# Generate an address for this node
nodeID = str(uuid4()).replace('-', '')

# Instantiate the blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # We will use the proof of work algorithm to calculate the next proof
    rear_block = blockchain.final_block
    rear_proof = rear_block['proof']
    proof = blockchain.proof_of_work(rear_proof)

    # Award an amount for calculating the proof
    # We can set the sender to "0" to signify that this node has mined a new coin
    blockchain.create_transc(sender="0", receiver=nodeID, amount=1, dsa_rsa=None, signature=None)

    # now we can add the new block to the chain
    prev_hash = blockchain.hash_block(rear_block)
    block = blockchain.create_block(proof, prev_hash)

    response = {
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 201

@app.route('/wallet', methods=['POST'])
def check_wallet():
    data = request.get_json()
    # Check to make sure we are not missing any important information
    required = ['address']
    if not all(k in data for k in required):
        return 'Missing data', 400
    amount = blockchain.wallet(data['address'])
    response = {'message': f'You have {amount} in your wallet'}
    return jsonify(response), 201

@app.route('/transactions/new', methods=['POST'])
def create_transc():
    data = request.get_json()

    # Check to make sure we are not missing any important information
    required = ['sender', 'receiver', 'amount', 'dsa_rsa']
    if not all(k in data for k in required):
        return 'Missing data', 400

    # Create signature/confidental for RSA or DSA
    signature = blockchain.get_signature(data['sender'], data['receiver'], data['amount'], data['dsa_rsa'])

    # Create a new transaction
    indx = blockchain.create_transc(data['sender'], data['receiver'], data['amount'], data['dsa_rsa'], signature)
    if indx == 0:
        response = {'message': f'The new transaction could not be added to the blockchain'}
    else:
        response = {'message': f'The new transaction will be added to Block {indx}'}
    return jsonify(response), 201


@app.route('/transactions/verify')
def verify_transc():
    # Get the latest transaction to verify
    jsonData = json.dumps(blockchain.currTransacs[len(blockchain.currTransacs)-1])
    print(blockchain.currTransacs)
    data = json.loads(jsonData)
    print(data)
    print(data['signature'])

    verified = blockchain.verify_new_transaction(data['sender'], data['receiver'], data['amount'], data['dsa_rsa'], data['signature'])
    response = {'message': f'The new transaction is {verified}'}
    return jsonify(response), 201


@app.route('/createUser', methods=['POST'])
def createUser():
    data = request.get_json()
    # Check to make sure we are not missing any important information
    required = ['address', 'privKey', 'pubKey']
    if not all(k in data for k in required):
        return 'Missing data', 400

    validUser = blockchain.create_new_user(data['address'], data['privKey'], data['pubKey'])
    for i in list_of_users:
        print(i.__dict__)
    if validUser:
        response = {'message': f'The new user has been created!'}
    else:
        response = {'message': 'The new user could not be created!'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def chain():
    response = {
        'chain': blockchain.chain,
        'length of chain': len(blockchain.chain)
    }
    return jsonify(response), 201

@app.route('/recent')
def recent():
    response = blockchain.chain[-1]
    return jsonify(response), 201

@app.route('/node/register', methods=['POST'])
def reg_node():
    data = request.get_json()

    nodes = data.get('nodes')
    if nodes is None:
        return "Error: Nodes were not successfully sent", 400
    
    #for nodes in nodes:
    #print(nodes)
    blockchain.reg_node(nodes)

    response = {
        'message': 'New nodes have been successfully added',
        'total_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201

@app.route('/node/resolve', methods=['GET'])
def longest_chain():
    result = blockchain.longest_chain_conflict()

    if result:
        response = {
            'message': 'A new chain was found and our chain has been replaced',
            'chain': blockchain.chain
        }
    else:
        response = {
            'message': 'No longer chain has been found',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    arguments = parser.parse_args()
    port = arguments.port
    app.run(host='0.0.0.0', port=port)

