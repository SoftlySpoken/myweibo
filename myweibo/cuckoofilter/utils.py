# coding=utf-8
import sys
import mmh3
import hashlib

if sys.version_info[0] == 3:
    from_bytes = lambda b: int.from_bytes(b, 'little')
else:
    from_bytes = lambda b: long(b.encode("hex"), 16)


def get_next_pow2(n):
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    n |= n >> 32
    n += 1
    return n


murmur_hash = lambda key: mmh3.hash_bytes(key, 0xdbd342)
md5_hash = lambda key: hashlib.md5(key).digest()
sha1_hash = lambda key: hashlib.sha1(key).digest()