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
        dataHash = SHA512.new(self.message.encode()).digest()
        sig = signKey.sign(dataHash, '')
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
        dataHash = SHA512.new(self.message.encode()).digest()
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

        rsa_sign = RSAClass('privKey.pem', '', "helloworld")
        signKey = rsa_sign.loadKey()
        signature = rsa_sign.getSignature(signKey)
        print(f'Signature: {signature}')

    # We are verifying the signature

        rsa_verify = RSAClass('pubKey.pem', signature, "helloworld")
        sigFileSig = rsa_verify.loadSig()
        signKey = rsa_verify.loadKey()
        isVerified = rsa_verify.verifyFileSig(signKey, sigFileSig)




