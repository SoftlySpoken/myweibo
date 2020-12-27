# coding=utf-8

import random
from . import bucket
from .utils import get_next_pow2, from_bytes, murmur_hash, md5_hash, sha1_hash

try:
    import cPickle as pickle
except ImportError:
    import pickle

MAX_CUCKOO_COUNT = 10

class CuckooFilter(object):

    def __init__(self, num_buckets, bucket_size, fp_size=4):
        self.num_buckets = int(get_next_pow2(num_buckets))
        self.bucket_size = bucket_size
        self.fp_size = fp_size
        self.num_items = 0   # the number of fingerprints in cuckoofilter
        self.buckets = [bucket.Bucket(bucket_size) for _ in range(self.num_buckets)]

    def insert(self, item):
        if self.contains(item):
            return False
        fp, i1, i2 = self.get_fp_and_indexes(item)
        if self.insert_fp(fp, i1) or self.insert_fp(fp, i2):
            return True
        # reinsert, kick out some fps
        i = random.choice([i1, i2])
        last_but_one_i = -1
        for _ in range(MAX_CUCKOO_COUNT):
            fp = self.buckets[i].swap(fp)
            last_but_one_i = i
            i = self.get_ano_index(fp, i)
            if self.insert_fp(fp, i):
                return True
        # Roll back
        i = last_but_one_i
        for _ in range(MAX_CUCKOO_COUNT):
            fp = self.buckets[i].swap(fp)
            i = self.get_ano_index(fp, i)
            assert not self.insert_fp(fp, i)
        return False

    def insert_fp(self, fp, i):
        if self.buckets[i].insert(fp):
            self.num_items += 1
            return True
        return False

    def get_fp_and_indexes(self, item):
        # f = fingerprint(x) --> md5_hash
        # i1 = hash_1(x) --> sha1_hash
        # i2 = i1 ^ hash_2(f) --> murmur_hash
        try:
            item = pickle.dumps(item)
        except TypeError:
            raise f'item {item} is not serializable'
        fp = md5_hash(item)[: self.fp_size]
        i1 = from_bytes(sha1_hash(item)) % self.num_buckets
        i2 = self.get_ano_index(fp, i1)
        assert i1 == self.get_ano_index(fp, i2)
        return fp, i1, i2

    def get_ano_index(self, fp, i):
        return i ^ (from_bytes(murmur_hash(fp)) % self.num_buckets)

    def delete(self, item):
        fp, i1, i2 = self.get_fp_and_indexes(item)
        return self.delete_fp(fp, i1) or self.delete_fp(fp, i2)

    def delete_fp(self, fp, i):
        if self.buckets[i].delete(fp):
            self.num_items -= 1
            return True
        return False

    def contains(self, item):
        fp, i1, i2 = self.get_fp_and_indexes(item)
        b1, b2 = self.buckets[i1], self.buckets[i2]
        return (b1.get_fp_index(fp) > -1) or (b2.get_fp_index(fp) > -1)

    def size(self):
        return self.num_items

    def __contains__(self, item):
        return self.contains(item)

    def __len__(self):
        return self.num_buckets

    def __str__(self):
        return (
            f'<CuckooFilter: num_buckets={str(self.num_buckets)}, '
            f'bucket_size={self.bucket_size}, '
            f'fp_size={self.fp_size}byte(s)>'
        )