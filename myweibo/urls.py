"""myweibo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.views.static import serve
from . import view
 
urlpatterns = [
    path('admin/', admin.site.urls),
    url('hello/', view.hello,name="hello"),
    url('index/', view.index,name="Index"),
    url('login/', view.LoginPage,name="LoginPage"),
    url('register/', view.RegisPage,name="RegisPage"),
    url('userInfo/', view.UserInfoPage,name="UserInfoPage"),
    url('loginCheck/', view.LoginCheck,name="LoginCheck"),
    url('regisCheck/', view.RegisCheck,name="RegisCheck"),
    url('logout/', view.Logout,name="LogOut"),
    url('square/', view.Square,name="Square"),
    url('myspace/', view.MySpace,name="MySpace"),
    url('searchPeople/', view.searchPeople,name="searchPeople"),
    url('otherspace/', view.OtherSpace,name="OtherSpace"),
    url('otherUserInfo/', view.OtherUserInfoPage,name="OtherUserInfoPage"),
    url('transfer/', view.transfer,name="transfer"),
    url('comment/', view.Comment, name="comment"),
    url('addComment/', view.addComment,name="addComment"),
    url('addTransfer/', view.addTransfer,name="addTransfer"),
    url('addWeibo/', view.addWeibo,name="addWeibo"),
    url('delWeibo/', view.delWeibo,name="delWeibo"),
    url('clickLike/', view.clickLike,name="clickLike"),
    url('disLike/', view.disLike,name="disLike"),
    url('follow/', view.follow,name="follow"),
    url('disFollow/', view.disFollow,name="disFollow"),
    url('recommend/', view.Recommend,name="Recommend"),
    url(r'^templates/img/(?P<path>.*)', serve, {'document_root':'D:\\myweibo\\templates\\img'}),
]
