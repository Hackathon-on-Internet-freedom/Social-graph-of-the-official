import telebot
import requests
bot = telebot.TeleBot('**yor bot key**')

keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('Найти человека', 'Помощь')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Доброго времени суток!\nЭтот бот призван найти связи людей.\nДля поиска введите строку типа:\n/research', reply_markup=keyboard1)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'Найти человека':
        bot.send_message(message.chat.id, 'Введите ссылку типа: vk.com/id111222333 или vk.com/durov')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Прощай, создатель')

def research(vk_url):
    pass

bot.polling()