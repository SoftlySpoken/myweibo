# coding=utf-8
import random
import threading


class Bucket(object):

    def __init__(self, bucket_size):
        self.capacity = bucket_size
        self.items = []

    def insert(self, fp):
        assert isinstance(fp, bytes)
        if len(self.items) >= self.capacity:
            return False
        self.items.append(fp)
        return True

    def delete(self, fp):
        assert isinstance(fp, bytes)
        try:
            self.items.remove(fp)
            return True
        except:
            return False

    def get_fp_index(self, fp):
        try:
            return self.items.index(fp)
        except ValueError:
            return -1

    def swap(self, fp):
        # i = random.randint(0, len(self) - 1)
        i = len(self.items) - 1
        fp, self.items[i] = self.items[i], fp
        return fp

    def __contains__(self, fp):
        return self.get_fp_index(fp) > -1

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return "<Bucket: capacity=" + str(self.capacity) + ">"
