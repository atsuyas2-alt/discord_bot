import os
import requests 
from dotenv import load_dotenv
import logging
import time
from todo_db_class import Task,TaskRepository
from datetime import datetime,timezone,timedelta

load_dotenv()
api_key=os.getenv('WEATHER_API_KEY')
url=os.getenv('DISCORD_WEBHOOK_URL')
todo_db=os.getenv('DB_NAME')
db_url = os.getenv("TURSO_DATABASE_URL")
db_token = os.getenv("TURSO_AUTH_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log',encoding='utf-8')
    ]
    )





def send_to_discord(city_name_variable,temp_variable,temp_feel_variable,humidity_variable,windspeed_variable,weather_variable,image_data_variable):

    for i in range(3): 
        try:   
            #discordに送るデータ
            embed_data={
                'title':'⛅ 現在の天気情報',
                'color':16711680,
                'fields':[
                    {'name':'都市名','value':f'{city_name_variable}','inline':True},
                    {'name':'気温','value':f'{temp_variable}℃','inline':True},
                    {'name':'体感温度','value':f'{temp_feel_variable}℃','inline':True},
                    {'name':'風速','value':f'{windspeed_variable}m/s','inline':True},
                    {'name':'湿度','value':f'{humidity_variable}%','inline':True},
                    {'name':'天気','value':f'{weather_variable}','inline':True},
                ],
                'thumbnail':{'url':image_data_variable}
            }
            payload={'embeds':[embed_data]}

            post_response=requests.post(url,json=payload)
            if post_response.status_code==204:
                logging.info('wether success')
                break
                
            else:
                
                logging.error(f'discord sending failure:エラーコード{post_response.status_code}')
                time.sleep(3)
        except requests.exceptions.RequestException as e:
            logging.error(f'api connect failuer:{e}')
            time.sleep(3)
    else:
        logging.warning('discord send 3times failuer')


city_name=os.getenv("CITY_NAME", "Kanazawa")
for i in range(3):
    
    
    try:
        api_endpoint= f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
        response=requests.get(api_endpoint)

        if response.status_code ==200:
            weather_data=response.json()
            #print(weather_data)
            
            temp_data= weather_data['main']['temp']
            temp_feel_data=weather_data["main"]['feels_like']
            humidity_data=weather_data['main']['humidity']
            windwpeed_data=weather_data['wind']['speed']
            weather_data_weather = weather_data['weather'][0]['main']
            image_data=weather_data['weather'][0]['icon']

            image_data_url=f'https://openweathermap.org/img/wn/{image_data}@2x.png'

            send_to_discord(city_name,temp_data,temp_feel_data,humidity_data,windwpeed_data,weather_data_weather,image_data_url)
            logging.info('success')
            break

        else:       
            logging.error(f'api get failuer:{response.status_code}')
            time.sleep(3)

    except requests.exceptions.RequestException as e:
        logging.error(f'api connect failuer:{e}')
        time.sleep(3)

else:
    logging.warning('api get 3times failuer')


#todo integration
jst=timezone(timedelta(hours=9))
today=datetime.now(jst).strftime('%Y-%m-%d')
repo=TaskRepository(db_url)

task_today_incomplete=repo.get_due_today_incomplete(today)



for i in range(3):
        try: 
            if task_today_incomplete:
                field_list=[]
                for t in task_today_incomplete:
                    task_name=t.name
                    task_state=t.state
                    task_deadline=t.deadline
                    field_list.append({'name':f'name:{task_name}',
                     'value':f'state:{task_state}/deadline:{task_deadline}',
                     'inline':True})

            #discordに送るデータ
                embed_data={
                    'title':'今日締め切りのtodoリスト',
                    'fields':field_list,
                    }

            else:
                embed_data={
                'title':'今日締め切りのtodoリスト',
                'fields':[
                     {'name':'todoお知らせ','value':'今日締め切りのタスクはありません','inline':True}
                ],
                }
            payload={'embeds':[embed_data]}

            post_response=requests.post(url,json=payload)
            if post_response.status_code==204:
                logging.info('todo success')
                break
                
            else:
                
                logging.error(f'discord sending failure:エラーコード{post_response.status_code}')
                time.sleep(3)
        except requests.exceptions.RequestException as e:
            logging.error(f'discord connect failuer:{e}')
            time.sleep(3)
else:
    logging.warning('discord send 3times failuer')
repo.close()