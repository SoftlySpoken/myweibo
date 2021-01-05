import pymysql
import pandas as pd
mysql_conn = pymysql.connect(host='127.0.0.1', port=3306, user='root',
                             password='seagraph2020', db='weibodatabase')

int_province = {}
province_int = {}
int_city = {}
city_int = {}


def do_query(sql: str):
    try:
        with mysql_conn.cursor() as cursor:
            cursor.execute(sql)
            select_result = cursor.fetchall()
            return select_result
    except Exception as e:
        print(e)


def gen_sql(table_name: str, src: str, dst: str) -> str:
    return f" select {src},{dst} from {table_name} ;"


def doEscape(raw_str: str) -> str:
    return raw_str.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n") \
        .replace("\r", "\\r").replace("\b", "\\b").replace("\f", "\\f").replace("\"", "\\\"")


def translate_nt(name1: str, t1: str, s1: str, name2: str, t2: str, s2: str) -> str:
    if name1 == 'uid' or name1 == 'suid' or name1 == 'tuid':
        t1 = ''
    if name2 == 'uid' or name2 == 'suid' or name2 == 'tuid':
        t2 = 'uid'

    if name1 == 'mid' or name1 == 'smid' or name1 == 'tmid':
        t1 = 'mid'
    if name2 == 'mid' or name2 == 'smid' or name2 == 'tmid':
        t2 = 'mid'

    predicate = name2
    if predicate == 'suid' or predicate == 'tuid':
        predicate = 'careFor'

    if predicate == 'smid' or predicate == 'tmid':
        predicate = 'refer'

    obj = ''
    if t2 == 'datetime':
        # '2011-10-07 18:54:43'
        s2 = str(s2)
        obj = str(s2).replace(' ', '_')
        obj = "\"" + doEscape(obj) + "\""
    elif t2 == 'uid':
        obj = "<" + s2 + ">"
    elif t2 == 'mid':
        obj = "<" + s2 + ">"
    elif type(s2) == str:
        obj = '\"' + doEscape(s2) + '\"'
    elif type(s2) == int:
        obj = '"' + str(s2) + '\"^^<http://www.w3.org/2001/XMLSchema#integer>'
    else:
        obj = '\"' + doEscape(s2) + '\"'

    return f"<{s1}>\t<{predicate}>\t{obj}.".replace(' ', '').replace('\t', ' ')


def table_translator(tableName: str, table_struct: dict, fout):
    PRIMARY_KEY = table_struct['PRIMARY KEY']
    PRIMARY_KEY_type = table_struct[PRIMARY_KEY]
    for k, k_type in table_struct.items():
        if k == PRIMARY_KEY or k == 'PRIMARY KEY':
            continue
        sql = gen_sql(tableName, PRIMARY_KEY, k)
        print(f'excute SQL:{sql}')
        results = do_query(sql)
        for record in results:
            PRIMARY_KEY_VALUE = record[0]
            k_V = record[1]
            print(translate_nt(PRIMARY_KEY, PRIMARY_KEY_type, PRIMARY_KEY_VALUE,
                               k, k_type, k_V), file=fout)
        print(f"get {len(results)} results.")


def main():
    Table_user = {
        'uid': 'varchar',
        'screen_name': 'varchar',
        'name': 'varchar',
        'province': 'int',
        'city': 'int',
        'location': 'varchar',
        'url': 'varchar',
        'gender': 'varchar',
        'followersnum': 'int',
        'friendsnum': 'int',
        'statusesnum': 'int',
        'favouritesnum': 'int',
        'created_at': 'datetime',
        'PRIMARY KEY': 'uid',
    }
    Table_userrelation = {
        'suid': 'varchar',
        'tuid': 'varchar',
        'PRIMARY KEY': 'suid'
    }
    Table_weibo = {
        'mid': 'varchar',
        'date': 'datetime',
        'text': 'varchar',
        'source': 'varchar',
        'repostsnum': 'int',
        'commentsnum': 'int',
        'attitudesnum': 'int',
        'uid': 'varchar',
        'topic': 'varchar',
        'PRIMARY KEY': 'mid',
    }
    Table_weiborelation = {
        'smid': 'varchar',
        'tmid': 'varchar',
        'PRIMARY KEY': 'smid',
    }
    with open('./weibo.nt', 'w', encoding='utf-8') as file_out:
        table_translator(tableName='user', table_struct=Table_user, fout=file_out)
        table_translator(tableName='userrelation', table_struct=Table_userrelation, fout=file_out)
        table_translator(tableName='weibo', table_struct=Table_weibo, fout=file_out)
        table_translator(tableName='weiborelation', table_struct=Table_weiborelation, fout=file_out)


def extract_province_map():
    global int_province, province_int
    for on in do_query("select distinct province,location from user "):
        int_province[on[0]] = on[1][:on[1].find(' ')]
        province_int[on[1][:on[1].find(' ')]] = on[0]


def extract_city_map():
    global int_city, city_int
    for on in do_query("select distinct city,location from user "):
        int_city[on[0]] = on[1]
        city_int[on[1]] = on[0]


# print(do_query("select * from user limit 10")[0])

# extract_province_map()
# extract_city_map()
# main()

def topk():
    results = do_query("select * from weiborelation;")
    with open('weiborelation_topk.txt','w') as fout:
        for t in results:
            print(t[1],file=fout)
    results = do_query("select * from userrelation;")
    with open('userrelation_topk.txt', 'w') as fout:
        for t in results:
            print(t[1], file=fout)

    results = do_query("select topic,date from weibo;")
    with open('weibotopic.txt', 'w') as fout:
        for t in results:
            print(t[0],"\t",t[1], file=fout)

def userrelation():
    results = do_query("select * from userrelation;")
    with open('userrelation.txt','w') as fout:
        for t in results:
            print(t[0]+'\t'+t[1],file=fout)

def user():
    results = do_query("select * from user;")
    cols = ["uid", "screen_name" ,"name", "province" ,"city","location","url","gender",
    "followersnum","friendsnum","statusesnum","favouritesnum","created_at"]

    vi_maps = { v:k for k,v in enumerate(cols)}
    iv_maps = {k: v for k, v in enumerate(cols)}
    values = {k:[] for k in cols}
    for r in results:
        for i,v in enumerate(r):
            values[iv_maps[i]].append(v)
    df = pd.DataFrame(values)
    # print(df)
    df.to_csv("./user.csv",encoding='utf-8')
    # print(pd.read_csv("./user.csv")['screen_name'])

# userrelation()
# user()
topk()
mysql_conn.close()
