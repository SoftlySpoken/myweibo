from myweibo.util import *
from myweibo.CuckooClient import CuckooFilter
cuckooClient = CuckooFilter()

class User:
    def __init__(self):
        self.name = "我爱海量图"
        self.ID = "0"
        self.password = "123456"
        self.location = "未知"
        self.gender = "m"
        self.url = "TBD"
        self.created_time = ""
        self.followersnum = "0"
        self.friendsnum = "0"
        self.statusesnum = "0"

    def get_name(self):
        return self.name

    def get_ID(self):
        return self.ID

    def get_password(self):
        return self.password

    def get_location(self):
        return self.location

    def get_gender(self):
        return self.gender

    def get_url(self):
        return self.url

    def get_followersnum(self):
        return self.followersnum

    def get_friendsnum(self):
        return self.friendsnum

    def get_statuesnum(self):
        return self.statusesnum

    def setNewUser(self, info):
        msg = {}
        name = info.get('name')
        ID = info.get('tel')
        if ID is None:
            msg['status'] = -1
            msg['msg'] = "用户ID错误！"
            return msg
        password = info.get('password')
        if password is None:
            password = ""
        if name is None:
            name = "我爱海量图"
        flag_loc = False
        if info.get('province') != None:
            flag_loc = True
            province = info.get('province')
        else:
            province = ""
        if info.get('city') != None:
            flag_loc = True
            city = info.get('city')
        else:
            city = ""
        if  flag_loc == True:
            location = province + city
        else:
            location = "太阳系火星新人类基地"
        gender = info.get('gender')
        if gender is None:
            gender = "m"
        url = "TBD"
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d_%H:%M:%S")
        created_time = time

        # 向cuckoo Filter查询是否有这个用户
        if cuckooClient.contains(ID):
            # 有可能有假阳性，向gStore查询以最终确认
            sparql_unique = "ask {<" + ID + "> ?x ?y}"
            if ask_res(gc.query(sparql_unique)) == True:
                msg['status'] = '0'  # 账户已存在
                msg['msg'] = '用户已存在！'
                return msg
        cuckooClient.insert(ID)
        sparql_name = "insert data {<" + ID + "> <name> \"" + name + "\".}"
        sparql_pwd = "insert data {<" + ID + "> <password> \"" + password + "\"^^<http://www.w3.org/2001/XMLSchema#integer>.}"
        sparql_location = "insert data {<" + ID + "> <location> \"" + location + "\".}"
        sparql_gender = "insert data {<" + ID + "> <gender> \"" + gender + "\".}"
        sparql_url = "insert data {<" + ID + "> <url> \"" + url + "\".}"
        sparql_followersnum = "insert data {<" + ID + "> <followersnum> \"0\"^^<http://www.w3.org/2001/XMLSchema#integer>.}"
        sparql_friendsnum = "insert data {<" + ID + "> <friendsnum> \"0\"^^<http://www.w3.org/2001/XMLSchema#integer>.}"
        sparql_statusesnum = "insert data {<" + ID + "> <statusesnum> \"0\"^^<http://www.w3.org/2001/XMLSchema#integer>.}"
        sparql_time = "insert data {<" + ID + "> <created> \"" + time + "\".}"
        if not insert_res(gc.query(sparql_name)):
            msg['status'] = '-1'
            msg['msg'] = '用户名错误'
            return msg
        if not insert_res(gc.query(sparql_pwd)):
            msg['status'] = '-1'
            msg['msg'] = '密码错误'
            return msg
        if not insert_res(gc.query(sparql_location)):
            msg['status'] = '-1'
            msg['msg'] = '所在地区错误'
            return msg
        if not insert_res(gc.query(sparql_gender)):
            msg['status'] = '-1'
            msg['msg'] = '性别错误'
            return msg
        if not insert_res(gc.query(sparql_url)):
            msg['status'] = '-1'
            msg['msg'] = 'url添加错误'
            return msg
        if not insert_res(gc.query(sparql_followersnum)):
            msg['status'] = '-1'
            msg['msg'] = '粉丝数错误'
            return msg
        if not insert_res(gc.query(sparql_friendsnum)):
            msg['status'] = '-1'
            msg['msg'] = '关注数错误'
            return msg
        if not insert_res(gc.query(sparql_statusesnum)):
            msg['status'] = '-1'
            msg['msg'] = '微博数错误'
            return msg
        if not insert_res(gc.query(sparql_time)):
            msg['status'] = '-1'
            msg['msg'] = '创建时间错误'
            return msg
        msg['status'] = "1"
        msg['msg'] = "用户注册成功"
        return msg

    def getUserPwd(self, userid):
        sparql = "select ?z where{ <" + str(userid) + "> <password> ?z}"
        res = gc.query(sparql)
        res = query_res(res, "001")
        dict = {}
        if res == False:
            dict['status'] = "-1"
            dict['password'] = "none"
        elif res == None:
            dict['status'] = "0"
            dict['password'] = "none"
        else:
            dict['status'] = "1"
            dict['password'] = res[0]
        return dict

    def getUserName(self, userid):
        sparql = "select ?z where{ <" + str(userid) + "> <name> ?z}"
        res = gc.query(sparql)
        res = query_res(res, "001")
        dict = {}
        if res == False:
            dict['status'] = "-1"
            dict["name"] = "none"
        elif res == None:
            dict['status'] = "0"
            dict["name"] = "none"
        else:
            dict['status'] = "1"
            dict["name"] = res[0]

        sparql = "select ?z where{ <" + str(userid) + "> <gender> ?z}"
        res = gc.query(sparql)
        res = query_res(res, "001")
        if res == False:
            dict['status'] = "-1"
            dict["gender"] = "none"
        elif res == None:
            dict['status'] = "0"
            dict["gender"] = "none"
        else:
            dict['status'] = "1"
            dict["gender"] = res[0]

        return dict

    def getUserID(self, nickName):
        sparql = "select ?x where{?x <name> \"" + str(nickName) + "\".}"
        res = gc.query(sparql)
        res = query_res(res, "100")
        dict = {}
        if res == False:
            dict['status'] = "-1"
            dict["uid"] = "none"
        elif res == None:
            dict['status'] = "0"
            dict["uid"] = "none"
        else:
            dict['status'] = "1"
            dict["uid"] = res[0]
        return dict

    def getUserInfo(self, userid):
        ID = userid
        sparql = "select ?y ?z where{ <" + str(userid) + "> ?y ?z}"
        res = gc.query(sparql)
        res = query_res(res, "011")
        dict = {}
        msg = {}
        if res == False:
            msg['status'] = "-1"
            msg['msg'] = "user query failed"
            msg['content'] = dict
            return msg
        elif res == None:
            msg['status'] = "0"
            msg['msg'] = "No user"
            msg['content'] = dict
            return msg
        else:
            for key in res:
                if key != "userrelation" and key != "send":
                    dict[key] = res[key]
                    if key == 'name':
                        self.name = res[key]
                    elif key == 'location':
                        self.location = res[key]
                    elif key == 'url':
                        self.url = res[key]
                    elif key == 'followersnum':
                        self.followersnum = res[key]
                    elif key == 'created':
                        self.created_time = res[key]
                    elif key == 'gender':
                        self.gender = res[key]
                    elif key == 'friendsnum':
                        self.friendsnum = res[key]
                    elif key == 'statusesnum':
                        self.statusesnum = res[key]
        msg['status'] = "1"
        msg['msg'] = "get user info success"
        dict['id'] = userid
        msg['content'] = dict
        return msg

    def delUserInfo(self, ID):
        # 删除用户本身，不删除关注其的关系

        cuckooClient.delete(ID)
        sparql = "delete where {<" + str(ID) + "> ?y ?z.}"
        msg = {}
        if not delete_res(gc.query(sparql)):
            msg['status'] = "0"
            msg['msg'] = "delete user fail"
        else:
            msg['status'] = "1"
            msg['msg'] = "delete user success"
        return msg

    def setUserInfo(self, info):
        loc_flag = False
        if info.get('ID') != None:
            ID = info.get('ID')
        dict = {}
        if info.get('province') != None or info.get('city') != None:
            location = ""
            loc_flag = True
        if info.get('province') != None:
            location = info.get('province')
        if info.get('city') != None:
            location += " " + info.get('city')
        if loc_flag == True:
            sparql_del = "delete where {<" + ID + "> <location> ?z.}"
            if not delete_res(gc.query(sparql_del)):
                dict['status'] = '-1'
                dict['msg'] = 'location update error'
                return dict
            sparql_add = "insert data {<" + ID + "> <location> \"" + location + "\".}"
            if not insert_res(gc.query(sparql_add)):
                dict['status'] = '-1'
                dict['msg'] = 'location update error'
                return dict

        if info.get('name') != None:
            name = info.get('name')
            sparql_del = "delete where {<" + ID + "> <name> ?z.}"
            if not delete_res(gc.query(sparql_del)):
                dict['status'] = '-1'
                dict['msg'] = 'name update error'
                return dict
            sparql_add = "insert data {<" + ID + "> <name> \"" + name + "\".}"
            if not insert_res(gc.query(sparql_add)):
                dict['status'] = '-1'
                dict['msg'] = 'name update error'
                return dict

        if info.get('gender') != None:
            gender = info.get('gender')
            sparql_del = "delete where {<" + ID + "> <gender> ?z.}"
            if not delete_res(gc.query(sparql_del)):
                dict['status'] = '-1'
                dict['msg'] = 'gender update error'
                return dict
            sparql_add = "insert data {<" + ID + "> <gender> \"" + gender + "\".}"
            if not insert_res(gc.query(sparql_add)):
                dict['status'] = '-1'
                dict['msg'] = 'gender update error'
                return dict

        if info.get('url') != None:
            url = info.get('url')
            sparql_del = "delete where {<" + ID + "> <url> ?z.}"
            if not delete_res(gc.query(sparql_del)):
                dict['status'] = '-1'
                dict['msg'] = 'url update error'
                return dict
            sparql_add = "insert data {<" + ID + "> <url> \"" + url + "\".}"
            if not insert_res(gc.query(sparql_add)):
                dict['status'] = '-1'
                dict['msg'] = 'url update error'
                return dict

        if info.get('password') != None:
            pwd = info.get('password')
            old_pwd = self.getUserPwd(ID)
            msg = {}
            if old_pwd == pwd:
                msg['status'] = '-1'
                msg['msg'] = 'same password'
            else:
                sparql_del = "delete where {<" + ID + "> <password> ?z.}"
                if not delete_res(gc.query(sparql_del)):
                    msg['status'] = '-1'
                    msg['msg'] = 'password update error'
                    return msg
                sparql_add = "insert data {<" + ID + "> <password> \"" + str(
                    pwd) + "\"^^<http://www.w3.org/2001/XMLSchema#integer>.}"
                if not insert_res(gc.query(sparql_add)):
                    msg['status'] = '-1'
                    msg['msg'] = 'password update error'
                    return msg

        dict['status'] = '1'
        dict['msg'] = 'update success'
        return dict
