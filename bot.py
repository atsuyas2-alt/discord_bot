import os
import requests 
from dotenv import load_dotenv
import logging

load_dotenv()
api_key=os.getenv('WEATHER_API_KEY')
url=os.getenv('DISCORD_WEBHOOK_URL')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log',encoding='utf-8')
    ]
    )





def send_to_discord(city_name_variable,temp_variable,temp_feel_variable,humidity_variable,windspeed_variable,weather_variable,image_data_variable):
    
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
        logging.info('success')
    else:
        
        logging.error(f'discord sending failure:エラーコード{post_response.status_code}')



city_name=os.getenv("CITY_NAME", "Kanazawa")

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
    
else:
    logging.error(f'api get failuer:{response.status_code}')
    