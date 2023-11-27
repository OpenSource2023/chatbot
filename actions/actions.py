# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

# import mysql.connector
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import os

class ActionRecommendPlants(Action):
    def name(self) -> Text:
        return "action_recommend_plants"

    def recommend_plants(self, user_input: Text) -> List[Text]:
      
        # # MySQL 연결 설정
        # db_config = {
        #     'host': 'MYSQL_HOST',
        #     'user': 'MYSQL_USER',
        #     'password': 'MYSQL_PASS',
        #     'database': 'MYSQL_DATABASE'
        # }
        # conn = mysql.connector.connect(**db_config)

        # # 데이터베이스에서 데이터 불러오기
        # query = "SELECT * FROM plant_data"
        # plant_data = pd.read_sql_query(query, conn)

        # # 연결 닫기
        # conn.close()        
        
        # 식물 데이터 불러오기
        plant_data = pd.read_csv("plant_data.csv", encoding='euc-kr')

        # 추천된 식물 리스트 초기화
        recommended_plants = []

        # 사용자에게 추천할 식물 개수
        num_recommendations = 3

        # 사용자의 발화에서 추출한 entities에 대해 가중치 부여
        user_entities = {"place": 0, "water": 0, "size": 0, "formaldehyde": 0, "carbon_dioxide": 0, "negative_ion": 0, "relative_humidity": 0}

        # 사용자 발화에서 추출한 entities가 있을 경우 가중치 부여
        for index, entity in enumerate(user_entities.keys()):
            if entity in user_input:
                user_entities[entity] = 1 + 0.1 * index  # 먼저 나온 entity일수록 더 높은 가중치 부여

        # 추천할 식물들을 저장할 데이터프레임 생성
        recommendations = pd.DataFrame(columns=["plant", "score"])

        # 각 식물에 대해 점수 계산
        for index, plant in plant_data.iterrows():
            score = sum(user_entities[attr] * (1 if plant[attr] == user_entities[attr] else 0) for attr in user_entities)
            recommendations = recommendations.append({"plant": plant["plant"], "score": score}, ignore_index=True)

        # 이미 추천한 식물은 제외
        recommendations = recommendations[~recommendations["plant"].isin(recommended_plants)]

        # 점수가 높은 순으로 정렬하고 상위 n개 추천
        top_recommendations = recommendations.sort_values(by="score", ascending=False).head(num_recommendations)

        # 추천된 식물 리스트에 추가
        recommended_plants.extend(top_recommendations["plant"])

        return top_recommendations["plant"].tolist()

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # 사용자의 발화를 가져와서 추천 알고리즘에 전달
        user_input = tracker.latest_message.get("text", "")
        
        # 추천 알고리즘에 전달하여 추천 받기
        recommendations = self.recommend_plants(user_input)

        # 추천된 식물에 대한 메시지를 사용자에게 전송
        if recommendations:
            plant_list = ', '.join(recommendations)
            dispatcher.utter_message(text=f"다음 식물을 추천해 드립니다: {plant_list}.")
        else:
            dispatcher.utter_message(text="죄송합니다. 현재 조건에 맞는 식물을 찾을 수 없습니다.")

        return []
