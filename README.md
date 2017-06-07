# 글로벌스누

Note: **NOT suitable for production.** Migration to Django 1.11 (from 1.9) in
process. Also rewriting some parts. (FYI, `globalsnu.com` currently runs on a
different version.)


## Intro

글로벌스누는 서울대학교에서 교환학생 혹은 스누인월드 프로그램을 준비하는 분들을 위한
정보 공유 사이트입니다. 교환학생, 스누인월드 프로그램에 지원해 보고 싶지만 어디서부터
준비해야 할지 모르셨던 분들, 관심 있는 지역의 학교, 나의 전공을 제공하는 학교들에 대해
더 알아보고 싶으신 분들, 소소하고 즐거운 수기를 읽어 보고 싶으신 분들, 또 그런 수기를
남겨 보고 싶으신 분들, 그리고 해외의 대학에 관심이 있는 학우분들을 위해 서울대학교와
협정을 체결한 모든 해외 대학들에 대한 정보를 담아내는 것이 저희의 목표입니다. 저희의
목표에 공감해 주시는 분들께서 남기시는 위키 한 줄, 수기 한 페이지가 모여 나와 다른
분들에게 더 큰 세계를 선물해 줄 것이라고 믿습니다. 더 많은 분들이 글로벌스누를 통해
세계를 향한 꿈을 키우고 이뤄 나가시길 바랍니다:)


## Setup

### Windows

1. Clone repository
2. `$ cd globalsnu`
3. `$ python -m venv venv`
4. `$ venv\Scripts\activate`
5. `$ pip install -r requirements.txt`


## Applications Reference

### core (`globalsnu.core`)

글로벌스누 프로젝트의 중앙 기능들을 담당하는 앱. 홈과 같은 공통적 페이지에 대한 뷰와,
mail/urlresolvers 등 여러 앱에서 두루 사용되는 기능들을 포함한다.

### auth_ (`globalsnu.auth`)

유저와 관련된 기능들을 담당하며 `django.contrib.auth`의 모델을 일부 대체한다. 이
프로젝트에서는 커스텀 유저를 사용하므로 User 대신 `settings.AUTH_USER_MODEL`을
필히 사용하여야 한다. `django.contrib.auth`와의 네임스페이스 충돌을 피하기 위해
auth_로 명명하였다.

### wiki (`globalsnu.wiki`)

공동편집이 가능한 위키 앱으로 프로젝트에서 가장 핵심이 된다.

`class Wiki`: 언어별 위키. 위키피디아가 언어별로 독립된 페이지 리스트를 갖듯이 여러
독립된 위키가 병존할 수 있도록 확장 가능성을 염두에 두었다.

`class Page`: 문서 페이지. 위키의 특성상 히스토리를 관리해야 하기 때문에 리비전들의
컨테이너 역할을 한다. current_revision이라는 OneToOneField를 통해 정보를 불러온다.

`class PageRevision`: 위 Page의 실질적인 정보를 담는다.

`class Essay`: 수기와 인터뷰. Page에 링크되는 형태로만 생성이 가능하며 Page와 달리
개인에게 소유권과 편집권이 주어진다.

`class External`: 외부 문서들과 연결하는 기능을 한다.

### univ (`globalsnu.univ`)

wiki의 Page에 의존하는 모델들을 포함하는 앱으로, 학교 Page와 국가 Page에 대하여
부가적인 정보를 담거나 별도의 템플릿을 불러올 수 있도록 한다. 학교에 대해서 '좋아요'를
할 수 있다.


## Compatible Packages

### Core

* Python 3.5.3
* Elasticsearch 2.4.5

### Python Packages

* Django 1.11.1
* BeautifulSoup 4.6.0
* Django Compressor 2.1.1
* Django Haystack 2.6.1
* django-mobile 0.7.0 (Note: check `postdeployment.txt`)
* django-widget-tweaks 1.4.1
* lxml 3.7.3
* Markdown 2.6.8
* Pillow 4.1.1
* Requests 2.14.2
* SlimIt 0.8.1

### Miscellaneous

* Bootstrap 3.3.7
* jQuery 3.2.1
* marked 0.3.6
* Trumbowyg 2.5.1
