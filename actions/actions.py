# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

#import mysql.connector
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import os

class ActionRecommendPlants(Action):
    def name(self) -> Text:
        return "action_recommend_plants"

    def recommend_plants(self, user_input: Text) -> List[Text]:
        
        # 사용자의 발화에서 추출한 entities에 대해 가중치 부여
        user_entities = {"place": 0, "water": 0, "size": 0, "formaldehyde": 0, "carbon dioxide": 0, "negative ion": 0, "relative humidity": 0}

        # 사용자 발화에서 추출한 entities가 있을 경우 가중치 부여
        for index, entity in enumerate(user_entities.keys()):
            if entity in user_input:
                user_entities[entity] = 1 + 0.1 * index  # 먼저 나온 entity일수록 더 높은 가중치 부여

        # CSV 파일을 읽기
        plant_data = pd.read_csv("C:\\Temp\\hywu_23_2\\singmul\\chatenv\\plant_data.csv", encoding='euc-kr')
        
        # 열 이름에서 앞뒤 공백을 제거
        plant_data.columns = [col.strip() for col in plant_data.columns]

        # 추천된 식물 리스트 초기화
        recommended_plants = []

        # 사용자에게 추천할 식물 개수
        num_recommendations = 3

        # 추천할 식물들을 저장할 데이터프레임 생성
        recommendations = pd.DataFrame(columns=["plant", "score"])

        # 각 식물에 대해 점수 계산
        for index, plant in plant_data.iterrows():
            print(f"Plant keys: {plant.keys()}")
            print(f"User entities keys: {user_entities.keys()}")
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
        
        # debugging
        print("ActionRecommendPlants is executed.")
        
        # 사용자의 발화를 가져와서 추천 알고리즘에 전달
        user_input = tracker.latest_message.get("text", "")
        print(user_input)
        
        # 추천 알고리즘에 전달하여 추천 받기
        recommendations = self.recommend_plants(user_input)
        print(recommendations)

        # 추천된 식물에 대한 메시지를 사용자에게 전송
        if recommendations:
            plant_list = ', '.join(recommendations)
            print(plant_list)
            dispatcher.utter_message(text=f"다음 식물을 추천해 드립니다: {plant_list}.")
        else:
            dispatcher.utter_message(text="죄송합니다. 현재 조건에 맞는 식물을 찾을 수 없습니다.")

        return []

'''
class RespondToUserIntent(Action):
    def name(self) -> Text:
        return "respond_to_user_intent"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 최근 메시지에서 사용자 의도 추출
        intent = tracker.latest_message['intent'].get('name')

        # 사용자 의도에 따라 다른 응답 생성
        if intent == '시작_인사':
            dispatcher.utter_message("안녕하세요! 어떻게 도와드릴까요?")
        elif intent == '종료_인사':
            dispatcher.utter_message("안녕히 가세요! 다음에 또 도움이 필요하시면 오세요.")
        elif intent == '사용자_요구':
            dispatcher.utter_message("무엇을 원하시나요?")
        elif intent == '긍정':
            dispatcher.utter_message("감사합니다! 도움이 필요하신 경우 언제든 물어봐주세요.")
        elif intent == '부정':
            dispatcher.utter_message("죄송해요. 다른 방법으로 도움을 드리고 싶어요. 무엇이 문제인지 말해주시겠어요?")
        else:
            dispatcher.utter_message("죄송합니다. 이해할 수 없는 요청이에요.")

        return []
'''