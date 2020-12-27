from myweibo.User import *
from myweibo.weibo import *
from myweibo.CuckooClient import CuckooFilter
import logging
weiboClient = Weibo()
client = CuckooFilter()

class Action:
    def setattitude(self, wID, flag):
        if flag != 1 and flag != -1:
            return False
        sparql_search = "select ?z where {<%s> <attitudesnum> ?z.}" % str(wID)
        res = query_res(gc.query(sparql_search), "001")
        if not res or res == None:
            return False
        num = str(int(res[0]) + flag)
        sparql_del = "delete where {<%s> <attitudesnum> ?z.}" % (wID)
        res = delete_res(gc.query(sparql_del))
        if not res:
            return False
        sparql_insert = "insert data {<%s> <attitudesnum> \"%s\"^^<http://www.w3.org/2001/XMLSchema#integer>.}" % (
            wID, num)
        res = insert_res(gc.query(sparql_insert))
        if not res:
            return False
        return True

    def attitudes(self, info):
        logging.info("info:"+str(info))
        msg = {}
        if info.get('wid') is None:
            msg['status'] = "-1"
            msg['msg'] = "attitude failed"
            return msg
        wid = info['wid']
        # TODO:cancel like
        flag = int(info['flag'])
        res = self.setattitude(wid, flag)
        if not res:
            msg['status'] = "-1"
            msg['msg'] = "weibo liked failed"
            return msg
        else:
            msg['status'] = "0"
            msg['msg'] = "attitude success"
            return msg

    def followers(self, ID, flag):
        if flag != 1 and flag != -1:
            return False
        sparql_search = "select ?z where {<%s> <followersnum> ?z.}" % str(ID)
        res = query_res(gc.query(sparql_search), "001")
        if not res or res == None:
            return False
        num = str(int(res[0]) + flag)
        sparql_del = "delete where {<%s> <followersnum> ?z.}" % (ID)
        res = delete_res(gc.query(sparql_del))
        if not res:
            return False
        sparql_insert = "insert data {<%s> <followersnum> \"%s\"^^<http://www.w3.org/2001/XMLSchema#integer>.}" % (
        str(ID), num)
        res = insert_res(gc.query(sparql_insert))
        if not res:
            return False
        return True

    def setlike(self, uID, wid):
        sparql_insert = "insert data {<%s> <likes> <%s>.}" % (str(uID), str(wid))
        res = insert_res(gc.query(sparql_insert))
        if not res:
            return False
        return True

    def dislike(self, uID, wID):
        sparql_ask = "ask {<%s> <likes> <%s>.}" % (str(uID), str(wID))
        if not ask_res(gc.query(sparql_ask)):
            return False
        sparql_delete = "delete data {<%s> <likes> <%s>.}" % (str(uID), str(wID))
        res = insert_res(gc.query(sparql_delete))
        if not res:
            return False
        return True

    def friends(self, ID, flag):
        if flag != 1 and flag != -1:
            return False
        sparql_search = "select ?z where {<%s> <friendsnum> ?z.}" % str(ID)
        res = query_res(gc.query(sparql_search), "001")
        if not res or res == None:
            return False
        num = str(int(res[0]) + flag)
        sparql_del = "delete where {<%s> <friendsnum> ?z.}" % (ID)
        res = delete_res(gc.query(sparql_del))
        if not res:
            return False
        sparql_insert = "insert data {<%s> <friendsnum> \"%s\"^^<http://www.w3.org/2001/XMLSchema#integer>.}" % (
        ID, num)
        res = insert_res(gc.query(sparql_insert))
        if not res:
            return False
        return True

    def follow(self, info):
        msg = {}
        if info.get("lid") == None or info.get("rid") == None:
            msg['status'] = "-1"
            msg['msg'] = "follow relation error"
            return msg
        lid = info.get("lid")
        rid = info.get("rid")
        if lid == rid:
            msg['status'] = "-1"
            msg['msg'] = "can not follow yourself"
            return msg
        # 是否已经关注
        check = self.is_follower(info)
        if check['status'] == "1":
            msg['status'] = "0"
            msg['msg'] = "follow already"
            return msg
        sparql_add = "insert data{ <%s> <careFor> <%s> .}" % (lid, rid)
        res = gc.query(sparql_add)
        if not insert_res(res):
            msg['status'] = "-1"
            msg['msg'] = "follow failed"
            return msg
        else:
            if self.followers(rid, 1) and self.friends(lid, 1):
                msg['status'] = "1"
                msg['msg'] = "follow success"
                return msg
            else:
                msg['status'] = "0"
                msg['msg'] = "follow failer"
                return msg

    def unfollow(self, info):
        msg = {}
        if info.get("lid") == None or info.get("rid") == None:
            msg['status'] = "-1"
            msg['msg'] = "follow relation error"
            return msg
        lid = info.get("lid")
        rid = info.get("rid")
        # 如果不是粉丝
        check = self.is_follower(info)
        if check['status'] == "0":
            msg['status'] = "0"
            msg['msg'] = "already not follower"
            return msg
        sparql_del = "delete data{ <%s> <careFor> <%s> .}" % (lid, rid)
        res = gc.query(sparql_del)
        if not insert_res(res):
            msg['status'] = "-1"
            msg['msg'] = "unfollow failed"
            return msg
        else:
            if self.followers(rid, -1) and self.friends(lid, -1):
                msg['status'] = "1"
                msg['msg'] = "unfollow success"
                return msg
            else:
                msg['status'] = "-1"
                msg['msg'] = "unfollow failed"
                return msg

    def getfollowerlist(self, uid, limit="50"):
        '''
        :param info:
        :return:dict{status, msg, userlist{dict{id:uid, name:uname}}}
        '''
        msg = {}
        u = User()
        userlist = []
        sparql_search = "select ?x where{?x <careFor> <%s>}limit %s" % (str(uid), str(limit))
        res = query_res(gc.query(sparql_search), "100")
        if not res:
            msg['status'] = "-1"
            msg['msg'] = "query followers failed"
            msg['num'] = len(userlist)
            msg['list'] = userlist
            return msg
        elif res is None:
            msg['status'] = "0"
            msg['msg'] = "No followers"
            msg['num'] = len(userlist)
            msg['list'] = userlist

            return msg
        else:
            for i in range(len(res)):
                dict = {}
                info = u.getUserName(res[i])
                if info['status'] != "1":
                    msg['status'] = "0"
                    msg['msg'] = "get partial followers"
                    msg['num'] = len(userlist)
                    msg['list'] = userlist
                    continue
                dict['name'] = info['name']
                dict['id'] = res[i]
                userlist.append(dict)
            msg['status'] = "1"
            msg['msg'] = "get followers success"
            msg['num'] = len(userlist)
            msg['list'] = userlist
            return msg

    def getfriendslist(self, uid, limit="50"):
        msg = {}
        u = User()
        userlist = []
        sparql_search = "select ?z where{<%s> <careFor> ?z} limit %s" % (str(uid), str(limit))
        res = query_res(gc.query(sparql_search), "001")
        if not res:
            msg['status'] = "-1"
            msg['msg'] = "query friends failed"
            msg['num'] = len(userlist)
            msg['list'] = userlist
            return msg
        elif res is None:
            msg['status'] = "0"
            msg['msg'] = "No friends"
            msg['num'] = len(userlist)
            msg['list'] = userlist
            return msg
        else:
            for i in range(len(res)):
                dict = {}
                info = u.getUserName(res[i])
                if info['status'] != "1":
                    msg['status'] = "0"
                    msg['msg'] = "get partial friends"
                    msg['num'] = len(userlist)
                    msg['list'] = userlist
                    continue
                dict['name'] = info['name']
                dict['id'] = res[i]
                userlist.append(dict)
            msg['status'] = "1"
            msg['msg'] = "get friends success"
            msg['num'] = len(userlist)
            msg['list'] = userlist
            return msg

    def is_follower(self, info):
        '''
        :param info:
        检查lid是否是rid的粉丝
        :return:
        '''
        msg = {}
        if info.get('lid') == None or info.get('rid') == None:
            msg['status'] = "0"
            msg['msg'] = "user id error"
            return msg
        lid = str(info.get('lid'))
        rid = str(info.get('rid'))
        sparql_ask = "ask {<%s> <careFor> <%s>.}" % (lid, rid)

        if not ask_res(gc.query(sparql_ask)):
            msg['status'] = "0"
            msg['msg'] = "not follow"
            return msg
        else:
            msg['status'] = "1"
            msg['msg'] = "following"
            return msg

    # 查看fid是否是uid的关注
    def is_friend(self, info):
        msg = {}
        if info.get('lid') == None or info.get('rid') == None:
            msg['status'] = "0"
            msg['msg'] = "user id error"
            return msg
        lid = str(info.get('lid'))
        rid = str(info.get('rid'))
        info['lid'] = rid
        info['rid'] = lid
        # 右边是左边的粉丝，等于左边是右边的关注
        return self.is_follower(info)

    def commonfriend(self, info):
        msg = {}
        commonlist = []
        if info.get('uid') == None or info.get('fid') == None:
            msg['status'] = "-1"
            msg["list"] = commonlist
            msg['msg'] = "user id error"
            return msg
        uid = info.get('uid')
        fid = info.get('fid')
        sparql = "select ?z where{<%s> <careFor> ?z. <%s> <careFor> ?z.}" % (str(uid), str(fid))
        res = query_res(gc.query(sparql), "001")
        if not res or res is None:
            msg['status'] = "0"
            msg["num"] = 0
            msg['msg'] = "no common friends"
            return msg
        commonlist = res
        msg['status'] = "1"
        msg["num"] = len(commonlist)
        msg['msg'] = "get common friends list success"
        return msg

    def getfriendsweibo(self, ID, limit="50"):
        spraql = "select ?z where { <%s> <careFor> ?x. ?z <uid> ?x.} limit %s" % (str(ID), (limit))
        weibolist = query_res(gc.query(spraql), "001")
        if weibolist is None or not weibolist:
            weibolist = []
        weibos = []
        msg = {}
        for i in range(len(weibolist)):
            weibo_res = weiboClient.getWeibo(weibolist[i], ID)
            if weibo_res['status'] != "1":
                msg['status'] = '0'
                msg['msg'] = "get all weibos fail"
                msg['num'] = str(len(weibos))
                msg['weibos'] = weibos
                continue
            weibos.append(weibo_res['weibo'])
        # sort
        # weibos = sorted(weibos, key=lambda d: datetime.datetime.strptime(d["createTime"], "%Y-%m-%d %H:%M:%S"), reverse=True)
        msg['status'] = '1'
        msg['msg'] = "get all weibos success"
        msg['num'] = str(len(weibos))
        msg['weibos'] = weibos
        return msg


if __name__ == '__main__':
    act = Action()
    info = {
        'rid': "13120329926",
        'lid': "1771731262"
    }
