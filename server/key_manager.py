from Crypto import Signature
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA512
from Crypto.Signature import pss

import os

RSA_KEY_SIZE = 2048
pubkey = None
privkey = None
            

def _load_keys_from_file():
    """
    returns public and private keys
    """
    global pubkey, privkey
    if os.path.exists('privkey.pem') and os.path.exists('pubkey.pem'):
        try:
            with open('pubkey.pem', 'rb') as f:
                pubkey = RSA.import_key(f.read())
                
            with open('privkey.pem', 'rb') as f:
                privkey = RSA.import_key(f.read(), "GdP7PTE>@7IH}Cj,++w<KnMKi\"e~`z")
                
        except Exception:
            pubkey = None
            privkey = None
            
    return pubkey, privkey

def _save_keys_to_file():
    if not privkey or not pubkey:
        return
    
    with open('privkey.pem', 'wb') as f:
        f.write(privkey.export_key('PEM'))
    
    with open('pubkey.pem', 'wb') as f:
        f.write(pubkey.export_key('PEM'))
        
def _generate_keys():
    global privkey, pubkey
    
    key = RSA.generate(RSA_KEY_SIZE)
    
    privkey = RSA.import_key(key.export_key())
    pubkey = key.publickey()
    
def _create_verifier():
    global verifier
    verifier = pss.new(pubkey)

def setup_keys(save_to_file=True):
    global privkey, pubkey
    
    privkey, pubkey = _load_keys_from_file()
    
    if not pubkey or not privkey:
        _generate_keys()

    if save_to_file:
        _save_keys_to_file()
    
    _create_verifier()
    
    

def generate_signature(data: str):
    hash = _generate_hash512_256(data.encode('utf-8'))
    """
    * truncate to 256 to prevent length-extension attacks as described in pycrypto documentation
    * documentation -> https://pycryptodome.readthedocs.io/en/latest/src/hash/sha512.html
    """
    signature = pss.new(privkey).sign(privkey)
    return signature

def verify_signature(data: str, signature: bytes) -> bool:
    hash = _generate_hash512_256(data)
    try:
        verifier.verify(hash, signature)
        return True
    except Exception:
        return False
    

def _generate_hash512_256(data: str):
    """
    Generate SHA-512 hash and truncate it to 256 bytes
    """
    return SHA512.new(data, truncate='256')
    

