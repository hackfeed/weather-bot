import os

import vk_api
import pyowm
import pymorphy2
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from dotenv import load_dotenv

import meta

load_dotenv()

vk = vk_api.VkApi(token=os.getenv("TOKEN_VK"))
owm = pyowm.OWM(API_key=os.getenv("TOKEN_OWM"), language="ru")
morph = pymorphy2.MorphAnalyzer()
longpoll = VkLongPoll(vk)


def get_wind_direction(degrees):
    if 351 <= degrees <= 360 or 0 <= degrees <= 10:
        return "Северный"
    if 11 <= degrees <= 80:
        return "Северно-Восточный"
    if 81 <= degrees <= 100:
        return "Восточный"
    if 101 <= degrees <= 170:
        return "Юго-Восточный"
    if 171 <= degrees <= 190:
        return "Южный"
    if 191 <= degrees <= 260:
        return "Юго-Западный"
    if 261 <= degrees <= 280:
        return "Западный"
    if 281 <= degrees <= 350:
        return "Северо-Западный"


def get_weather(place):
    place = morph.parse(place)[0].normal_form.capitalize()

    location = owm.weather_at_place(place)
    weather = location.get_weather()

    time = f"{weather.get_reference_time('date').strftime('%d.%m.%Y %H:%M')} UTC"
    temperature = f"{weather.get_temperature('celsius')['temp']}°С"
    wind = f"{weather.get_wind()['speed']} м/c"
    wind_dir = get_wind_direction(weather.get_wind()['deg'])
    humidity = f"{weather.get_humidity()}%"

    weather_msg = f"☁️ Погода в городе {place}\n\n" \
        f"⌚ Время измерения: {time}\n" \
        f"🌡️ Температура воздуха: {temperature}\n" \
        f"🎐 Cкорость ветра: {wind}, направление: {wind_dir}\n" \
        f"🌊 Влажность воздуха: {humidity}"

    return weather_msg


def send_message(user_id, message):
    vk.method("messages.send", {
        "user_id": user_id,
        "message": message,
        "random_id": get_random_id()
    })


def listen_events(poll):
    for event in poll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                msg_text = event.text.lower().strip(meta.STRIP_CHARACTERS)

                if msg_text in meta.WELCOME_MESSAGES:
                    send_message(event.user_id, meta.BOT_MESSAGE)
                elif msg_text.startswith(tuple(meta.WEATHER_MESSAGES)):
                    city = msg_text

                    for msg in meta.WEATHER_MESSAGES:
                        if city.startswith(msg):
                            city = city[len(msg):]
                            break

                    try:
                        city = city.split()[0]
                    except IndexError:
                        send_message(event.user_id, meta.CITY_NOT_FOUND_ERROR)
                        continue

                    city_normalized = morph.parse(city)[0].normal_form

                    try:
                        weather = get_weather(city_normalized)
                        send_message(event.user_id, weather)
                    except pyowm.exceptions.api_response_error.NotFoundError:
                        send_message(event.user_id, meta.CITY_NOT_FOUND_ERROR)
                else:
                    send_message(event.user_id, meta.CMD_ERROR)


if __name__ == "__main__":
    listen_events(longpoll)
