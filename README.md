# chatbot
자연어 처리(rasa), 가중치 추천 알고리즘을 활용한 챗봇 서비스

# yaml 파일의 주석 처리 방법: # 

# 코드 작성 순서
rasa train: rasa 학습시키는 코드. 변경사항 후 학습시켜야 한다.
rasa run actions: rasa 서버 실행. 다른 cmd에 실행.
rasa shell --debug: 쉘에서 테스트할 때. debug 찍으면 오류 검출 가능.
rasa run --enable-api --cors "http://localhost:3000" --debug: rasa 서버 실행
rasa run -m --Model --enable-api --cors "http://localhost:3000" --debug: 이렇게도 쓰던데..

# 파일의 인코딩을 확인
#pip install chardet

import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']

file_path = 'C:\\Temp\\hywu_23_2\\singmul\\chatenv\\plant_data.csv'
encoding = detect_encoding(file_path)
print(f"The file's encoding is: {encoding}")


# nlu.yml


# domain.yml


# rules.yml


# stories.yml

# 필요하면 다시 붙이기