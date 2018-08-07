#-*- coding:utf-8 -*-
import codecs
from collections import Counter
from operator import itemgetter
from WordAnalyzer import WordAnalyzer
import json
import os

memberDict = dict()
hourDict = dict()
monthDict = dict()
pictureDict = dict()

WORKDIR =  os.path.dirname(os.path.realpath(__file__))
OUTPUTDIR = ''

filter = ['NNP', 'NNG', 'VV', 'VA', 'IC']
exception = []


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

    month = '0' + str(month) if (month<10) else str(month)
    day = '0' + str(day) if (day<10) else str(day)
    yearMonth = str(year) + '-' + month + '-' + day
    hour = '0' + str(hour) if (hour<10) else str(hour)

    return (yearMonth, hour)
    

def surplusamount(lines):
    global memberDict
    global pictureDict
    global monthDict
    global hourDict
    global OUTPUTDIR

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

        yearMonth, hour = parseMonthTime(string[0] + ':' + string[1])
        
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

    total_amount = dict()
    for names in sorted(memberDict.items(), key=lambda e: len(e[1]), reverse=True):
        total_amount.update({ names[0] : len(names[1])})
    with open(OUTPUTDIR + '/total_amount.json', 'w', encoding='utf-8') as make_file:
        json.dump(total_amount, make_file, ensure_ascii=False, indent='\t')
    with open(OUTPUTDIR + '/hour.json', 'w', encoding='utf-8') as make_file:
        json.dump(hourDict, make_file, ensure_ascii=False, indent='\t')
    with open(OUTPUTDIR + '/month.json', 'w', encoding='utf-8') as make_file:
        json.dump(monthDict, make_file, ensure_ascii=False, indent='\t')

def analyze_i():
    global memberDict
    w = WordAnalyzer()

    for name in sorted(memberDict.items(), key=lambda e: len(e[1]), reverse=True):
        nouns = [t[0] for t in w.filter(name[1], filter, exception)]
        #가장 많이 언급된 단어를 선별하는 클래스. KoNLPy에 정의된 다른 클래스를 사용해도 된다.
        with open(OUTPUTDIR + '/' + name[0] + '.json', 'w', encoding='utf-8') as make_file:
            json.dump(Counter(nouns).most_common(50), make_file, ensure_ascii=False, indent='\t')

        


def main():
    global OUTPUTDIR
    path = input("path : ")
    filename = path.split('/')[-1].split('.')[0]
    f = codecs.open(path, 'r', 'utf-8', errors='ignore')
    slist = f.readlines()
    f.close()

    while True:
        if 'result' in os.listdir(WORKDIR):
            if os.path.isdir(WORKDIR + '/result'):
                tag = 1
                if filename in os.listdir(WORKDIR + '/result'):
                    orig = filename
                    while filename in os.listdir(WORKDIR + '/result'):
                        filename = orig + '(' + str(tag) + ')'
                        tag += 1
                OUTPUTDIR = WORKDIR + '/result/' + filename
                os.mkdir(OUTPUTDIR)
                break
            else:
                print("Error : ", WORKDIR, '/result already exists. But it is not a directory')
                exit()
        else:
            os.mkdir(WORKDIR + '/result')
            continue

    print('WORKDIR : ', WORKDIR, '\nOUTPUTDIR : ', OUTPUTDIR)
                
    surplusamount(slist)
    #단순히 대화 '양'만을 측정하는 메소드.
    analyze_i()

main()
    
    
