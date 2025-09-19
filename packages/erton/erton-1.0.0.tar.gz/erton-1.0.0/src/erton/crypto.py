
from __future__ import annotations
import struct, os, hmac, hashlib, base64, time
from typing import Tuple, Optional
def _rotl32(v: int, n: int) -> int: return ((v<<n)&0xffffffff)|(v>>(32-n))
def _qr(a,b,c,d): a=(a+b)&0xffffffff; d^=a; d=_rotl32(d,16); c=(c+d)&0xffffffff; b^=c; b=_rotl32(b,12); a=(a+b)&0xffffffff; d^=a; d=_rotl32(d,8); c=(c+d)&0xffffffff; b^=c; b=_rotl32(b,7); return a,b,c,d
def _block(key:bytes,counter:int,nonce:bytes)->bytes:
    a0,a1,a2,a3=struct.unpack('<4I',b'expand 32-byte k'); k0,k1,k2,k3,k4,k5,k6,k7=struct.unpack('<8I',key); c0=counter&0xffffffff; n0,n1,n2=struct.unpack('<3I',nonce)
    st=[a0,a1,a2,a3,k0,k1,k2,k3,k4,k5,k6,k7,c0,n0,n1,n2]; w=st[:]
    for _ in range(10):
        w[0],w[4],w[8],w[12]=_qr(w[0],w[4],w[8],w[12]); w[1],w[5],w[9],w[13]=_qr(w[1],w[5],w[9],w[13]); w[2],w[6],w[10],w[14]=_qr(w[2],w[6],w[10],w[14]); w[3],w[7],w[11],w[15]=_qr(w[3],w[7],w[11],w[15])
        w[0],w[5],w[10],w[15]=_qr(w[0],w[5],w[10],w[15]); w[1],w[6],w[11],w[12]=_qr(w[1],w[6],w[11],w[12]); w[2],w[7],w[8],w[13]=_qr(w[2],w[7],w[8],w[13]); w[3],w[4],w[9],w[14]=_qr(w[3],w[4],w[9],w[14])
    out=[(w[i]+st[i])&0xffffffff for i in range(16)]
    return struct.pack('<16I',*out)
def chacha20_keystream(n:int,key:bytes,nonce:bytes,counter:int=1)->bytes:
    out=bytearray()
    while len(out)<n: out.extend(_block(key,counter,nonce)); counter=(counter+1)&0xffffffff
    return bytes(out[:n])
def generate_key()->bytes: return os.urandom(32)
def encrypt(pt:bytes,key:bytes,*,nonce:bytes|None=None,aad:bytes=b'')->tuple[bytes,bytes,bytes]:
    if nonce is None: nonce=os.urandom(12)
    ct=bytes([p^k for p,k in zip(pt,chacha20_keystream(len(pt),key,nonce,1))])
    tag=hmac.new(key,nonce+aad+ct,hashlib.sha256).digest(); return nonce,ct,tag
def decrypt(nonce:bytes,ct:bytes,tag:bytes,key:bytes,*,aad:bytes=b'')->bytes:
    exp=hmac.new(key,nonce+aad+ct,hashlib.sha256).digest()
    if not hmac.compare_digest(exp,tag): raise ValueError('auth failed')
    return bytes([c^k for c,k in zip(ct,chacha20_keystream(len(ct),key,nonce,1))])
def hmac_sign(data:bytes,key:bytes)->bytes: return hmac.new(key,data,hashlib.sha256).digest()
def hmac_verify(data:bytes,sig:bytes,key:bytes)->bool: return hmac.compare_digest(hmac_sign(data,key),sig)
def issue_token(pid:str,key:bytes,ttl:int=5)->str:
    raw=f"{pid}:{int(time.time())}:{ttl}".encode(); sig=hmac_sign(raw,key); return base64.b64encode(raw+sig).decode()
def check_token(tok:str,key:bytes)->bool:
    try:
        raw=base64.b64decode(tok.encode()); payload,sig=raw[:-32],raw[-32:]
        if not hmac_verify(payload,sig,key): return False
        _,ts,ttl=payload.decode().split(':'); ts=int(ts); ttl=int(ttl)
        return int(time.time())<=ts+ttl
    except Exception: return False
