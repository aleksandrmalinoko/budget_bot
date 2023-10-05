from pathlib import Path
import datetime
import telebot
from configparser import ConfigParser
import prometheus_client
import logging
import argparse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


parser = argparse.ArgumentParser(description="You can run this script locally, using flag --devmode or -d",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--devmode", action="store_true", help="Developer mode")
parser.add_argument("-m", "--macmode", action="store_true", help="Developer mode macos")
args = parser.parse_args()
config = vars(args)


devmode = config['devmode']
macmode = config['macmode']
if devmode:
    logging.basicConfig(filename="..\\logs\\budget_bot.log",
                        level=logging.INFO)
elif macmode:
    logging.basicConfig(filename="../logs/budget_bot.log",
                        level=logging.INFO)
else:
    logging.basicConfig(filename="/budget_bot/logs/budget_bot.log", level=logging.INFO)
using_bot_counter = prometheus_client.Counter(
    "using_bot_count",
    "request to the bot",
    ['method', 'user_id', 'username']
)

parser = ConfigParser()
if devmode:
    parser.read(Path('C:\\Users\\amalinko\\PycharmProjects\\budget_bot\\config\\init.ini').absolute())
elif macmode:
    parser.read(Path('/Users/aleksandrmalinko/PycharmProjects/budget_bot/config/init.ini').absolute())
else:
    parser.read(Path('/budget_bot/config/init.ini').absolute())
telegram_api_token = parser['telegram']['telegram_api_token']
bot = telebot.TeleBot(token=telegram_api_token)

if devmode:
    faq_path: Path = Path(f"C:\\Users\\amalinko\\PycharmProjects\\budget_bot\\config\\faq.yaml").absolute()
elif macmode:
    faq_path: Path = Path(f"/Users/aleksandrmalinko/PycharmProjects/budget_bot/config/faq.yaml").absolute()
else:
    faq_path: Path = Path(f"/budget_bot/config/faq.yaml").absolute()


if devmode:
    role_model_path: Path = Path(f"C:\\Users\\amalinko\\PycharmProjects\\budget_bot\\config\\role_model.txt").absolute()
elif macmode:
    role_model_path: Path = Path(f"/Users/aleksandrmalinko/PycharmProjects/budget_bot/config/role_model.txt").absolute()
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

