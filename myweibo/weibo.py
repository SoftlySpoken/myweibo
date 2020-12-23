from myweibo.User import *

# gc = Connection()

u = User()


class Weibo:
    def __init__(self):
        self.ID = "0"
        self.text = ""
        self.author = ""
        self.authorID = "0"
        self.time = ""
        self.commentsnum = "0"
        self.attitudesnum = "0"
        self.repostsnum = "0"
        self.topic = ""

    def getAuthor(self, ID):
        msg = {}
        author_dict = {}
        sparql_uid = "select ?x {<" + "%s> <uid> ?x .}" % str(ID)
        res = query_res(gc.query(sparql_uid), "100")
        if not res:
            msg['status'] = "-1"
            msg['msg'] = "author query failed"
            msg['author'] = author_dict
            return msg
        if res is None:
            msg['status'] = "0"
            msg['msg'] = "no author"
            msg['author'] = author_dict
            return msg
        name = u.getUserName(res[0])
        if name['status'] != "1":
            msg['status'] = "-1"
            msg['msg'] = "author query failed"
            msg['author'] = author_dict
            return msg
        author_dict['userid'] = res[0]
        author_dict['username'] = name['name']
        msg['status'] = "1"
        msg['msg'] = "get author"
        msg['author'] = author_dict
        return msg

    def getWeibo(self, wID, uid):
        msg = {}
        # find author ID
        wID = str(wID)
        uid = str(uid)
        empty = {}
        weibo = {}
        res = self.getSourceWeibo(wID)
        if res['status'] != "1":
            msg['status'] = "-1"
            msg['msg'] = "get weibo error"
            msg['weibo'] = empty
            return msg
        res = res['weibo']
        author_dict = res['author']
        weibo['weiboId'] = wID
        weibo['author'] = author_dict
        # 处理转发
        trans = self.gettrans(wID)
        sourceID = trans['source']
        if trans['num'] == "0":  # 不为转发
            weibo["hastrans"] = 0
        else:
            weibo["hastrans"] = 1
            weibo["trans"] = trans['list']

        if uid == author_dict['userid']:
            weibo["isOwn"] = 1
        else:
            weibo["isOwn"] = 0
        # 提取源微博信息
        source_res = self.getSourceWeibo(sourceID)
        if source_res['status'] != "1":
            msg['status'] = "-1"
            msg['msg'] = "get weibo error"
            msg['weibo'] = empty
            return msg
        source_res = source_res['weibo']
        weibo['topic'] = "#" + source_res['topic'] + "#"
        if source_res.get('text') is not None:
            weibo['content'] = source_res['text']
        else:
            weibo['content'] = "微博因非法内容不存在"
        # 继续返回本微博信息
        weibo['createTime'] = res['date']
        weibo['likeNum'] = res['attitudesnum']
        weibo['commentNum'] = res['commentsnum']
        weibo['transNum'] = res['repostsnum']
        weibo['isLike'] = self.checkLike(uid, wID)
        msg['status'] = "1"
        msg['msg'] = "get weibo success"
        msg['weibo'] = weibo
        return msg

    def getSourceWeibo(self, wID):
        msg = {}
        empty = {}
        # get other info
        sparql_get = "select ?y ?z where{<" + "%s> ?y ?z}" % str(wID)
        res = query_res(gc.query(sparql_get), "011")
        if not res:
            msg['status'] = "-1"
            msg['msg'] = "weibo query failed"
            msg['weibo'] = empty
            return msg
        if res is None:
            msg['status'] = "0"
            msg['msg'] = "no weibo"
            msg['weibo'] = empty
            return msg
        author_res = self.getAuthor(wID)
        if author_res['status'] != "1":
            msg['status'] = "-1"
            msg['msg'] = "author query failed"
            msg['weibo'] = empty
            return msg
        res['author'] = author_res['author']
        msg['status'] = "1"
        msg['msg'] = "get weibo"
        msg['weibo'] = res
        return msg

    def checkLike(self, uID, wID):
        sparql_ask = "ask {<%s> <likes> <%s>.}" % (uID, wID)

        if not ask_res(gc.query(sparql_ask)):
            return 0
        else:
            return 1

    def gettrans(self, ID):
        translist = []
        msg = {}
        while True:
            sparql_search = "select ?z {<" + "%s> <refer> ?z.}" % (ID)
            res = query_res(gc.query(sparql_search), "001")
            if not res or res is None:
                msg['num'] = str(len(translist))
                msg["list"] = translist
                msg['source'] = ID
                return msg
            else:
                weibo_res = self.getSourceWeibo(ID)  # 下一级转发
                if weibo_res['status'] != "1":
                    msg['num'] = str(len(translist))
                    msg["list"] = translist
                    msg['source'] = ID
                    return msg
                else:
                    ID = res[0]
                    dict = {}
                    dict['content'] = weibo_res['weibo']['text']
                    dict['username'] = weibo_res['weibo']['author']['username']
                    dict['userid'] = weibo_res['weibo']['author']['userid']
                    translist.append(dict)

    def getUserWeibo(self, uid, ID, limit=50):
        weibos = []
        msg = {}
        sparql_search = "select ?z where {?z <uid> <%s>}" % (str(uid))
        res = query_res(gc.query(sparql_search), "001")
        if res == False:
            msg['status'] = "-1"
            msg['msg'] = "get user's weibo failed"
            msg['weibos'] = weibos
            return msg
        elif res is None:
            msg['status'] = "0"
            msg['msg'] = "user has no weibo"
            msg['weibos'] = weibos
            return msg
        for i in range(len(res)):
            weiboID = res[i]
            res1 = self.getWeibo(weiboID, ID)
            if res1['status'] != "1":
                msg['status'] = "-1"
                msg['msg'] = "get user's partial weibo"
                msg['weibos'] = weibos
                continue
            dit = res1['weibo']
            weibos.append(dit)
        weibos = sorted(weibos, key=lambda d: datetime.datetime.strptime(d["createTime"], "%Y-%m-%d_%H:%M:%S"),
                        reverse=True)
        if len(weibos) > limit:
            weibos = weibos[:limit]
        msg['status'] = "1"
        msg['msg'] = "get user's weibo success"
        msg['num'] = len(weibos)
        msg['weibos'] = weibos
        return msg

    def weibonum(self, ID, flag):
        if flag != 1 and flag != -1:
            return False
        sparql_search = "select ?z {<%s> <statusesnum> ?z.}" % str(ID)
        res = query_res(gc.query(sparql_search), "001")
        if not res or res is None:
            return False
        num = str(int(res[0]) + flag)
        sparql_del = "delete where {<%s> <statusesnum> ?z.}" % str(ID)
        res = delete_res(gc.query(sparql_del))
        if not res:
            return False
        sparql_add = "insert data{<%s> <statusesnum> \"%s\"^^<http://www.w3.org/2001/XMLSchema#integer>.}" % (
            str(ID), num)
        res = insert_res(gc.query(sparql_add))
        if not res:
            return False
        return True

    def postNewWeibo(self, dict):
        msg = {}
        date = get_time()
        ID = weiboID()

        sparql_date = "insert data {<%s> <date> \"%s\"}" % (ID, date)
        if not insert_res(gc.query(sparql_date)):
            msg['status'] = "-1"
            msg['ID'] = ID
            msg['msg'] = "post weibo <%s> failed" % ID
            return msg
        # author
        if dict.get('uid') != None:
            authorID = dict.get('uid')
            sparql = "insert data {<%s> <uid> <%s>.}" % (ID, authorID)
            if not insert_res(gc.query(sparql)):
                msg['status'] = -1
                msg['ID'] = ID
                msg['msg'] = "post weibo <%s> failed" % ID
                return msg
        else:
            msg['status'] = "-1"
            msg['ID'] = ID
            msg['msg'] = "post weibo <%s> failed" % ID
            return msg

        # statuesnum
        if not self.weibonum(authorID, 1):
            msg['status'] = "-1"
            msg['ID'] = ID
            msg['msg'] = "post weibo <%s> failed" % ID
            return msg

        # text
        if dict.get('text') != None:
            text = dict.get('text')
        else:
            text = "我爱海量图"
        sparql_text = "insert data {<%s> <text> \"%s\".}" % (ID, text)
        if not insert_res(gc.query(sparql_text)):
            msg['status'] = "-1"
            msg['ID'] = ID
            msg['msg'] = "post weibo <%s> failed" % ID
            return msg

        # topic
        if dict.get('topic') != None:
            topic = dict.get('topic')
            print("TOPIC: " + topic)
            sparql_topic = "insert data {<%s> <topic> \"%s\".}" % (ID, topic)
            if not insert_res(gc.query(sparql_topic)):
                msg['status'] = "-1"
                msg['ID'] = ID
                msg['msg'] = "post weibo <%s> failed" % ID
                return msg

        # attitudesnum
        if dict.get('attitudesnum') != None:
            attitudesnum = dict.get("attitudesnum")
        else:
            attitudesnum = "0"
        sparql_num = "insert data {<%s> <attitudesnum> \"%s\"^^<http://www.w3.org/2001/XMLSchema#integer>.}" % (
            ID, attitudesnum)
        if not insert_res(gc.query(sparql_num)):
            msg['status'] = "-1"
            msg['ID'] = ID
            msg['msg'] = "post weibo <%s> failed" % ID
            return msg

        # commentsnum
        if dict.get('commentsnum') != None:
            commentsnum = dict.get("commentsnum")
        else:
            commentsnum = "0"
        sparql_num = "insert data {<%s> <commentsnum> \"%s\"^^<http://www.w3.org/2001/XMLSchema#integer>.}" % (
            ID, commentsnum)
        if not insert_res(gc.query(sparql_num)):
            msg['status'] = "-1"
            msg['ID'] = ID
            msg['msg'] = "post weibo <%s> failed" % ID
            return msg

        # repostsnum
        if dict.get('repostsnum') != None:
            repostsnum = dict.get("repostsnum")
        else:
            repostsnum = "0"
        sparql_num = "insert data {<%s> <repostsnum> \"%s\"^^<http://www.w3.org/2001/XMLSchema#integer>.}" % (
            ID, repostsnum)
        if not insert_res(gc.query(sparql_num)):
            msg['status'] = "-1"
            msg['ID'] = ID
            msg['msg'] = "post weibo <%s> failed" % ID
            return msg

        # success
        msg['status'] = "1"
        msg['ID'] = ID
        msg['msg'] = "post weibo <%s> success" % ID
        return msg

    def delweibo(self, ID):
        # 删除微博信息
        sparql = "delete where{<%s> ?y ?z.}" % str(ID)
        msg = {}
        if not delete_res(gc.query(sparql)):
            msg['status'] = "-1"
            msg['msg'] = "delete weibo failed"
            return msg
        # 删除用户发送记录和微博数
        author = self.getAuthor(ID)
        if author['status'] != "1":
            msg['status'] = "-1"
            msg['msg'] = "delete weibo failed"
            return msg
        else:
            author = author['author']
            uid = author['userid']
        sparql1 = "delete where{ ?x ?y <%s>.}" % str(ID)
        if not delete_res(gc.query(sparql1)):
            msg['status'] = "-1"
            msg['msg'] = "delete weibo failed"
            return msg
        if not self.weibonum(uid, -1):
            msg['status'] = "-1"
            msg['msg'] = "delete weibo failed"
            return msg
        msg['status'] = "1"
        msg['msg'] = "delete weibo success"
        return msg

    def repostweibo(self, info):
        msg = {}
        # 判断uid和wid是否合法
        if info.get('uid') is None:
            msg['status'] = "-1"
            msg['msg'] = "repost error"
            return msg
        uid = info.get('uid')
        if info.get('wid') is None:
            msg['status'] = "-1"
            msg['msg'] = "repost error"
            return msg
        wid = info.get('wid')
        # 设定转发文字
        if info.get('text') == None:
            text = "转发微博"
        else:
            text = info.get('text')
        # 更新转发微博转发数
        weibo = self.getWeibo(wid, uid)['weibo']
        num = str(int(weibo['transNum']) + 1)
        sparql_inc = "delete where {<%s> <repostsnum> ?x.}" % (wid)
        if not delete_res(gc.query(sparql_inc)):
            msg['status'] = "-1"
            msg['msg'] = "repost error"
            return msg
        sparql_inc1 = "insert data {<%s> <repostsnum> \"%s\"^^<http://www.w3.org/2001/XMLSchema#integer>.}" % (wid, num)
        if not insert_res(gc.query(sparql_inc1)):
            msg['status'] = "-1"
            msg['msg'] = "repost error"
            return msg
        # 重新包装info，修改作者 作者ID 内容
        info['topic'] = weibo['topic']
        info['uid'] = uid
        info['text'] = text
        # 发布新微博
        res = self.postNewWeibo(info)
        if res['status'] != "1":
            msg['status'] = "-1"
            msg['msg'] = "repost error"
            return msg
        # 添加微博转发关系
        sparql_add = "insert data {<%s> <refer> <%s>.}" % (res['ID'], wid)
        if not insert_res(gc.query(sparql_add)):
            msg['status'] = "-1"
            msg['msg'] = "repost error"
            return msg
        msg['status'] = "1"
        msg['ID'] = res['ID']
        msg['msg'] = "repost success"
        return msg


def main():
    w = Weibo()
    dict = {
        'uid': "13120329926",
        'text': "欢迎回来",
        'topic': "unknown"
    }
    repost = {
        'uid': "13120329926",
        "wid": "4841720408873664"
    }
    repost1 = {
        'uid': "13120329926",
        "wid": "4084239431236597",
        'text': "来了来了",
    }
    # print(w.postNewWeibo(dict))
    # print(w.repostweibo(repost))
    # print(w.getWeibo("4692841009976180", "13120329926"))
    print(w.getUserWeibo("123456", "13120329926"))
    print(w.delweibo("4747870210874902"))


if __name__ == '__main__':
    main()
