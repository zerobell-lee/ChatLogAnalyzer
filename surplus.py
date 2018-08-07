#-*- coding:utf-8 -*-
import codecs
from collections import Counter
from operator import itemgetter
from WordAnalyzer import WordAnalyzer
import time

memberDict = dict()
hourDict = dict()
monthDict = dict()
pictureDict = dict()

filter = ['NNP', 'NNG', 'VV', 'VA', 'IC']
exception = ['하다', '되다', 'ㅋㅋ']


def parseMonthTime(line):
    splited = line.split('년')
    year = int(splited[0])
    splited = splited[1].split('월')
    month = int(splited[0])
    splited = splited[1].split('일')
    day = int(splited[0])
    splited = splited[1].split(' ')
    isPM = splited[1]=='오후'
    timestamp = splited[2][0:-1].split(':')

    if isPM:
        if timestamp[0]=='12':
            hour = 12 
        else:
            hour = int(timestamp[0]) + 12
    else:
        if timestamp[0]=='12':
            hour = 0
        else:
            hour = int(timestamp[0])

    yearMonth = str(year) + '-' + str(month)
    hour = '0' + str(hour) if (hour<10) else str(hour)

    return (yearMonth, hour)
    

def surplusamount(lines):
    global memberDict
    global pictureDict
    global monthDict
    global hourDict
    line_row = -1
    bunch = ''
    b_name = ''
    b_yearMonth = ''
    b_hour = ''

    for line in lines:
        line_row += 1
        #대화방 정보 출력
        if (line_row < 5 ):
            print(line.split('\n')[0].split('\r')[0])
            continue

        
        if (line == '\r\n'):
            #대화 도중 개행문자 \n가 들어간 대화를 따로 처리하기 위한 구문
            if (bunch == ''):
                continue
            else:
                if b_name in list(memberDict.keys()):
                    memberDict.update({ b_name : memberDict[b_name] + ' ' + bunch})
                else:
                    memberDict.update({ b_name : bunch})

                if b_yearMonth in list(monthDict.keys()):
                    monthDict.update({ b_yearMonth : monthDict[b_yearMonth] + len(bunch)})
                else:
                    monthDict.update({ b_yearMonth : len(bunch)})

                if b_hour in list(hourDict.keys()):
                    hourDict.update({ b_hour : hourDict[b_hour] + len(bunch)})
                else:
                    hourDict.update({ b_hour : len(bunch)})

                bunch = ''
                b_name = ''
                b_yearMonth = ''
                b_hour = ''
                continue
                #bunch는 여러줄로 구성된 대화. b_name은 해당 bunch를 발언한 대화자.
                
        if (bunch != ''):
            if (line[-2:-1] == '\r'):
                bunch = bunch + ' ' + line.split('\r\n')[0]
                
                if b_name in list(memberDict.keys()):
                    memberDict.update({ b_name : memberDict[b_name] + ' ' + bunch})
                else:
                    memberDict.update({ b_name : bunch})

                if b_yearMonth in list(monthDict.keys()):
                    monthDict.update({ b_yearMonth : monthDict[b_yearMonth] + len(bunch)})
                else:
                    monthDict.update({ b_yearMonth : len(bunch)})

                if b_hour in list(hourDict.keys()):
                    hourDict.update({ b_hour : hourDict[b_hour] + len(bunch)})
                else:
                    hourDict.update({ b_hour : len(bunch)})

                bunch = ''
                b_name = ''
                b_yearMonth = ''
                b_hour = ''
                continue
            bunch = bunch + ' ' + line.split('\n')[0]
            continue

        string = line.split(':')
        if (len(string)<3): continue
       
        #이름 취득 
        name = string[1]
        name = name.split(',')
        name = name[1]
        name = name[1:-1]

        yearMonth, hour = parseMonthTime(string[0] + string[1])
        
        text = '' 
        for i in range(2,len(string)):
            text = text + ':' + string[i]

        if (text[-2:-1] != '\r') and (text[-1:] == '\n'):
            bunch = text[0:-1]
            bunch = bunch[2:]
            b_name = name
            b_yearMonth = yearMonth
            b_hour = hour
            continue
        text = text.split('\r\n')[0]
        text = text[1:]
        if text == ' <사진>':
            if name in list(pictureDict.keys()):
                pictureDict.update({ name : pictureDict[name] + 1})
            else:
                pictureDict.update({ name : 1})
            continue
        else:

            if name in list(memberDict.keys()):
                memberDict.update({ name : memberDict[name] + ' ' + text})
            else:
                memberDict.update({ name : text})

            if yearMonth in list(monthDict.keys()):
                monthDict.update({ yearMonth : monthDict[yearMonth] + len(text)})
            else:
                monthDict.update({ yearMonth : len(text)})

            if hour in list(hourDict.keys()):
                hourDict.update({ hour : hourDict[hour] + len(text)})
            else:
                hourDict.update({ hour : len(text)})

    print("잉여력 측정 결과입니다.")

    
    for name in sorted(memberDict.items(), key=lambda e: len(e[1]), reverse=True):
        print(name[0], ":", len(name[1]))

def analyze_i():
    global memberDict
    w = WordAnalyzer()

    for name in sorted(memberDict.items(), key=lambda e: len(e[1]), reverse=True):
        nouns = [t[0] for t in w.filter(name[1], filter, exception)]
        #가장 많이 언급된 단어를 선별하는 클래스. KoNLPy에 정의된 다른 클래스를 사용해도 된다.
        print(name[0], "-------------")
        for e in Counter(nouns).most_common(50):
            print(e[1], e[0], end='\n')
        print("====================\n")

        


def main():
    path = input("path : ")
    f = codecs.open(path, 'r', 'utf-8', errors='ignore')
    slist = f.readlines()
    f.close()

    surplusamount(slist)
    #단순히 대화 '양'만을 측정하는 메소드.
    analyze_i()

main()
    
    
