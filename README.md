# CPSC-452-Final-Proj
CPSC 452 Cryptography Final Project

Christopher Phongsa - cphongsa@csu.fullerton.edu

Theresa Tanubrata - theresatanubrata123@csu.fullerton.edu

Marianne Tolentino - mariannetolentino@csu.fullerton.edu

Julian Coronado - juliancoronado@csu.fullerton.edu

Andrew Lopez - alopez8969@csu.fullerton.edu

-----------------------------
As of right now, our blockchain will be ran on the localhost:5000 by default

To begin the server, run the following line:

pipenv run python3 blockchain.py

Then open another terminal in the same directory, and run the following line:

pipenv run python3 blockchain.py -p 5001

*Note that for both terminals, make sure you have an extra tab opened in each so that you can run the cUrl commands

Now you will have two blockchains running on port 5000 and port 5001

To view the current chain:
curl http://localhost:5000/chain

To mine a block:
curl http://localhost:5000/mine

------------------------------------
The main goal of our project is to have the blockchains verify each others chains, and use the longest chain available as the current chain

To test this, make sure that each blockchain is registered with one another:

curl -X POST -H "Content-Type: application/json" -d '{
 "nodes": "http://127.0.0.1:5001"
}' http://localhost:5000/node/register

curl -X POST -H "Content-Type: application/json" -d '{
 "nodes": "http://127.0.0.1:5000"
}' http://localhost:5001/node/register

Then, do the following:
- on port 5000, mine a block:
curl http://localhost:5000/mine

if you view the chain, you'll see that it increased:
curl http://localhost:5000/chain

Then on port 5001, verify the chain of port 5000, and if it is longer than your chain, replace it as your chain
curl http://localhost:5000/node/resolve 

This is how you add a new transaction, after mining a new block:
curl -X POST -H "Content-Type: application/json" -d '{
 "sender": "d4ee26eee15148ee92c6cd394edd974e",
 "receiver": "someone-other-address",
 "amount": 5
}' http://localhost:5000/transaction/new
