# coding=utf-8
from myweibo.cuckoofilter import cuckoofilter, bucket

s = "test"


class CuckooFilter:
    def __init__(self):
        self.fail_insert = set()
        self.cf = cuckoofilter.CuckooFilter(num_buckets=1000000, bucket_size=4)
        with open("D:\\projects\\gitrepo\\classProject\\SeaGraph\\server\\resource\\screen_names.txt",
                  encoding='utf-8') as fin:
            for line in fin:
                name = line.strip()
                if not self.cf.insert(name):
                    self.fail_insert.add(name)

    def insert(self,s) -> bool:
        return self.cf.insert(s)

    def contains(self,s) -> bool:
        return self.cf.contains(s)

    def delete(self,s) -> bool:
        return self.cf.delete(s)

    def reportLoadFactor(self) -> str:
        return f'Load factor: {self.cf.num_items / (self.cf.num_buckets * self.cf.bucket_size)}'
