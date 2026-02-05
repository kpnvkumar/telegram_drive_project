# accounts/otp.py
import os, struct, base64, random, pyotp
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def encrypt_random_integer():
    key = os.urandom(32)
    iv = os.urandom(16)
    r = random.randint(0, 10000000)

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(struct.pack(">I", r)) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded) + encryptor.finalize()

    return key, iv, base64.b32encode(encrypted).decode(), r

def generate_otp(secret):
    return pyotp.TOTP(secret).now()

def verify_otp(secret, user_input):
    return pyotp.TOTP(secret).verify(user_input, valid_window=5)
