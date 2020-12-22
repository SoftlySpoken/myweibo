# encoding=utf-8
import re

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from myweibo.User import *
from myweibo.Recommend import *
from myweibo.commets import *

commenting = Comment()
user = User()
recommender = Recommender()
action = Action()


def logincheck(request):
    if "userid" in request.session.keys():
        return 1
    return 0


@csrf_exempt
def hello(request):
    return HttpResponse("Hello world ! ")


@csrf_exempt
def index(request):
    d = {}
    d["greeting"] = "欢迎来到MyWeibo！"
    return render(request, "index.html", d)


@csrf_exempt
def LoginPage(request):
    return render(request, "Login.html")


@csrf_exempt
def transfer(request):
    '''
        查看某条微博的评论详情和转发微博
    '''
    uid = request.session["userid"]
    username = request.session["username"]
    print("        def transfer(request):")
    print(request)
    print(" " * 30)
    if request.method == 'POST':
        wid = request.POST.get('weiboid')  # 获取id
    else:
        wid = request.GET.get("weiboid")
    print("wid:", wid)
    wid = str(wid)
    uid = str(uid)
    d = {}
    # 下面是生成被转发微博的内容的数据
    weibo = weiboClient.getWeibo(wid, uid)
    if weibo['status'] == "1":
        weibo = weibo['weibo']
    else:
        weibo = {}
    d["weibo"] = weibo

    # 下面生成评论列表的数据
    commentList = commenting.getallcomment(wid)
    if commentList['status'] != "1":
        commentList = []
    else:
        commentList = commentList['comments']
    d["commentList"] = commentList
    d["username"] = request.session["username"]
    return render(request, "transfer.html", d)


@csrf_exempt
def MySpace(request):
    '''
     这个函数用来渲染显示当前用户的关注列表、被关注列表和发过的微博的页面
     
    '''
    uid = request.session['userid']
    name = request.session['username']
    d = {}
    # 下面是生成关注列表的数据格式示例：
    friendList = []
    friends = action.getfriendslist(uid)
    if friends['status'] == "1":
        friends = friends['list']
        for i in range(len(friends)):
            friend = {}
            fid = friends[i]['id']
            friend['userid'] = fid
            friend['username'] = friends[i]['name']
            uinfo = user.getUserInfo(fid)
            if uinfo['status'] != "1":
                continue
            uinfo = uinfo['content']
            friend['fanNum'] = uinfo['followersnum']
            friend['friendNum'] = uinfo['friendsnum']
            friend['weiboNum'] = uinfo['statusesnum']
            friendList.append(friend)
    else:
        friends = []
    d["friendList"] = friendList

    # 下面是生成粉丝列表的数据格式示例,比上面多了个指示是否已经互关的项
    fanList = []
    fans = action.getfollowerlist(uid)
    if fans['status'] != "1":
        fanList = []
    else:
        fans = fans['list']
        for i in range(len(fans)):
            fan = {}
            fid = fans[i]['id']
            fan["userid"] = fid
            fan['username'] = fans[i]['name']
            uinfo = user.getUserInfo(fid)
            if uinfo['status'] != "1":
                continue
            uinfo = uinfo['content']
            fan['fanNum'] = uinfo['followersnum']
            fan['friendNum'] = uinfo['friendsnum']
            fan['weiboNum'] = uinfo['statusesnum']
            info = {}
            info['lid'] = fid
            info['rid'] = uid
            fan['isFriend'] = int(action.is_friend(info)['status'])
            fanList.append(fan)
    d["fanList"] = fanList

    # 下面是生成顶部用户简单信息的数据示例,注意这里一个dict对象就行，不用list
    master = {
        "userid": str(uid),
        "username": str(name),
        "fanNum": "Nan",
        "weiboNum": "Nan",
        "friendNum": "Nan"
    }
    myinfo = user.getUserInfo(uid)
    if myinfo['status'] == "1":
        myinfo = myinfo['content']
        master["fanNum"] = myinfo['followersnum']
        master['friendNum'] = myinfo['friendsnum']
        master['weiboNum'] = myinfo['statusesnum']
    d["master"] = master

    # 下面是生成用户微博列表的数据示例
    weibolist = []
    myweibos = weiboClient.getUserWeibo(uid, uid)
    if myweibos['status'] != "1":
        weibolist = []
    else:
        weibolist = myweibos['weibos']

    d["weiboList"] = weibolist
    d["username"] = request.session["username"]
    return render(request, "mysquare.html", d)


@csrf_exempt
def Square(request):
    flag = logincheck(request)
    if flag == 1:
        uid = request.session["userid"]
        username = request.session["username"]

    else:
        messages.warning(request, "您未登录或登录信息过期，请重新登录")
        return HttpResponseRedirect("login/")
    d = {}
    # 下面是渲染输入数据静态实例
    weibolist = []
    fweibo = action.getfriendsweibo(uid)
    if fweibo['status'] == "1":
        weibolist = weibolist + fweibo['weibos']
    myweibo = weiboClient.getUserWeibo(uid, uid)
    if myweibo['status'] == "1":
        weibolist = weibolist + myweibo['weibos']

    weibolist = sorted(weibolist, key=lambda d: datetime.datetime.strptime(d["createTime"], "%Y-%m-%d_%H:%M:%S"),
                       reverse=True)
    d["username"] = request.session["username"]
    d["weiboList"] = weibolist
    return render(request, "square.html", d)


@csrf_exempt
def OtherSpace(request):
    '''
     这个函数用来渲染显示给定的userid的用户的关注列表、被关注列表和发过的微博的页面
     
    '''
    if request.method == 'POST':
        uid = request.POST.get('userid')  # 获取id
    else:
        uid = request.GET.get("userid")

    uid = str(uid)
    mid = request.session['userid']
    d = {}
    # 下面是生成其他用户关注列表的数据格式示例,和myspace不同，这里也需要加上isFriend标明这个用户和登录用户是不是关注了：
    friendList = []
    friends = action.getfriendslist(uid)
    if friends['status'] != "1":
        friendList = []
    else:
        friends = friends['list']
        for i in range(len(friends)):
            fid = friends[i]['id']
            friend = {}
            friend['userid'] = fid
            friend['username'] = friends[i]['name']
            uinfo = user.getUserInfo(fid)
            if uinfo['status'] != "1":
                continue
            uinfo = uinfo['content']
            friend['fanNum'] = uinfo['followersnum']
            friend['friendNum'] = uinfo['friendsnum']
            friend['weiboNum'] = uinfo['statusesnum']
            info = {}
            info['lid'] = fid
            info['rid'] = mid
            friend['isFriend'] = int(action.is_friend(info)['status'])
            friendList.append(friend)
    d["friendList"] = friendList

    # 下面是生成其他用户粉丝列表的数据格式示例
    fanList = []
    fans = action.getfollowerlist(uid)
    if fans['status'] != "1":
        fanList = []
    else:
        fans = fans['list']
        for i in range(len(fans)):
            fid = fans[i]['id']
            fan = {}
            fan["userid"] = fid
            fan['username'] = fans[i]['name']
            uinfo = user.getUserInfo(fid)
            if uinfo['status'] != "1":
                continue
            uinfo = uinfo['content']
            fan['fanNum'] = uinfo['followersnum']
            fan['friendNum'] = uinfo['friendsnum']
            fan['weiboNum'] = uinfo['statusesnum']
            info = {}
            info['rid'] = mid
            info['lid'] = fid
            fan['isFriend'] = int(action.is_friend(info)['status'])
            fanList.append(fan)
    d["fanList"] = fanList

    master = {
        "userid": str(uid),
        "username": " ",  # 注意这里的id和名字不再从session拿，而是要根据传过来的userid拿
        "fanNum": "Nan",
        "weiboNum": "Nan",
        "friendNum": "Nan",
        "isFriend": 0  # 指示这个用户和登录用户是不是关注
    }
    uname = user.getUserName(uid)
    if uname['status'] == "1":
        master['username'] = uname['name']
    uinfo = user.getUserInfo(uid)
    if uinfo['status'] == "1":
        uinfo = uinfo['content']
        master['fanNum'] = uinfo['followersnum']
        master['friendNum'] = uinfo['friendsnum']
        master['weiboNum'] = uinfo['statusesnum']
    info = {}
    info['lid'] = uid
    info['rid'] = mid
    master['isFriend'] = int(action.is_friend(info)['status'])
    # 下面是生成顶部其他用户简单信息的数据示例,注意这里一个dict对象就行，不用list

    d["master"] = master

    # 下面是生成用户微博列表的数据示例
    weibolist = []
    myweibos = weiboClient.getUserWeibo(uid, mid)
    if myweibos['status'] != "1":
        weibolist = []
    else:
        weibolist = myweibos['weibos']
    d["weiboList"] = weibolist
    d["username"] = request.session["username"]  # 这个是显示在顶部导航的登录用户名，不用改

    print("-"*30)
    print(d)
    return render(request, "otherspace.html", d)


@csrf_exempt
def OtherUserInfoPage(request):
    if request.method == 'POST':
        uid = request.POST.get('userid')  # 获取id
    else:
        uid = request.GET.get("userid")

    # 这里的数据应该是用uid查出来的
    d = {}
    res = user.getUserInfo(uid)
    if res['status'] != "0":
        messages.warning(request, "此用户非法或不存在!")
        return HttpResponseRedirect("login/")
    res = res['content']
    d["username"] = res['name']
    d["location"] = res['location']
    d["userid"] = str(uid)
    d["sex"] = res['gender']
    d["fans"] = res['followersnum']
    d["follow"] = res['friendsnum']
    d["duration"] = res['date']
    d["weiboCount"] = res['statuesnum']
    return render(request, "otherUserInfo.html", d)


@csrf_exempt
def UserInfoPage(request):
    # 开始从cookie中获取用户id
    flag = logincheck(request)
    if flag == 1:
        uid = request.session["userid"]
        username = request.session["username"]
    else:
        messages.warning(request, "您未登录或登录信息过期，请重新登录")
        return HttpResponseRedirect("login/")
    d = {}
    res = user.getUserInfo(uid)
    if res['status'] != "1":
        messages.warning(request, "您的账号可能非法或不存在，请重新登录")
        return HttpResponseRedirect("login/")
    res = res['content']
    d["username"] = res['name']
    d["location"] = res['location']
    d["userid"] = str(uid)
    if res['gender'] == "m":
        d["sex"] = "男生"
    else:
        d["sex"] = "女生"
    d["fans"] = res['followersnum']
    d["follow"] = res['friendsnum']
    d["duration"] = res['created']
    d["weiboCount"] = res['statusesnum']
    return render(request, "userInfo.html", d)


@csrf_exempt
def Logout(request):
    del request.session['userid']
    del request.session['username']
    return HttpResponseRedirect("index/")


@csrf_exempt
def Recommend(request):
    '''
    这里和mysquare基本样式一致，只是要进行的数据库操作不同
    '''
    d = {}
    uid = request.session['userid']
    name = request.session['username']
    rec1 = recommender.new_recom(uid)
    friendList = []
    if rec1['status'] != "1":
        friendList = []
    else:
        fdic1 = rec1['list']
        for key in fdic1:
            friend = {}
            fid = key
            friend['userid'] = fid
            uname = user.getUserName(fid)
            if uname['status'] != "1":
                continue
            friend['username'] = uname['name']
            friend['commonNum'] = fdic1[key]
            uinfo = user.getUserInfo(fid)
            if uinfo['status'] != "1":
                continue
            uinfo = uinfo['content']
            friend['fanNum'] = uinfo['followersnum']
            friend['friendNum'] = uinfo['friendsnum']
            friend['weiboNum'] = uinfo['statusesnum']
            info = {}
            info['rid'] = uid
            info['lid'] = fid
            friend['isFriend'] = int(action.is_friend(info)['status'])
            friendList.append(friend)
    d["commonFriendList"] = friendList

    # 下面是推荐关注的列表的数据格式示例
    rec = recommender.users_recom(uid)
    fanList = []
    if rec['status'] != "1":
        fanList = []
    else:
        users = rec['users']
        for i in range(len(users)):
            fid = users[i]
            fan = {}
            uname = user.getUserName(fid)
            if uname['status'] != "1":
                continue
            fan["userid"] = fid
            fan['username'] = uname['name']
            uinfo = user.getUserInfo(fid)
            if uinfo['status'] != "1":
                continue
            uinfo = uinfo['content']
            fan['fanNum'] = uinfo['followersnum']
            fan['friendNum'] = uinfo['friendsnum']
            fan['weiboNum'] = uinfo['statusesnum']
            info = {}
            info['lid'] = fid
            info['rid'] = uid
            fan['isFriend'] = int(action.is_friend(info)['status'])
            fanList.append(fan)
    d["fanList"] = fanList

    recweibo = recommender.popularweibos()
    weibolist = []
    # 下面是推荐的微博的列表
    if recweibo['status'] != "1":
        weibolist = []
    else:
        weiboIDs = recweibo['weibos']
        for i in range(len(weiboIDs)):
            wid = weiboIDs[i]
            weibo = {}
            weibo = weiboClient.getWeibo(wid, uid)
            if weibo['status'] != "1":
                continue
            weibo = weibo['weibo']
            weibolist.append(weibo)
    weibolist = sorted(weibolist, key=lambda d: datetime.datetime.strptime(d["createTime"], "%Y-%m-%d_%H:%M:%S"),
                       reverse=True)

    d["username"] = request.session["username"]
    d["weiboList"] = weibolist

    return render(request, "recommend.html", d)


@csrf_exempt
def LoginCheck(request):
    if request.method == 'POST':
        uid = request.POST.get('userid')  # 获取用户名
        pwd = request.POST.get('password')  # 获取密码
    else:
        uid = request.GET.get("userid")
        pwd = request.POST.get('password')
    uid = str(uid)
    pwd = str(pwd)
    '''
    这里需要
    1.用uid读用户的密码
    2.比较pwd和读回来的密码是否一致
    3.如果相等，flag=1,否则 flag=0
    下面是简单示例
    '''
    res = user.getUserPwd(uid)
    if res['status'] != "1":
        flag = 0
    else:
        password = res['password']
        goldPwd = str(password)  # 这里应该用读数据库的函数
        if goldPwd == pwd:
            flag = 1
        else:
            flag = 0

    if flag == 1:
        # 登录成功的情况
        messages.success(request, "登陆成功！欢迎回来，编号%s" % uid)
        # 登录成功后，在cookie中加入用户的id和昵称
        request.session["userid"] = str(uid)
        request.session["username"] = user.getUserName(str(uid))['name']

        # 下面跳转到“我的关注”,因为重定向有问题，所以得执行跟Square()里一样的操作来渲染页面
        # 下面是渲染输入数据静态实例
        d = {}
        weibolist = []
        fweibo = action.getfriendsweibo(uid)
        if fweibo['status'] == "1":
            weibolist = weibolist + fweibo['weibos']
        myweibo = weiboClient.getUserWeibo(uid, uid)
        if myweibo['status'] == "1":
            weibolist = weibolist + myweibo['weibos']

        weibolist = sorted(weibolist, key=lambda d: datetime.datetime.strptime(d["createTime"], "%Y-%m-%d_%H:%M:%S"),
                           reverse=True)
        d["username"] = request.session["username"]
        d["weiboList"] = weibolist

        print(d)
        return render(request, "square.html", d)

    else:
        # 登录失败，目前不区分具体的失败原因
        messages.success(request, "登录失败！请检查您的用户名与密码是否正确")
        return HttpResponseRedirect("login/")


@csrf_exempt
def RegisCheck(request):
    # 读参数
    if request.method == 'POST':
        uid = request.POST.get('userid')  # 获取用户名
        pwd = request.POST.get('password')  # 获取密码
        rpwd = request.POST.get('rpassword')  # 获取重复输入的密码
        nickname = request.POST.get('nickname')  # 获取昵称
        province = request.POST.get('province')  # 获取省份
        city = request.POST.get('city')  # 获取城市
        sex = request.POST.get('sex')  # 获取性别
    else:
        uid = request.GET.get("userid")  # 获取用户名
        pwd = request.POST.get('password')  # 获取密码
        rpwd = request.POST.get('rpassword')  # 获取重复输入的密码
        nickname = request.POST.get('nickname')  # 获取昵称
        province = request.POST.get('province')  # 获取省份
        city = request.POST.get('city')  # 获取城市
        sex = request.POST.get('sex')  # 获取性别

    if rpwd != pwd:
        messages.success(request, "两次输入的密码不一致")
        return HttpResponseRedirect("register/")
    '''
    这里需执行插入新用户的函数
    若插入成功，flag = 1，否则 flag = 0
    '''
    info = {}
    info['tel'] = uid
    info['name'] = nickname
    info['province'] = province
    info['city'] = city
    info['gender'] = sex
    info['password'] = pwd
    res = user.setNewUser(info)
    if res['status'] != "1":
        reason = res['msg']
        flag = 0
    else:
        flag = 1
    if flag == 1:
        messages.success(request, "注册成功！请登录")
        return HttpResponseRedirect("login/")
    else:
        reason = reason + "注册失败！"
        messages.success(request, reason)
        return HttpResponseRedirect("register/")


@csrf_exempt
def RegisPage(request):
    return render(request, "regis.html")


@csrf_exempt
def addTransfer(request):
    '''
        发评论
    '''
    if request.method == 'POST':
        com_wid = request.POST.get('weiboid')  # 获取被评论的微博的id
        content = request.POST.get('content')
    else:
        com_wid = request.GET.get("weiboid")
        content = request.GET.get('content')
    uid = request.session["userid"]
    username = request.session["username"]
    info = {}
    info['author'] = uid
    info['weiboId'] = com_wid
    if content == "":
        info['text'] = "我只是路过"
    else:
        info['text'] = content

    # 执行评论操作
    com_res = commenting.postcomment(info)
    # 不管成不成都返回成功

    messages.success(request, "评论成功！")
    return HttpResponseRedirect("transfer/?weiboid=" + com_wid)


@csrf_exempt
def addComment(request):
    '''
        转发微博
    '''
    if request.method == 'POST':
        trans_wid = request.POST.get('weiboid')  # 获取被转发的微博的id
        content = request.POST.get('content')
    else:
        trans_wid = request.GET.get("weiboid")
        content = request.GET.get('content')

    uid = request.session["userid"]
    username = request.session["username"]
    info = {}
    info['uid'] = uid
    info['wid'] = trans_wid
    if content != "":
        info['text'] = content

    # 执行转发操作
    repost = weiboClient.repostweibo(info)
    if repost['status'] != "1":
        messages.success(request, "转发失败！请重试")
    # 不管成不成功都返回成功
    else:
        messages.success(request, "转发成功！跳转至转发微博")
        trans_wid = repost['ID']
    return HttpResponseRedirect("comment/?weiboid=" + trans_wid)


@csrf_exempt
def addWeibo(request):
    '''
        发微博
    '''
    if request.method == 'POST':
        content = request.POST.get('content')
    else:
        content = request.GET.get('content')

    uid = request.session["userid"]
    username = request.session["username"]

    '''result = re.findall(r"#[^#]+#", content)

    if len(result) > 0:
        topic = result[0]
    else:
        topic = "我爱海量图""'''
    topic = "我爱海量图"
    info = {}
    info['topic'] = topic
    info['text'] = content
    info['uid'] = uid
    print(info)
    post_res = weiboClient.postNewWeibo(info)
    if post_res['status'] != "1":
        messages.success(request, "发博失败!请重试")
    # 执行发微博操作
    else:
        messages.success(request, "发博成功！可到个人中心查看")
    return HttpResponseRedirect("/myspace")

@csrf_exempt
def searchPeople(request):
    '''
        查询用户
    '''
    if request.method == 'POST':
        target_people = request.POST.get('target_people')
    else:
        target_people = request.GET.get('target_people')

    searchResult = user.getUserID(target_people)
    if searchResult['status'] != "1":
        messages.success(request, "查无此人")
        return HttpResponseRedirect("/square")
    return HttpResponseRedirect("/otherspace/?userid=%s"%(searchResult["uid"]))


@csrf_exempt
def comment(request):
    '''
        生成转发微博的页面
    '''
    if request.method == 'POST':
        wid = request.POST.get('weiboid')  # 获取id
    else:
        wid = request.GET.get("weiboid")

    wid = str(wid)

    d = {}
    # 下面是生成被转发微博的内容的数据
    uid = request.session["userid"]
    username = request.session["username"]
    weibo = weiboClient.getWeibo(wid, uid)
    if weibo['status'] != "1":
        weibo = {}
    else:
        weibo = weibo['weibo']
    d["weibo"] = weibo
    d["username"] = request.session["username"]
    return render(request, "comment.html", d)


@csrf_exempt
def follow(request):
    if request.method == 'POST':
        fid = request.POST.get('userid')  # 获取要关注的人的id
    else:
        fid = request.GET.get("userid")
    uid = request.session["userid"]
    print("in follow, fid = " + fid + ", uid = " + uid)
    info = {}
    info['lid'] = uid
    info['rid'] = fid
    # 执行关注操作
    follow = action.follow(info)
    if follow['status'] == "1":
        return HttpResponse("关注成功")
    elif follow['status'] == "0":
        return HttpResponse("您已关注，不能重复关注了哦")
    else:
        return HttpResponse("关注失败，请刷新后重试")
    # 不管成不成功都返回成功


@csrf_exempt
def disFollow(request):
    if request.method == 'POST':
        fid = request.POST.get('userid')  # 获取要关注的人的id
    else:
        fid = request.GET.get("userid")
    uid = request.session["userid"]
    info = {}
    info['lid'] = uid
    info['rid'] = fid
    # 执行关注操作
    unfollow = action.unfollow(info)
    if unfollow['status'] == "1":
        return HttpResponse("取关成功")
    elif unfollow['status'] == "0":
        return HttpResponse("您已取关，不能重复取关了哦")
    else:
        return HttpResponse("取关失败，请刷新后重试")


@csrf_exempt
def delWeibo(request):
    if request.method == 'POST':
        wid = request.POST.get('weiboid')  # 获取id
    else:
        wid = request.GET.get("weiboid")
    print(wid)
    # 执行删除微博操作
    del_res = weiboClient.delweibo(wid)
    if del_res["status"] == "1":
        return HttpResponse("已删除")
    else:
        return HttpResponse("删除失败，请刷新后重试")


@csrf_exempt
def clickLike(request):
    if request.method == 'POST':
        wid = request.POST.get('weiboid')  # 获取id
    else:
        wid = request.GET.get("weiboid")
    print("likelike")
    # 执行点赞操作
    uid = request.session["userid"]
    info = {}
    info['uid'] = uid
    info['wid'] = wid
    info['flag'] = "1"
    res = action.attitudes(info)
    if res['status'] == "0":
        return HttpResponse("已点赞")
    else:
        return HttpResponse("抱歉，点赞失败，请刷新后重试")


@csrf_exempt
def disLike(request):
    if request.method == 'POST':
        print('=' * 30)
        print(request.POST)
        print('=' * 30)
        wid = request.POST.get('weiboid')  # 获取id
    else:
        print('-' * 30)
        print(request.GET)
        print('-' * 30)
        wid = request.GET.get("weiboid")
    # 执行取消赞操作
    print("disLike, wid = " + wid)
    uid = request.session["userid"]
    info = {}
    print(uid)
    print(wid)
    info['uid'] = uid
    info['wid'] = wid
    info['flag'] = "-1"
    res = action.attitudes(info)
    print(res)
    if res['status'] == "0":
        return HttpResponse("已取消赞")
    else:
        return HttpResponse("抱歉，取消点赞失败，请刷新后重试")
