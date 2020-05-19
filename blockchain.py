#import hashlib
import json
from textwrap import dedent
from Crypto.Hash import SHA512
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, render_template
from urllib.parse import urlparse
import requests

from user import User

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
        
    def create_transc(self, sender, receiver, amount):
        # Create a new transaction to add to the list of transactions
        # param sender: <str> contains the address of the sender
        # param receiver: <str> contains the address of the receiver
        # param amount: <int> amount
        #return: <int> the index of the block that will hold this transacation

        self.currTransacs.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
        })

        return self.final_block['index'] + 1

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
    blockchain.create_transc(sender="0", receiver=nodeID, amount=1)

    # now we can add the new block to the chain
    prev_hash = blockchain.hash_block(rear_block)
    block = blockchain.create_block(proof, prev_hash)

    response = {
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return render_template("mine.html", block = response)

@app.route('/transaction/new', methods=['POST'])
def create_transc():
    data = request.get_json()

    # Check to make sure we are not missing any important information
    required = ['sender', 'receiver', 'amount']
    if not all(k in data for k in required):
        return 'Missing data', 400

    # Create a new transaction
    indx = blockchain.create_transc(data['sender'], data['receiver'], data['amount'])

    response = {'message': f'The new transaction will be added to Block {indx}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def chain():
    response = {
        'chain': blockchain.chain,
        'length of chain': len(blockchain.chain)
    }
    return render_template("chain.html", chain_info = response, length = response['length of chain'])

@app.route('/recent')
def recent():
    return render_template("recent.html", view_block = blockchain.chain[-1])

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

@app.route("/")
def homepage():
    return render_template('homepage.html')

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    arguments = parser.parse_args()
    port = arguments.port
    app.run(host='0.0.0.0', port=port)

