from myweibo.Action import*
from myweibo.User import*

u = User()
a = Action()
class Recommender:
    def  __init__(self):
        self.name = "recommender"

    def sort_by_factor(self, res):
        dict = {}
        for i in range(len(res)):
            fans = int(res[i]['y']['value'])
            friends = int(res[i]['z']['value'])
            if friends == 0:
                factor = float('inf')
            else:
                factor = fans/friends
            dict[res[i]['x']['value']] = factor
            sorted(dict, key=dict.get)
        user = list(dict)
        user.reverse()
        return user

    def popularusers(self, limit = "50"):
        msg = {}
        users = []
        sparql = "select ?x ?y ?z where{ ?x <followersnum> ?y.\
                    ?x <friendsnum> ?z. \
                    FILTER(?y >\"500000\"^^<http://www.w3.org/2001/XMLSchema#integer>) \
                    FILTER(?z <\"200\"^^<http://www.w3.org/2001/XMLSchema#integer>) "
        res = query_res(gc.query(sparql), "111")
        if res == False:
            msg['status'] = "1"
            msg['msg'] = "popularuser recommend error"
            msg['num'] = str(len(users))
            msg['users'] = users
            return msg
        if res == None :
            msg['status'] = "0"
            msg['msg'] = "No popularuser recommend"
            msg['num'] = str(len(users))
            msg['users'] = users
            return msg
        else:
            msg['status'] = "1"
            msg['msg'] = "get recommended popular users"
            users = self.sort_by_factor(res)
            msg['num'] = str(len(users))
            msg['users'] = users
            return msg

    #两跳
    def users_recom(self, ID, limit = "50"):
        msg = {}
        users = []
        sparql = "select ?z where{ <%s> <careFor> ?y. ?y <careFor> ?z.} %s"%(str(ID), str(limit))
        res = query_res(gc.query(sparql), "001")
        if res == False:
            msg['status'] = "1"
            msg['msg'] = "user recommend error"
            msg['num'] = str(len(users))
            msg['users'] = users
            return msg
        if res == None :
            msg['status'] = "0"
            msg['msg'] = "No user recommend"
            msg['num'] = str(len(users))
            msg['users'] = users
            return msg
        else:
            msg['status'] = "1"
            msg['msg'] = "get recommended users"
            msg['num'] = str(len(users))
            users = res
            msg['users'] = users
            return msg

    def new_recom(self, ID, limit = 50):
        sparql = "select ?x {<%s> <careFor> ?z. ?x <careFor> ?z.}" % (str(ID))
        res = query_res(gc.query(sparql), "100")
        msg = {}
        users = []
        if res is None or not res:
            msg['status'] = "-1"
            msg['msg'] = "no users"
            msg['list'] = []
            return msg
        users = res
        users = sample(users, min(limit, len(users)))
        dic = {}
        for i in range(len(users)):
            info = {}
            info['uid'] = ID
            info['fid'] = users[i]
            dic[users[i]] = int(a.commonfriend(info)['num'])

        sorted(dic, key=dic.get)

        msg['status'] = "1"
        msg['msg'] = "get recommending user success"
        msg['list'] = dic
        return msg

    #共同关注
    def users_recom1(self, ID, limit = 50):
        msg = {}
        ulist = []
        res = a.getfriendslist(ID, 20)
        if res['status'] != "1":
            msg['status'] = "-1"
            msg['msg'] = "get recommending user fail"
            msg['list'] = ulist
            return msg
        ulist = res['list']
        users = set()
        for i in range(len(ulist)):
            res = a.getfollowerlist(ulist[i]['id'], 5)
            if res['status'] == "1":
                tlist = res['list']
                for j in range(len(tlist)):
                    users.add(tlist[j]['id'])
        dic = {}
        for user in users:
            info = {}
            info['uid'] = ID
            info['fid'] = user
            dic[user] = int(a.commonfriend(info)['num'])
        dic = sorted(dic.items(), key=lambda d: d[1], reverse=True)
        msg['status'] = "1"
        msg['msg'] = "get recommending user success"
        msg['list'] = dic
        return msg

    def popularweibos(self, limit = 20):
        msg = {}
        weibos = []
        sparql = \
            "select ?x \
             where{ ?x <repostsnum> ?y.\
                    ?x <commentsnum> ?z. ?x <attitudesnum> ?p. \
                    FILTER(?y > \"500\"^^<http://www.w3.org/2001/XMLSchema#integer>) \
                    FILTER(?z > \"300\"^^<http://www.w3.org/2001/XMLSchema#integer>) \
                    FILTER(?p > \"1000\"^^<http://www.w3.org/2001/XMLSchema#integer>) } "
        res = query_res(gc.query(sparql), "100")
        if res == False:
            msg['status'] = "1"
            msg['msg'] = "popularuser recommend error"
            msg['num'] = str(len(weibos))
            msg['weibos'] = weibos
            return msg
        if res == None:
            msg['status'] = "0"
            msg['msg'] = "No popularuser recommend"
            msg['num'] = str(len(weibos))
            msg['weibos'] = weibos
            return msg
        else:
            msg['status'] = "1"
            msg['msg'] = "get recommended popular weibos"
            weibos = res
            weibos = sample(weibos, limit)
            msg['num'] = str(len(weibos))
            msg['weibos'] = weibos
            return msg


if __name__ == '__main__':
    r = Recommender()
    print(r.new_recom("1262065265"))
