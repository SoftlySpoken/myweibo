from . import GstoreConnector
import json
import random
import datetime
from random import sample

class Connection:
    def __init__(self):
        # self.IP = "172.31.222.78"
        # self.Port = 9001
        self.IP = "127.0.0.1"
        self.Port = 9000
        self.username = "root"
        self.password = "123456"
        self.db_name = "weibo"
        self.con = GstoreConnector.GstoreConnector(self.IP, self.Port, self.username, self.password)

    def query(self, sparql):
        res = self.con.query(self.db_name, "json", sparql)
        return res

    def refresh(self):
        self.con.unload(self.db_name)
        self.con.load(self.db_name)

gc = Connection()
def query_res(res, code):
    res = json.loads(res)
    if res['StatusCode'] != 0:  # 查询出错
        return False
    ans_dict = {}
    ans_list = []
    res = res['results']['bindings']
    if res:
        for i in range(len(res)):
            if code == "001":
                ans_list.append(res[i]['z']['value'])
            if code == "010":
                ans_list.append(res[i]['y']['value'])
            if code == "100":
                ans_list.append(res[i]['x']['value'])
            if code == "011":
                ans_dict[res[i]['y']['value']] = res[i]['z']['value']
            if code == "110":
                ans_dict[res[i]['x']['value']] = res[i]['y']['value']
            if code == "101":
                ans_dict[res[i]['x']['value']] = res[i]['z']['value']
        if code == "001" or code == "010" or code == "100":
            return ans_list
        elif code == "011" or code == "110" or code == "101":
            return ans_dict
        else:
            return res
    else:
        return None

def insert_res(res):
    res = json.loads(res)
    if res['StatusCode'] == 402:  # 插入操作成功
        return True
    else:
        return False

def delete_res(res):
    res = json.loads(res)
    if res['StatusCode'] == 402: # 删除操作成功
        return True
    else:
        return False


def ask_res(res):
    res = json.loads(res)
    print(res)
    if res['StatusCode'] != 0:
        return None
    else:
        res = res['results']['bindings']
        res = res[0]['_askResult']['value']
        print("res = " + res)
        if res == "false":
            return False
        else:
            return True

def weiboID():
    base = 4000000000000000
    ID = base + random.randint(0, 1000000000000000)
    return str(ID)

def userID():
    base = 4000000000
    ID = base + random.randint(0, 1000000000)
    return str(ID)

def get_time():
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d_%H:%M:%S")
    return time

def commentID():
    base = 5000000000000000
    ID = base + random.randint(0, 2000000000000000)
    return str(ID)