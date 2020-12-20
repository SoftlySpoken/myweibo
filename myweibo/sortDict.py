import datetime
a = [
    {
    "author":{"hi":"1"},
    "isNum": 5,
    "createTime": "2019-06-08 12:00:36"
    },
    {
    "author":{"hi":"2"},
    "isNum": 4,
    "createTime": "2018-06-08 12:00:36"
    },
    {
    "author":{"hi":"3"},
    "isNum": 3,
    "createTime": "2020-01-02 12:00:36"
    },
]
b = sorted(a,key = lambda d:datetime.datetime.strptime(d["createTime"],"%Y-%m-%d_%H:%M:%S"))
print(b)