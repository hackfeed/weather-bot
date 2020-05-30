import os

import vk_api
import pyowm
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from dotenv import load_dotenv

load_dotenv()

vk = vk_api.VkApi(token=os.getenv("TOKEN_VK"))
owm = pyowm.OWM(API_key=os.getenv("TOKEN_OWM"), language="ru")
longpoll = VkLongPoll(vk)


def send_message(user_id, message):
    vk.method("messages.send", {
        "user_id": user_id,
        "message": message,
        "random_id": get_random_id()
    })


def get_weather(place):
    location = owm.weather_at_place(place)
    weather = location.get_weather()

    weather_msg = f"Погода в городе {place}, время {weather.get_reference_time('iso')}. Температура воздуха - " \
        f"{weather.get_temperature('celsius')['temp']}, скорость ветра - {weather.get_wind()['speed']}, " \
        f"влажность воздуха - {weather.get_humidity()}."

    return weather_msg


if __name__ == "__main__":
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                msg_text = event.text

                if msg_text.lower() == "привет":
                    send_message(event.user_id, "Привет!!!")

                if msg_text.lower().startswith("скажи погоду в"):
                    city = msg_text.split()[3]
                    send_message(event.user_id, get_weather(city))
