from flask import Flask, request
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import pickle
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'
MAIN_SERVER_URL = 'http://main_server_ip:5000'
SERVER_MENU_FILE = 'server_menu.pkl'

# بارگیری دیکشنری از فایل در ابتدای اجرا
def load_server_menu():
    if os.path.exists(SERVER_MENU_FILE):
        with open(SERVER_MENU_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

server_menu = load_server_menu()  # بارگیری دیکشنری از فایل

# تابع ذخیره دیکشنری در فایل
def save_server_menu():
    with open(SERVER_MENU_FILE, 'wb') as f:
        pickle.dump(server_menu, f)

def start(update, context):
    update.message.reply_text('Welcome to the Server Monitoring Bot!')

def status(update, context):
    keyboard = []
    for server_name in server_menu.keys():
        keyboard.append([
            InlineKeyboardButton(server_name, callback_data=server_name),
            InlineKeyboardButton("Reboot", callback_data=f'reboot_{server_name}')
        ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Select a server:', reply_markup=reply_markup)

# ...

def button(update, context):
    query = update.callback_query
    query.answer()

    server_name = query.data
    keyboard = [
        [InlineKeyboardButton("Check Server Status", callback_data=f'check_{server_name}')],
        [InlineKeyboardButton("Reboot", callback_data=f'reboot_{server_name}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f'Select an option for {server_name}:', reply_markup=reply_markup)

def get_server_status(update, context):
    query = update.callback_query
    query.answer()

    server_name = query.data.replace('check_', '')  # حذف پیشوند 'check_' از دیتا
    url = f'{MAIN_SERVER_URL}/get_server_status'
    data = {'server_name': server_name}
    response = requests.get(url, params=data)
    status_message = response.text
    context.bot.send_message(chat_id=query.message.chat_id, text=status_message)

def reboot_server(update, context):
    query = update.callback_query
    query.answer()

    server_name = query.data.replace('reboot_', '')  # حذف پیشوند 'reboot_' از دیتا
    url = f'{MAIN_SERVER_URL}/reboot_server'
    data = {'server_name': server_name}
    response = requests.post(url, json=data)
    reboot_message = response.text
    context.bot.send_message(chat_id=query.message.chat_id, text=reboot_message)

def register(update, context):
    data = request.get_json()
    server_info = data.get('server_info')
    server_name = server_info.split('@')[0]

    if server_name not in server_menu:
        server_menu[server_name] = True
        save_server_menu()  # ذخیره دیکشنری در فایل
        update.message.reply_text(f'Server {server_name} registered successfully.')
    else:
        update.message.reply_text(f'Server {server_name} is already registered.')

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CallbackQueryHandler(get_server_status, pattern=r'^check_[^@]+$'))
    dp.add_handler(CallbackQueryHandler(reboot_server, pattern=r'^reboot_[^@]+$'))
    dp.add_handler(CommandHandler("register", register))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
