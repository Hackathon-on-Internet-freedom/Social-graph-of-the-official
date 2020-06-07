import argparse
import telebot
import pprint

from vkapi import VkApiWrapper
from parser import Rater

_DEFAULT_VK_ID = 129244038  # Алексей Навальный
_DEFAULT_OTHER_ID = 6  # Николай Дуров
_DEFAULT_TOKEN_PATH = 'token_example.txt'
_DEFAULT_REQ_FIELDS_PATH = 'req_fields.txt'

parser = argparse.ArgumentParser(description='Research vk page.')
parser.add_argument('--bot_token', type=str, required=True,
                    help=f'telegram bot token (ex. 1112223334:AAABBBCC4CDDDEEEFFF455GGGH56HHI6IIJ)')
parser.add_argument('--token_path', type=str, default=_DEFAULT_TOKEN_PATH,
                    help='path to a txt file with VK dev token')
parser.add_argument('--req_fields_path', type=str, default=_DEFAULT_REQ_FIELDS_PATH,
                    help='path to a txt file with the list of profile fields to analyze')
args = parser.parse_args()

bot = telebot.TeleBot(args.bot_token)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Присылайте ссылку на профиль ВК – например, http://vk.com/id99398077')


@bot.message_handler(content_types=['text'])
def find_closest_friends(message):
    vk_url = message.text
    # TODO: Добавить проверку корректности – регулярные выражения + пинг страницы профиля.
    pass
    # TODO: Получить ID из ссылки.
    vk_id = _DEFAULT_VK_ID

    try:
        api = VkApiWrapper(vk_id, args.token_path, args.req_fields_path)
        rater = Rater(api)
        friends = rater.get_friends()
        ratings = {}
        for friend in friends['items']:
            ratings[friend] = rater.rate(friend)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Что-то пошло не так :(')
        return

    # TODO: Сформировать ответ за запрос.
    reply_message = pprint.pformat(ratings)

    bot.reply_to(message, reply_message)


print('Bot started polling...')
bot.polling()
