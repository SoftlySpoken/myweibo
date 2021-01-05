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

    #两
    def users_recom(self, ID, limit = 25):
        msg = {}
        users = []
        dic_follow = {}
        dic_topic = {}
        sparql = "select distinct ?y ?z where \
            {<%s> <careFor> ?z. ?z <careFor> ?y. ?y <followersnum> ?fn. } \
            order by desc(?fn) limit %s" % (str(ID), str(2 * limit))
        res = query_res(gc.query(sparql), "011")
        if res != False and res != None:
            sampled_keys = sample(list(res), min(limit, len(res)))
            for i in range(len(sampled_keys)):
                if sampled_keys[i] != ID:
                    dic_follow[sampled_keys[i]] = res[sampled_keys[i]]

        sparql = "select distinct ?y ?z where \
            { ?w1 <uid> <%s>. ?w1 <topic> ?z. ?w2 <uid> ?y. ?w2 <topic> ?z. \
            ?y <followersnum> ?fn. } \
            order by desc(?fn) limit %s" % (str(ID), str(2 * limit))
        res = query_res(gc.query(sparql), "011")
        if res != False and res != None:
            sampled_keys = sample(list(res), min(limit, len(res)))
            for i in range(len(sampled_keys)):
                if sampled_keys[i] != ID and sampled_keys[i] not in dic_follow:
                    dic_topic[sampled_keys[i]] = res[sampled_keys[i]]
        
        print(dic_follow)
        print(dic_topic)
        if len(dic_follow) + len(dic_topic) == 0 :
            msg['status'] = "0"
            msg['msg'] = "No user recommend"
            msg['num'] = 0
            msg['users_follow'] = {}
            msg['users_topic'] = {}
            print(msg)
            return msg
        else:
            msg['status'] = "1"
            msg['msg'] = "get recommended users"
            msg['num'] = str(len(dic_follow) + len(dic_topic))
            msg['users_follow'] = dic_follow
            msg['users_topic'] = dic_topic
            return msg

    def peopleYouMayKnow(self, ID, limit = 50):
        # 寻找二度节点
        sparql = "select distinct ?x where\
        {<%s> <careFor> ?z. ?x <careFor> ?z. ?x <followersnum> ?fn. minus {<%s> <careFor> ?x}} \
        order by desc(?fn) limit %s" % (str(ID), str(ID), str(2 * limit))
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

        sorted_tuples = sorted(dic.items(), key=lambda item : item[1], reverse=True)
        dic = {k : v for k, v in sorted_tuples}

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
                    FILTER(?y > \"600\"^^<http://www.w3.org/2001/XMLSchema#integer>) \
                    FILTER(?z > \"500\"^^<http://www.w3.org/2001/XMLSchema#integer>) \
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

