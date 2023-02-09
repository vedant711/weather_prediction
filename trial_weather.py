import requests
import json

lat = '22.3072'
lon = '73.1812'
API_key = 'ddf2df38a550175470ef6bf036a717f7'
url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}'

r = requests.post(url)
resp_dict = r.json()
max_temp = resp_dict['main']['temp_max'] - 272
min_temp = resp_dict['main']['temp_min'] - 272
wind_speed = resp_dict['wind']['speed']
precipitation = resp_dict['main']['humidity']
# print(precipitation)

print(r.json())