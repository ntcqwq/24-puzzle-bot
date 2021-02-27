import random, os, TwPoint
from telegram.ext import Dispatcher,CommandHandler, MessageHandler, Filters, Updater
from telegram import BotCommand

def read_file_as_str(file_path):
    if not os.path.isfile(file_path):
        raise TypeError(file_path + " does not exist")
    all_the_text = open(file_path).read()
    return all_the_text
             
TOKEN=read_file_as_str('24TOKEN')
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

commands = TwPoint.add_handler(dispatcher)
updater.bot.set_my_commands(commands)

updater.start_polling()
print('Started')
updater.idle()
print('Stopping...')
print('Stopped.')