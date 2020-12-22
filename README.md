### To load the database

```
$ ssh root@39.101.65.125	# Password: Dell2020
$ cd /home/liangjianming/gStore-0.9/gStore-1.57.0/
$ export LD_LIBRARY_PATH=/opt/boost-1.57.0/lib:/opt/gcc-5.4.0/lib64:$LD_LIBRARY_PATH
$ export PATH=/opt/gcc-5.4.0/bin:$PATH
$ bin/ghttp weibo 9000
```

### To start myweibo server (in the project directory)

```
$ python manage.py runserver
```

若遇到
```
no such table:django_session
```
则执行如下命令
```
python manage.py migrate
```
### Bug list

#### 必须解决的问题

- [x] 点赞：默认显示已赞（weibohead.html, weibolist.html）；打开微博详情页时取消赞会失败（view.py中disLike函数，获取到的wid为空）
- [x] 关注：关注会导致错误
- [x] 取消关注：打开用户详情页时“取消关注”是写死的？（friendlist.html, otherfriendlist.html），点击会失败（view.py中follow函数，获取到的fid为空）；因此还没有测试关注后显示在关注列表、取关功能
- [x] 搜索：在个人中心的搜索页面键入他人的昵称，不能正确跳转至详情页面
- [x] 数据设计：数据中没有存储当前用户是否赞了当前微博的信息
#### 可以考虑解决的问题

- 目前微博话题是写死的，自己打话题标签没有用，不打话题标签也会被强行加上#我爱海量图#话题
- 评论时使用中文标点符号有时出现乱码（发布动态时不会）,需要测试数据