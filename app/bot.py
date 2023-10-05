from pathlib import Path
import datetime
import telebot
from configparser import ConfigParser
import prometheus_client
import logging
import argparse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


parser = argparse.ArgumentParser(description="You can run this script locally, using flag --alexmode or -d",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--alexmode", action="store_true", help="Developer mode")
parser.add_argument("-m", "--karinamode", action="store_true", help="Developer mode macos")
args = parser.parse_args()
config = vars(args)


alexmode = config['alexmode']
karinamode = config['karinamode']
if alexmode:
    logging.basicConfig(filename="..\\logs\\budget_bot.log",
                        level=logging.INFO)
elif karinamode:
    logging.basicConfig(filename="/Users/karina/PycharmProjects/budget_bot/logs/budget_bot.log",
                        level=logging.INFO)
else:
    logging.basicConfig(filename="/budget_bot/logs/budget_bot.log", level=logging.INFO)
using_bot_counter = prometheus_client.Counter(
    "using_bot_count",
    "request to the bot",
    ['method', 'user_id', 'username']
)

parser = ConfigParser()
if alexmode:
    parser.read(Path('..\\config\\init.ini').absolute())
elif karinamode:
    parser.read(Path('/Users/karina/PycharmProjects/budget_bot/config/init.ini').absolute())
else:
    parser.read(Path('/budget_bot/config/init.ini').absolute())
telegram_api_token = parser['telegram']['telegram_api_token']
bot = telebot.TeleBot(token=telegram_api_token)



if alexmode:
    role_model_path: Path = Path(f"C:\\Users\\amalinko\\PycharmProjects\\budget_bot\\config\\role_model.txt").absolute()
elif karinamode:
    role_model_path: Path = Path(f"/Users/karina/PycharmProjects/budget_bot/config/role_model.txt").absolute()
else:
    role_model_path: Path = Path(f"/budget_bot/config/role_model.txt").absolute()

access_denied_message = "Для использоавания бота Вы должны быть добавлены в ролевую модель"


def check_access_rights(role_model_file, username):
    with open(role_model_file, "r") as stream:
        all_user = stream.read()
    if username in all_user:
        return True
    return False


def bot_monitoring(message):
    using_bot_counter.labels(message.text, message.from_user.id, message.from_user.full_name).inc()


def bot_logging(message):
    pass
    logging.info(
        f"{datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}. "
        f"{message.text},"
        f" {message.from_user.id},"
        f" {message.from_user.full_name}"
    )
    print("lalala")


@bot.message_handler(commands=['test'])
def add_question_message(message):
    bot_logging(message)
    bot_monitoring(message)
    if not check_access_rights(role_model_file=role_model_path, username=f"@{message.chat.username}"):
        bot.send_message(
            message.chat.id,
            access_denied_message
        )
        return 0
    bot.send_message(
        message.chat.id,
        "Тест",
    )

if __name__ == '__main__':
    prometheus_client.start_http_server(9300)
    bot.infinity_polling()