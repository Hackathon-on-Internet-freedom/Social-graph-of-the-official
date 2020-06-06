import telebot
import argparse

parser = argparse.ArgumentParser(description='Research vk page.')
parser.add_argument('key', type=str, help='type a secret telegram bot id, like 1112223334:AAABBBCC4CDDDEEEFFF455GGGH56HHI6IIJ')
args = parser.parse_args()
bot_key= args.key

bot = telebot.TeleBot(bot_key)
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    splitted_message = message.text.split(' ')
    if splitted_message[0] == "/start":
        bot.send_message(message.from_user.id, "Доброго времни суток, вас приветствует бот для помощи в составлении досье на человека. Введте /help для помощи.")
    elif  splitted_message[0] == "/research":
        bot.send_message(message.from_user.id, " ".join(splitted_message))
    elif splitted_message[0] == "/help":
        bot.send_message(message.from_user.id, "Введите /research vk.com/durov или vk.com/id111222333, для помощи в составлении досье.")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")
    bot.polling(none_stop=True, interval=0)
get_text_messages()
