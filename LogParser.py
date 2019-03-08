from DatetimeParser import *
from collections import Counter
import mecab


class LogParser():
    def __init__(self, **kwargs):
        self.system = kwargs['system']
        self.datetimeParser = self.getParser()
        self.mecab = mecab.MeCab()
        if 'topKw' in kwargs:
            self.topKw = kwargs['topKw']
        else:
            self.topKw = 30

    @classmethod
    def read(cls, path):
        with open(path, 'rb') as fp:
            texts = fp.read().decode('utf-8').split('\r\n')

        return texts

    @classmethod
    def isChat(cls, l):
        return len(l.split(':')) > 2

    @classmethod
    def seperate(cls, l):
        parts = l.split(',')
        dt, rest = parts[0], ''.join(parts[1:])
        rest = rest.split(':')
        name, ctt = rest[0].strip(), ':'.join(rest[1:]).lstrip()

        return dt, name, ctt

    def process(self, path):
        return self.analyze(path)

    def getParser(self):
        if self.system == 'android':
            return AndroidDatetimeParser()
        else:
            return IOSDateTimeParser()

    def analyze(self, path):
        texts = self.read(path)
        analyzed_result = {'amount': {}, 'hour': {}, 'keywords': {}, 'emoticons': {}, 'photos': {}}

        startPoint = 3 if self.system == 'android' else 2

        for i in range(startPoint, len(texts)):
            l = texts[i]
            if self.isChat(l):
                dt, name, ctt = self.seperate(l)
                name = '개인-' + name
                hour = self.datetimeParser.getHour(dt)

                if name in analyzed_result['amount']:
                    analyzed_result['amount'][name] += len(ctt)
                else:
                    analyzed_result['amount'][name] = len(ctt)

                if hour in analyzed_result['hour']:
                    analyzed_result['hour'][hour] += len(ctt)
                else:
                    analyzed_result['hour'][hour] = len(ctt)

                if ctt == '이모티콘':
                    if name in analyzed_result['emoticons']:
                        analyzed_result['emoticons'][name] += 1
                    else:
                        analyzed_result['emoticons'][name] = 1
                elif ctt == '사진':
                    if name in analyzed_result['photos']:
                        analyzed_result['photos'][name] += 1
                    else:
                        analyzed_result['photos'][name] = 1
                elif ctt.startswith('샵검색:'):
                    continue
                else:
                    nouns = Counter(self.mecab.nouns(ctt))

                    if name in analyzed_result['keywords']:
                        for n in nouns.keys():
                            if n in analyzed_result['keywords'][name]:
                                analyzed_result['keywords'][name][n] += nouns[n]
                            else:
                                analyzed_result['keywords'][name][n] = nouns[n]
                    else:
                        analyzed_result['keywords'][name] = dict(nouns)

                    if 'total' in analyzed_result['keywords']:
                        for n in nouns.keys():
                            if n in analyzed_result['keywords']['total']:
                                analyzed_result['keywords']['total'][n] += nouns[n]
                            else:
                                analyzed_result['keywords']['total'][n] = nouns[n]
                    else:
                        analyzed_result['keywords']['total'] = dict(nouns)

        keywords_list = []
        for person in analyzed_result['keywords'].keys():
            keywords_list.append([person, Counter(analyzed_result['keywords'][person]).most_common(self.topKw)])

        analyzed_result['keywords'] = keywords_list

        analyzed_result['amount'] = sorted(list(Counter(analyzed_result['amount']).items()), key=lambda e: e[1], reverse=True)
        analyzed_result['emoticons'] = sorted(list(Counter(analyzed_result['emoticons']).items()), key=lambda e: e[1],
                                           reverse=True)
        analyzed_result['photos'] = sorted(list(Counter(analyzed_result['photos']).items()), key=lambda e: e[1],
                                           reverse=True)
        analyzed_result['hour'] = list(Counter(analyzed_result['hour']).items())

        return analyzed_result
