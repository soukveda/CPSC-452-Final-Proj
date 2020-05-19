import os, random, struct, re
import sys
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512
from base64 import b64encode, b64decode


class RSAClass:
    def __init__(self, keyPath, signature, message):
        self.keyPath = keyPath
        self.signature = signature
        self.message = message

    def loadKey(self):
        # The RSA key
        key = None

        # Open the key file
        with open(self.keyPath, 'r') as keyFile:
            # Read the key file
            keyFileContent = keyFile.read()

            # Decode the key
            decodedKey = b64decode(keyFileContent)

            # Load the key
            key = RSA.importKey(decodedKey)

        # Return the key
        return key

    def getSignature(self, signKey):
        dataHash = SHA512.new(self.message.encode()).hexdigest()
        sig = signKey.sign(dataHash.encode(), '')
        print(f'signature tuple: {sig}')
        tupleToStr = ''.join(str(sig) for v in sig)
        print(f'signature string: {tupleToStr}')
        return tupleToStr

    def loadSig(self):
        #remove unwanted characters
        result = re.sub('[^0-9]', '', self.signature)

        #convert to int
        keyInt = int(result)
        #convert to tuple
        keyTuple = (keyInt,)
        print(f'keyTuple: {keyTuple}')
        return keyTuple

    def verifyFileSig(self, key, keyTuple):
        dataHash = SHA512.new(self.message.encode()).hexdigest()
        isValid = self.verifySig(dataHash, keyTuple, key)
        return isValid

    def verifySig(self, theHash, sig, veriKey):
        if veriKey.verify(theHash, sig):
            print("Signatures match!")
            return True
        else:
            print("Signatures do NOT match!")
            return False


# The main function
if __name__ == '__main__':
    # Make sure that all the arguments have been provided
    #if len(sys.argv) < 5:
    #    print("USAGE: " + sys.argv[0] + " <KEY> <SIGNATURE FILE NAME> <INPUT FILE NAME>")
    #    exit(-1)

    # The key
    #key = sys.argv[1]

    # Signature file name
    #sig = sys.argv[2]

    # The input file name
    #message = sys.argv[3]

    # The mode i.e., sign or verify
    #mode = sys.argv[4]

    #publicKey = "MIIBIjANBgkqhkiG9w0BAQEFAA"
    # We are signing
    #if mode == "sign":
        rsa_sign = RSAClass('privKey.pem', '', "helloworld")
        signKey = rsa_sign.loadKey()
        signature = rsa_sign.getSignature(signKey)
        print(f'Signature: {signature}')

    # We are verifying the signature
    #elif mode == "verify":

        rsa_verify = RSAClass('pubKey.pem', signature, "helloworld")
        sigFileSig = rsa_verify.loadSig()
        signKey = rsa_verify.loadKey()
        isVerified = rsa_verify.verifyFileSig(signKey, sigFileSig)

    #else:
        #print("Invalid mode", mode)
