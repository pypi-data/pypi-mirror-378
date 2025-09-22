# Python Selenium을 이용한 chrome, FireFox wrapper

# 동작확인
(ok) python ebay-rank.py :: 자동으로 크롬드라이버를 받는 방식으로 잘 작동함.


## 가상환경 들어가기
pkywebdriver.bat

## 관련 패키지 설치
pip install -r requirements.txt

## 관련 패키지 저장
pip freeze > requirements.txt

## 파이썬 패키지를 로컬에서 테스트하는 방법

1) 패키지 루트 폴더로 이동
2) python setup.py develop
3) pip list로 확인

참조: 
https://velog.io/@hsbc/python-setup.py
https://data-newbie.tistory.com/770


## 실행방법
python ebay-rank.py


## 패키지 배포
로컬패키지를 github에 올리면 깃허브에서 자동을 PyPi사이트로 등록한다.

git add .  
git commit -m   
git tag v0.0.1  
git push origin <tag_number> 
