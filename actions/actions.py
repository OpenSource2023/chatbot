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

    def recommend_plants(self, user_entity_list: Text) -> List[Text]:
        
        print(f"사용자 발화 중 나온 entity: {user_entity_list}\n")
        
        # 사용자의 발화에서 추출한 entities에 대해 가중치 부여
        user_entities = {"place": 0, "water": 0, "size": 0, "formaldehyde": 0, "carbonDioxide": 0, "negativeIon": 0, "relativeHumidity": 0}

        # 사용자 발화에서 추출한 entities가 있을 경우 가중치 부여
        for index, entity in enumerate(user_entities.keys()):
            if entity in user_entity_list:
                print(f"{entity}가 {user_entity_list}안에 있습니다.\n")
                print(f"user_entities[entity]: {user_entities[entity]}\n")
                user_entities[entity] = 10 - 1 * (index+1)  # 먼저 나온 entity일수록 더 높은 가중치 부여
            else:
                print(f"{entity}가 {user_entity_list}안에 없습니다.\n")
        
        # CSV 파일을 읽기
        plant_data = pd.read_csv("C:\\Temp\\hywu_23_2\\singmul\\chatenv\\plant_data.csv", encoding='utf-8')
        
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
            print(f"csv의 열 이름: \n{plant.keys()}\n")
            print(f"user_entities의 keys: \n{user_entities.keys()}\n")
            print(f"user_entities의 values: \n{user_entities.values()}\n")

            # 각 엔터티에 대해 사용자 입력과 식물 데이터가 일치하면 1을 더하고, 일치하지 않으면 0을 더하여 스코어를 계산
            score = sum(user_entities[attr] * (1 if plant[attr] == user_entities[attr] else 0) for attr in user_entities)
            
            # 식물 name과 score를 가지는 DataFrame 생성 후, recommendations에 추가
            recommendations = pd.concat([recommendations, pd.DataFrame({"plant": [plant["name"]], "score": [score]})], ignore_index=True)
            
            print(f"식물 이름: {plant['name']}, \nScore: {score}\n")

        # 이미 추천한 식물은 제외
        recommendations = recommendations[~recommendations["plant"].isin(recommended_plants)]

        # 점수가 높은 순으로 정렬하고 상위 n개 추천
        top_recommendations = recommendations.sort_values(by="score", ascending=False).head(num_recommendations)

        # 추천된 식물을 리스트에 추가
        recommended_plants.extend(top_recommendations["plant"])

        # 필요한 컬럼만 선택하여 반환
        selected_columns = ['photo', 'name', 'place', 'water', 'size', 'formaldehyde',
                             'carbonDioxide', 'negativeIon', 'relativeHumidity']
        
        recommended_plants_details = plant_data[plant_data["name"].isin(recommended_plants)][selected_columns].to_dict(orient='records')

        # 추천된 식물들의 상세 정보 반환
        return recommended_plants_details

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # 사용자의 발화를 가져오기
        user_input = tracker.latest_message.get("text")
        print(f"사용자의 발화: {user_input}\n")
        
        # 사용자의 발화에서 entity 추출
        user_entity_list = list(set(entity["entity"] for entity in tracker.latest_message["entities"]))
        print(f"사용자의 entity: {user_entity_list}\n")
        
        # 추천 알고리즘에 전달하여 추천 받기
        recommendations = self.recommend_plants(user_entity_list)
        print(f"사용자 메시지에 따른 recommend_plants 함수 결과: \n{recommendations}\n")

        # 추천된 식물에 대한 메시지를 사용자에게 전송
        if recommendations:
                        
            # 사용자에게 전송할 텍스트 생성
            message_text = ""
            for idx, plant_info in enumerate(recommendations):
                message_text += f"{idx+1}번째 식물: {plant_info['name']}\n"
                message_text += f"추천 장소: {plant_info['place']}\n"
                message_text += f"물 주기: {plant_info['water']}\n"
                message_text += f"크기: {plant_info['size']}\n"
                message_text += f"포름알데히드 제거 수치: {plant_info['formaldehyde']}\n"
                message_text += f"이산화탄소 제거 수치: {plant_info['carbonDioxide']}\n"
                message_text += f"음이온 발생량: {plant_info['negativeIon']}\n"
                message_text += f"상대습도: {plant_info['relativeHumidity']}\n\n"

            dispatcher.utter_message(text=f"다음 식물을 추천해 드립니다: \n{message_text}")
        else:
            print("식물 추천 실패")
            dispatcher.utter_message(text="죄송합니다. 현재 조건에 맞는 식물을 찾을 수 없습니다.")
            
            return []
