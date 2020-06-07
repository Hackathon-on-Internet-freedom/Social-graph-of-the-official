import argparse
import telebot
import pprint

from vkapi import verify_url, VkApiWrapper
from parser import Rater

_DEFAULT_REQ_FIELDS_PATH = 'req_fields.txt'

parser = argparse.ArgumentParser(description='Research vk page.')
parser.add_argument('--bot_token', type=str, required=True,
                    help=f'Telegram bot token (ex. 1112223334:AAABBBCC4CDDDEEEFFF455GGGH56HHI6IIJ)')
parser.add_argument('--vk_token', type=str, required=True,
                    help='VK dev token (ex. deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef)')
parser.add_argument('--req_fields_path', type=str, default=_DEFAULT_REQ_FIELDS_PATH,
                    help='path to a txt file with the list of profile fields to analyze')
args = parser.parse_args()

bot = telebot.TeleBot(args.bot_token)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Присылайте ссылку на профиль ВК – например, http://vk.com/id99398077 или https://vk.com/durov')


@bot.message_handler(content_types=['text'])
def find_closest_friends(message):
    vk_url = message.text
    if not verify_url(vk_url):
        bot.reply_to(message, 'Неверная ссылка на профиль! Попробуйте еще раз')
        return

    try:
        api = VkApiWrapper(vk_url, args.vk_token, args.req_fields_path)
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
