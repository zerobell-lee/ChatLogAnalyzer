
# ChatLogAnalyzer(카카오톡 채팅 로그 분석기)

## Overview

CLI 형태로 사용할 수 있는 카카오톡 채팅로그 분석기입니다.

다음과 같은 특징이 있습니다.

* CLI 형태로 작동합니다.
* Android/iOS에 따라 별도 지정하여 파싱합니다.
* 분석한 결과를 MySQL DB에 저장할 수 있습니다.
* DB에 적재하지 않고 바로 json으로 반환받을 수도 있습니다.

다음과 같은 **한계점**이 있습니다.

* mecab-ko이 설치된 환경에서만 올바르게 작동합니다. 설치 및 환경 구성은 [은전한닢님의 mecab-ko-dic 페이지](https://bitbucket.org/eunjeon/mecab-ko-dic)를 참조해주세요. 또한, Docker 환경에서 작동을 고려하고 계신다면 제가 제공하는 [mecab-ko](https://hub.docker.com/r/zerobell/mecab-ko) 이미지를 사용하셔도 됩니다.
* 오전/오후 시간 계산은 어디까지나 한글 기반입니다. 언어가 영어나 다른 외국어로 설정되어 있는 OS에서 추출한 채팅로그는 제대로 분석되지 않을 것입니다.

## Dependency

다음과 같은 라이브러리에 의존하고 있습니다.

* [PyMySQL](https://pypi.org/project/PyMySQL/)
* [python-mecab-ko](https://pypi.org/project/python-mecab-ko/)

## Install

아래의 설치 방법은 Ubuntu 기준으로 설명되었습니다.

<pre>$ git clone https://github.com/zerobell-lee/ChatLogAnalyzer.git
$ cd ChatLogAnalyzer
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip3 install -r requirements.txt
</pre>

## Return Value

어떤 모드로 사용하느냐에 따라 반환값이 다릅니다.

### JSON으로 바로 반환받을 경우

* amount : 각 대화자별로, 자신이 타이핑한 모든 글자수를 합한 총량값이 ['대화자', 대화량]의 쌍으로 이루어진 배열들로 표시됩니다. 기본적으로 대화량을 기준으로 내림차순 정렬되어 나타납니다.
* hour : 시간대별 대화량이 나옵니다. ['시간대(24시 기준)', 대화량]의 쌍으로 이루어진 배열들로 표시됩니다. 기본적으로 시간대를 기준으로 오름차순 정렬되어 나타납니다.
* keywords : 개인별 대화량이 나옵니다. 배열의 index마다 ['대화자', [키워드 배열]] 로 구성되어 있으며, 키워드 배열은 또한 내부에서 ['키워드', 키워드 언급 횟수]로 나타납니다. 기본적으로 키워드는 **상위 30**개만 표시되며, 이 또한 언급 횟수를 기준으로 내림차순 정렬되어 나타납니다.
* photos : '사진'을 가장 많이 보낸 사람의 이름이 들어갑니다.
* emoticons : '이모티콘'을 가장 많이 보낸 사람의 이름이 들어갑니다.

### MySQL에 저장하고 그 결과를 JSON으로 반환받을 경우

* result : MySQL 저장에 성공하였을 경우 "success"값이 반환됩니다.
* analyze_id : 분석된 결과가 저장된 테이블의 id를 받습니다. 이후 MySQL에 접속하여 amount + analyze_id, keywords + analyze_id, time + anlyze_id 에 select 문을 실행해보면 결과값들을 조회할 수 있습니다.

## Usage

### Default

<pre>$ venv/bin/python3 main.py KakaoTalkChats.txt
$ # 이 경우, 분석 OS는 Android로 설정되며, 분석 결과를 json 형태로 바로 반환합니다.</pre>

### Set OS

<pre>$ venv/bin/python3 main.py -s iOS KakaoTalkChats.txt
$ # 이 경우, 채팅 로그가 iOS에서 추출되었다고 간주하고 분석합니다. -s android 옵션도 가능하며, 생략할 경우 android로 자동 설정됩니다.
</pre>

### Use MySQL

<pre>$ venv/bin/python3 main.py -d -e host=localhost -e port=3306 -e uesr=root -e passwd=12341234 KakaoTalkChats.txt
</pre>

MySQL에 저장하는 옵션을 켜기 위해서는 <code>-d</code>를 붙여줍니다.
MySQL 계정에 대한 정보를 전달하기 위해서는 <code>-e</code>를 붙여줍니다. 이 뒤에는 '환경변수명'='변수값'의 형태로 전달시켜야 합니다.

아래와 같은 옵션들이 가능합니다.

* host : DB host 주소입니다. **필수항목입니다.**
* user : DB user 아이디입니다. **필수항목입니다.**
* passwd : DB user의 패스워드입니다. **필수항목입니다.**
* port : 접속 포트입니다. 기재하지 않을 경우 3306으로 자동 설정됩니다.

## To-DO

* 예시를 좀 더 알기 쉽게 스크린 샷 추가.
* 카카오톡 뿐 아니라, 라인에서도 사용 가능하도록 기능 추가
* 한국어가 아닌 OS에서 추출된 로그도 분석 가능하도록 변경