from myweibo.User import*

u = User()
class Comment:
    def __int__(self):
        self.name = "comment"

    def commentsnum(self, wid, flag):
        msg = {}
        if flag != 1 and flag != -1:
            msg['status'] = "-1"
            msg['msg'] = "comments failed"
            return msg
        sparql_search = "select ?z where {<%s> <commentsnum> ?z.}"%(wid)
        res = query_res(gc.query(sparql_search), "001")
        if not res:
            msg['status'] = "-1"
            msg['msg'] = "comments query failed"
            return msg
        if res == None:
            msg['status'] = "0"
            msg['msg'] = "weibo can't be commented"
            return msg
        num = str(int(res[0]) + flag)
        sparql_del = "delete where {<%s> <commentsnum> ?z.}"%(wid)
        res = delete_res(gc.query(sparql_del))
        if not res:
            msg['status'] = "-1"
            msg['msg'] = "comments delete failed"
            return msg
        sparql_insert = "insert data {<%s> <commentsnum> \"%s\"^^<http://www.w3.org/2001/XMLSchema#integer>.}" % (wid, num)
        res = insert_res(gc.query(sparql_insert))
        if not res:
            msg['status'] = "-1"
            msg['msg'] = "comments insert failed"
            return msg
        msg['status'] = "0"
        msg['msg'] = "comments success"
        return msg

    def postcomment(self, info):
        msg = {}
        time = get_time()
        ID = commentID()
        text = info.get('text')
        uid = info.get('author')
        wid = info.get("weiboId")
        if text == None or uid == None or wid == None:
            msg['status'] = "-1"
            msg['msg'] = "few elements"
            msg['ID'] = str(ID)
            return msg
        user_res = u.getUserName(uid)
        if user_res['status'] != "1":
            msg['status'] = "-1"
            msg['msg'] = "get authors fail"
            msg['ID'] = str(ID)
            return msg
        name = user_res['name']
        sparql_add1 = "insert data {<%s> <comment> <%s>.}"%(uid, ID)
        sparql_add2 = "insert data {<%s> <posttime> \"%s\".}"%(ID, time)
        sparql_add3 = "insert data {<%s> <content> \"%s\".}"%(ID, text)
        sparql_add4 = "insert data {<%s> <belong> <%s>.}"%(ID, wid)
        add_res1 = insert_res(gc.query(sparql_add1))
        add_res2 = insert_res(gc.query(sparql_add2))
        add_res3 = insert_res(gc.query(sparql_add3))
        add_res4 = insert_res(gc.query(sparql_add4))
        if not add_res1 or not add_res2 or not add_res3 or not add_res4:
            msg['status'] = "-1"
            msg['msg'] = "comment fail"
            msg['ID'] = str(ID)
            return msg
        self.commentsnum(wid, 1)
        msg['status'] = "1"
        msg['msg'] = "comment success"
        msg['ID'] = str(ID)
        return msg

    def getallcomment(self, wid):
        msg = {}
        empty = []
        comments = []
        sparql = "select ?x where{?x <belong> <%s>.}"%(str(wid))
        res = query_res(gc.query(sparql), "100")
        if not res or res is None:
            msg['status'] = "-1"
            msg['msg'] = "get comment fail"
            msg['comments'] = empty
            return msg
        for i in range(len(res)):
            comment = self.getcomment(res[i])
            if comment['status'] != "1":
                msg['status'] = "-1"
                msg['msg'] = "get comment fail"
                msg['comments'] = comments
                continue
            comment = comment['comment']
            comments.append(comment)
        msg['status'] = "1"
        msg['msg'] = "get comment success"
        msg['comments'] = comments
        return msg

    def getcomment(self, cid):
        sparql = "select ?y ?z where{<%s> ?y ?z.}"%(str(cid))
        empty = {}
        msg = {}
        comment = {}
        res = query_res(gc.query(sparql), "011")
        if not res or res is None:
            msg['status'] = "-1"
            msg['msg'] = "get comment fail"
            msg['comment'] = empty
            return msg
        comment['content'] = res['content']
        comment['createTime'] = res['posttime']
        sparql_user = "select ?x where{?x <comment> <%s>.}"%(str(cid))
        res = query_res(gc.query(sparql_user), "100")
        if not res or res is None:
            msg['status'] = "-1"
            msg['msg'] = "get comment fail"
            msg['comment'] = empty
            return msg
        uid = res[0]
        name = u.getUserName(uid)
        if name['status'] != "1":
            msg['status'] = "-1"
            msg['msg'] = "get comment fail"
            msg['comment'] = empty
            return msg
        author = {}
        author['username'] = name['name']
        author['userid'] = uid
        comment['author'] = author
        msg['status'] = "1"
        msg['msg'] = "get comment success"
        msg['comment'] = comment
        return msg

    def delcomment(self, cid, wid):
        msg = {}
        sparql = "delete where{<%s> ?x ?y.}"%(str(cid))
        if not delete_res(gc.query(sparql)):
            msg['status'] = "-1"
            msg['msg'] = "delete comment failed"
            return msg
        sparql1 = "delete where{?x ?y <%s>.}" % (str(cid))
        if not delete_res(gc.query(sparql1)):
            msg['status'] = "-1"
            msg['msg'] = "delete comment failed"
            return msg
        if not self.commentsnum(wid, -1):
            msg['status'] = "-1"
            msg['msg'] = "delete comment failed"
            return msg
        msg['status'] = "1"
        msg['msg'] = "delete comment success"
        return msg

if __name__ == '__main__':
    c = Comment()
    info = {
        'text': '路过，经验+6',
        'author': '1262065265',
        'weiboId': '3707897701312794'
    }
    print(c.getallcomment("3707897701312794"))