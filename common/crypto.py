
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from config import Config


class AESCipher:
    def __init__(self):
        self.bs = 32
        self.key = hashlib.sha256(Config.MASTER_KEY.encode()).digest()

    def encrypt(self, raw):
        raw = self.pad(raw).encode()
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def unpad(s):
        return s[:-ord(s[len(s)-1:])]
