from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler
from telegram import Update
import requests
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime
import calendar
import locale


# Function to get weather from OpenWeatherMap
def get_weather(city):
    api_url = "http://api.openweathermap.org/data/2.5/weather?lang=ru&units=metric"
    params = {
        'q': city,
        'appid': '423bb88b1b2ab03957b4ac3e3bf2055a',
        'units': 'metric'
    }
    response = requests.get(api_url, params=params)
    weather_data = response.json()
    try:
        city_name = weather_data['name']
        weather = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        pressure = weather_data['main']['pressure']
        wind_speed = weather_data['wind']['speed']
        wind_direction = weather_data['wind']['deg']

        # Determine city coordinates for timezone
        city_lat = weather_data['coord']['lat']
        city_lon = weather_data['coord']['lon']

        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=city_lon, lat=city_lat)
        local_timezone = pytz.timezone(tz_name)  # Set the local time zone

        sunrise_time = datetime.utcfromtimestamp(weather_data['sys']['sunrise']).replace(tzinfo=pytz.utc).astimezone(
            local_timezone).strftime('%H:%M')
        sunset_time = datetime.utcfromtimestamp(weather_data['sys']['sunset']).replace(tzinfo=pytz.utc).astimezone(
            local_timezone).strftime('%H:%M')

        return f"Погода в {city_name}: {weather}\nТемпература: {temp}°C\nДавление: {pressure} hPa\nВетер: {wind_speed} м/с, направление {wind_direction}°\nЗакат: {sunset_time}, Восход: {sunrise_time}"
    except KeyError:
        return "Ошибка: не удалось получить информацию о погоде."


# Command /start, message_handler, main functions remain the same

# Command /start
# Command /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Я бот, который может предоставить тебе текущий прогноз погоды.\n"
        "Просто напиши мне название города, и я скажу тебе, какая погода сейчас там."
    )

# Function to handle messages


def message_handler(update: Update, context: CallbackContext):
    message_text = update.message.text.lower()
    if 'привет' in message_text or 'здравствуй' in message_text or 'дай' in message_text:
        start(update, context)
    else:
        update.message.reply_text("Ваш запрос обрабатывается⏳.")
        city = update.message.text
        weather_info = get_weather(city)
        city_tz_name = get_city_timezone(city)
    if city_tz_name:
        city_timezone = pytz.timezone(city_tz_name)
        current_time = datetime.now(city_timezone).strftime('%H:%M:%S')
        current_date = datetime.now(city_timezone).strftime('%d.%m.%Y')
        day_of_week_num = datetime.now(city_timezone).weekday()
        day_of_week_rus = calendar.day_name[day_of_week_num]
        current_time_utc = datetime.utcnow().strftime('%H:%M:%S')
        message = f"{weather_info}\n\nТекущая дата в {city}: {current_date},  {
            day_of_week_rus}\nТекущее время в {city}: {current_time}\nТекущее время в UTC: {current_time_utc}"
    else:
        message = f"Извините, не удалось получить информацию о временной зоне для {
            city}"

    update.message.reply_text(message)


# Function to get timezone for a given city
def get_city_timezone(city):
    api_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': '423bb88b1b2ab03957b4ac3e3bf2055a',
        'units': 'metric'
    }
    response = requests.get(api_url, params=params)
    weather_data = response.json()
    if 'coord' in weather_data:
        city_lat = weather_data['coord']['lat']
        city_lon = weather_data['coord']['lon']
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=city_lon, lat=city_lat)
        return tz_name
    else:
        return None

    # Get current time

# Main function


def main():
    bot_token = "6983252326:AAHLw_GtHfF2m7yw_qpGicLAyzKOZa4AEPU"
    updater = Updater(bot_token)

    dp = updater.dispatcher
    # Respond to any text message
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~
                   Filters.command, message_handler))
    dp.add_handler(MessageHandler(Filters.command, start))  # Handle commands

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
