from LogParser import LogParser
import pymysql
import time
import random
import string
import json
import sys
import argparse


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def combine_id():
    return str(time.time()).replace('.', '') + id_generator()


def parseExpression(string):
    if len(string.split('=')) > 2:
        return False

    leftside, rightside = string.split('=')

    if str.isdigit(rightside):
        if leftside.upper() != 'PASSWD':
            rightside = int(rightside)

    return leftside.upper(), rightside


def saveToDB(data, dbConfig):
    db = pymysql.connect(host=dbConfig['HOST'], port=dbConfig['PORT'], user=dbConfig['USER'], passwd=dbConfig['PASSWD'], db=dbConfig['DB'])
    cursor = db.cursor(pymysql.cursors.DictCursor)

    tmp_id = ''
    while True:
        tmp_id = combine_id()
        cursor.execute(
            "select TABLE_NAME from INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA='kakao' and TABLE_NAME like %s",
            ('%' + tmp_id + '%',))
        if len(cursor.fetchall()) > 0:
            continue
        else:
            break

    sql = {
        'search': {
            'reduct': "select TABLE_NAME from INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA='kakao' and TABLE_NAME like %s" % (
                        '%' + tmp_id + '%')
        },
        'create': {
            'amount': "create table amount%s (id int auto_increment, name varchar(255), amount int, constraint pk_id primary key(id))" % tmp_id,
            'keywords': "create table keywords%s (id int auto_increment, name varchar(255), keyword varchar(255), count int, constraint pk_id primary key(id))" % tmp_id,
            'time': "create table time%s (hour int, amount int, constraint pk_hour primary key(hour))" % tmp_id
        },
        'insert': {
            'amount': "insert into amount" + tmp_id + " (name, amount) values (%s, %s)",
            'keywords': "insert into keywords" + tmp_id + " (name, keyword, count) values (%s, %s, %s)",
            'time': "insert into time" + tmp_id + " (hour, amount) values (%s, %s)"
        }
    }

    time_, amount, keywords = data['hour'], data['amount'], data['keywords']

    for s in sql['create'].keys():
        cursor.execute(sql['create'][s])

    for h in time_.keys():
        cursor.execute(sql['insert']['time'], (h, time_[h],))

    for a in amount.keys():
        cursor.execute(sql['insert']['amount'], (a, amount[a],))

    for k in keywords.keys():
        kwds = keywords[k]

        for kw in kwds:
            cursor.execute(sql['insert']['keywords'], (k, kw[0], kw[1],))

    db.commit()
    print(json.dumps({'result': 'success', 'analyze_id': tmp_id}))


parser = argparse.ArgumentParser(prog='CHATLOG ANALYZER')
parser.add_argument('source', help='the input file source(path)')
parser.add_argument('-d', '--db', help='if -d included, saving to db is enabled', action='store_true')
parser.add_argument('-e', help='''config of DB config. \n
ex) -e host=localhost -e port=3306 -e user=root -e passwd=12341234 -e db=chatlog\n
when argument "port" is not included, the default port would be 3306\n
But other arguments "host", "user", "passwd", "db" are required.''', action='append')
parser.add_argument('-s', help='the OS where the chat log came from. "android" and "iOS" is available.')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.11')

startOptions = parser.parse_args()
dbConfig = {}

if startOptions.db:
    for db_arg in startOptions.e:
        leftside, rightside = parseExpression(db_arg)
        dbConfig[leftside] = rightside

    if 'PORT' not in dbConfig.keys():
        dbConfig['PORT'] = 3306

    for necessary in ['HOST', 'USER', 'PASSWD', 'DB']:
        if necessary not in dbConfig.keys():
            print('[Error]Invalid Argument:: "%s" variable not in Database Config' % necessary)
            exit(-1)

parser = LogParser(system=startOptions.s if startOptions.s else 'android', topKw=100)
data = parser.process(startOptions.source)

if startOptions.db:
    saveToDB(data, dbConfig)
else:
    print(json.dumps(data))


