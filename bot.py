import argparse
import pprint

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram.ext.dispatcher import run_async

from vkapi import verify_url, VkApiWrapper
from parser import Rater


@run_async
def on_start(update, context):
    update.message.reply_text('Присылайте ссылку на профиль ВК – например, '
                              'http://vk.com/id99398077 или https://vk.com/durov')


@run_async
def on_text(update, context):
    vk_url = update.message.text
    if not verify_url(vk_url):
        update.message.reply_text('Неверная ссылка на профиль! Попробуйте еще раз', quote=True)
        return

    try:
        api = VkApiWrapper(vk_url, args.vk_token)
        rater = Rater(api)
        friends = rater.get_friends()
        ratings = {}
        for friend in friends['items']:
            ratings[friend] = rater.rate(friend)
    except Exception as e:
        print(e)
        update.message.reply_text('Что-то пошло не так :(', quote=True)
        return

    # TODO: Сформировать ответ за запрос.
    reply_message = pprint.pformat(ratings)

    update.message.reply_text(reply_message, quote=True)


def parse():
    parser = argparse.ArgumentParser(description='Research vk page.')
    parser.add_argument('--bot_token', type=str, required=True,
                        help=f'Telegram bot token (ex. 1112223334:AAABBBCC4CDDDEEEFFF455GGGH56HHI6IIJ)')
    parser.add_argument('--vk_token', type=str, required=True,
                        help='VK dev token (ex. deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse()

    updater = Updater(token=args.bot_token, use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', on_start))
    dispatcher.add_handler(MessageHandler(Filters.text, on_text))

    updater.start_polling()
    print('Bot started polling...')
