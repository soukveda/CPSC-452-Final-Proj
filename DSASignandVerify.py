import os, random, struct, re
import sys
import hashlib



class DSA:

    def __init__(self, p, q, g, M, sign_or_verify, key, r, s):
        # Domain parameters
        self.p = p
        self.q = q
        self.g = g
        self.M = M
        self.sign_or_verify = sign_or_verify
        self.key = key
        self.r = r
        self.s = s

    def sign(self):
        start_over = True
        while start_over:
            k = random.randint(1, self.q-1)
            X = (self.g**k) % self.p
            r = X % self.q
            K = self.modInverse(k, self.q)

            h = int(hashlib.sha256(self.M.encode()).hexdigest(), base=16) % self.q

            s = (K*(h + self.key*r)) % self.q

            if s == 0 or r == 0:
                start_over = True
            else:
                start_over = False
        return r, s

    def modInverse(self, a, m):
        a = a % m;
        for x in range(1, m):
            if ((a * x) % m == 1):
                return x
        return 1

    def verify(self):
        if 0 < self.r < self.q and 0 < self.s < self.q:
            pass
        else:
            return False
        w = self.modInverse(self.s, self.q)
        h = int(hashlib.sha256(self.M.encode()).hexdigest(), base=16) % self.q

        u1 = (h*w) % self.q

        u2 = (self.r*w) % self.q

        X = ((self.g**u1)*(self.key**u2)) % self.p

        v = X % self.q

        if v == self.r:
            print(f'{v} == {self.r}')
            return True
        else:
            print(f'{v} != {self.r}')
            return False


if __name__ == '__main__':
    signature = DSA(283, 47, 60, 'hi what is this', 'sign', 24, 0, 0)
    verification = DSA(283, 47, 60, 'hi what is this', 'verify', 158, 0, 0)
    if signature.sign_or_verify == 'sign':
        print("Now signing")
        verification.r, verification.s = signature.sign()
        if verification.r and verification.s:
            print(f'r = {verification.r}')
            print(f's = {verification.s}')
            print("Signature success!")
            print("Now verifying")
            valid = verification.verify()
            if valid:
                print("Verification success!")
            else:
                print("Verification failed!")
        else:
            print("Signature failed!")





