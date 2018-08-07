import MeCab

class WordAnalyzer():
    def __init__(self, dic='/usr/local/lib/mecab/dic/mecab-ko-dic'):
        self.dic = dic
        self.m = MeCab.Tagger('-d ' + dic)
    def filter(self, source, filter, exception=[]):
        result = []
        flag = False
        node =  self.m.parseToNode(source)
        while node.next!=None:
            node = node.next
            try:
                surface = node.surface
                feature = node.feature.split(',')[0].split('+')[0]
                if feature in filter:
                    if feature=='VV' or feature=='VA':
                        if node.feature.split(',')[-1].split('/')[0]!='*':
                            surface = node.feature.split(',')[-1].split('/')[0] + '다'
                        else:
                            surface = surface + '다'
                    elif 'NN' in feature:
                        surface = node.feature.split(',')[3]
                    if surface=='잣다':
                        surface='자다'
                    elif surface[0]=='ㅋ':
                        surface = 'ㅋㅋ'
                    elif surface[0]=='ㅎ':
                        surface = 'ㅎㅎ'
                    elif surface[0]=='ㅠ':
                        surface = 'ㅠㅠ'
                    if surface not in exception:
                        result.append((surface, feature))
            except UnicodeDecodeError as e:
                pass
            except IndexError as e:
                print(e, node.surface, node.feature)
        return result
 
