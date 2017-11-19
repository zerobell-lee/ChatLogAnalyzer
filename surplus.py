import codecs
from collections import Counter
from operator import itemgetter
from konlpy.tag import Kkma
from konlpy.tag import Twitter
from konlpy.tag import Hannanum
from konlpy.utils import pprint
import time

def surplusamount(lines):
    surplus_dict = dict()
    line_row = -1
    bunch = ''
    b_name = ''

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
                if b_name in list(surplus_dict.keys()):
                    surplus_dict.update({ b_name : surplus_dict[b_name] + len(bunch)})
                else:
                    surplus_dict.update({ b_name : len(bunch)})
                bunch = ''
                b_name = ''
                continue
                #bunch는 말뭉치. 즉, 여러줄로 구성된 대화. b_name은 해당 bunch를 발언한 대화자.
                
        if (bunch != ''):
            if (line[-2:-1] == '\r'):
                bunch = bunch + line.split('\r\n')[0]
                
                if b_name in list(surplus_dict.keys()):
                    surplus_dict.update({ b_name : surplus_dict[b_name] + len(bunch)})
                else:
                    surplus_dict.update({ b_name : len(bunch)})
                bunch = ''
                b_name = ''
                continue
            bunch = bunch + line.split('\n')[0]
            continue

        string = line.split(':')
        if (len(string)<3): continue
        
        name = string[1]
        name = name.split(',')
        name = name[1]
        name = name[1:-1]
        
        text = ''
        for i in range(2,len(string)):
            text = text + string[i]

        if (text[-2:-1] != '\r') and (text[-1:] == '\n'):
            bunch = text[0:-1]
            b_name = name
            continue
        else:
            text = text.split('\r\n')[0]
            text = text[1:]

            if name in list(surplus_dict.keys()):
                surplus_dict.update({ name : surplus_dict[name] + len(text)})
            else:
                surplus_dict.update({ name : len(text)})

    print("잉여력 측정 결과입니다.")

    
    for name in sorted(surplus_dict.items(), key=itemgetter(1), reverse=True):
        print(name[0], ":", name[1])

def analyze_i(lines):
    surplus_dict = dict()
    line_row = -1
    bunch = ''
    b_name = ''
    
    for line in lines:
        line_row += 1
        if (line_row < 5 ):
            continue
        
        if (line == '\r\n'):
            if (bunch == ''):
                continue
            else:
                if b_name in list(surplus_dict.keys()):
                    surplus_dict.update({ b_name : surplus_dict[b_name] + bunch})
                else:
                    surplus_dict.update({ b_name : bunch})
                bunch = ''
                b_name = ''
                continue
                
        if (bunch != ''):
            if (line[-2:-1] == '\r'):
                bunch = bunch + ' ' + line.split('\r\n')[0]
                
                if b_name in list(surplus_dict.keys()):
                    surplus_dict.update({ b_name : surplus_dict[b_name] + bunch})
                else:
                    surplus_dict.update({ b_name : bunch})
                bunch = ''
                b_name = ''
                continue
            bunch = bunch + ' ' + line.split('\n')[0]

            continue

        string = line.split(':')
        if (len(string)<3): continue
        
        name = string[1]
        name = name.split(',')
        name = name[1]
        name = name[1:-1]
        
        text = ''
        for i in range(2,len(string)):
            text = text + string[i]

        if (text[-2:-1] != '\r') and (text[-1:] == '\n'):
            bunch = text[0:-1]
            b_name = name
            continue
        else:
            text = text.split('\r\n')[0]
            text = text[1:]

            if name in list(surplus_dict.keys()):
                surplus_dict.update({ name : surplus_dict[name] + ' ' + text})
            else:
                surplus_dict.update({ name : text })

    while True:
        name = input("name?")
        nouns = Hannanum().nouns(surplus_dict[name])
        #가장 많이 언급된 단어를 선별하는 클래스. KoNLPy에 정의된 다른 클래스를 사용해도 된다.
        print(name, "-------------")
        pprint(Counter(nouns).most_common(10))
        print("====================\n")
        time.sleep(5)

        


def main():
    path = input("path : ")
    f = codecs.open(path, 'r', 'utf-8')
    slist = f.readlines()
    f.close()

    surplusamount(slist)
    #단순히 대화 '양'만을 측정하는 메소드.
    analyze_i(slist)
    #KoNLPy를 이용하여 가장 많이 언급한 키워드 10개를 선별하는 메소드.

main()
    
    
