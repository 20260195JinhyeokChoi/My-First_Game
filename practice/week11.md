# Week 11 실습

## 오늘 한 것
- PyInstaller 설치 및 빌드
- resource_path() 함수 추가
- --add-data 옵션으로 에셋 포함
- .exe 실행 확인

## resource_path() 를 써야 하는 이유
기존의 상대경로는 게임 코드 기준이고 빌드 파일 기준이 아니기에 이것을 병합하는 과정이 필요하다. 때문에 경로를 통일해줘야 하고, 그게 resource_path()다.

## 빌드 명령어
pyinstaller --onefile --windowed --add-data "sounds;sounds" --add-data "sprites;sprites" middle_invaderBreaker.py

## AI 활용 내역
파이인스톨러를 설치하는 법
콘솔 없이 간편하게 빌드하는 법(미적용)
콘솔로 빌드할때 쓰는 코드
sys._MEIPASS 및 resource_path() 적용법