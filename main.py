import logging
import sqlite3
from random import choice
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from telegram.ext import CommandHandler
from mail import anons_history, take_history

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
con = sqlite3.connect("users.db")
cur = con.cursor()


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_images(url):
    urls = []
    html_page = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    html = BeautifulSoup(html_page.content, "html.parser")
    for img in html.find_all("img"):
        img_url = img.attrs.get("src")
        if not img_url:
            continue
        img_url = urljoin(url, img_url)
        if is_valid(img_url):
            urls.append(img_url)
    return urls


cats = get_all_images("https://yandex.ru/images/search?text=котик в одуванчиках")


cats0 = ["Ты котик в одуванчиках)", "Ты молодец!", "У тебя все получится!",
         "Ты мой одуванчик)", "Ты чудо!", "Даже этот котик не такой милык как ты)",
         "Улыбайся чаще, тебе очень идет)"]
logger = logging.getLogger(__name__)


async def echo(update, context):
    await context.bot.sendPhoto(chat_id=update.message.chat.id, photo=
    choice(cats), caption=choice(cats0))
    user = update.effective_user
    variant = context.user_data['variant']
    if variant and not context.user_data['read'][variant]:
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data='3'), InlineKeyboardButton("Нет", callback_data='4')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Вы уже закончили данную историю,'
                                        ' желаете начать заново?', reply_markup=reply_markup)
    elif variant:
        await update.message.reply_text(f"*{context.user_data['read'][variant][0].split('/')[0]}*\n"
                                        f"{context.user_data['read'][variant][0].split('/')[1]}", parse_mode='Markdown')
        context.user_data['read'][variant] = context.user_data['read'][variant][1:]
        if not context.user_data['read'][variant]:
            context.user_data['variant'] = ''
            await update.message.reply_text(
                "История завершена...", reply_markup=ReplyKeyboardRemove()
            )
            keyboard = [
                [
                    InlineKeyboardButton("Каталог историй", callback_data='1'),
                    InlineKeyboardButton('Мои истории', callback_data='5')],
                [InlineKeyboardButton("Создать историю", url='http://127.0.0.1:8080')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите действие в меню")


async def start_read(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    variant = query.message.reply_markup.to_dict()['inline_keyboard'][0][0]['text']
    reply_keyboard = [[]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    if variant not in context.user_data['history']:
        context.user_data['history'][variant] = take_history(variant)
        context.user_data['read'][variant] = context.user_data['history'][variant]
    context.user_data['variant'] = variant
    if not context.user_data['read'][variant]:
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data='3'), InlineKeyboardButton("Нет", callback_data='4')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text('Вы уже закончили данную историю, желаете начать заново?',
                                      reply_markup=reply_markup)
    else:
        reply_keyboard = [['.', '/close']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        await query.message.reply_text('Чтение', reply_markup=markup
                                       )
        await query.message.edit_text(f'Вы читаете {variant}')


async def yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data['read'][context.user_data['variant']] = context.user_data['history'][context.user_data['variant']]
    await query.message.edit_text(f'Вы начали историю заново!')
    reply_keyboard = [['.', '/close']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await query.message.edit_text('Чтение')
    await query.message.reply_text(f'Вы читаете {context.user_data["variant"]}', reply_markup=markup)


async def no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        'Возобновление завершено')
    await query.message.reply_text(
        'Вы закончили читать', reply_markup=ReplyKeyboardRemove())
    context.user_data['variant'] = ''
    keyboard = [
        [
            InlineKeyboardButton("Каталог историй", callback_data='1'),
            InlineKeyboardButton('Мои истории', callback_data='5')],
        [InlineKeyboardButton("Создать историю", url='http://127.0.0.1:8080')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)


async def start(update, context):
    k = f"""SELECT * FROM users WHERE user_name = '{update.message.from_user.username}'"""
    result = cur.execute(k).fetchall()
    if not result:
        cur.execute("""INSERT INTO users VALUES(?, ?, ?)""", (update.message.from_user.id,
                                                              update.message.from_user.username,
                                                              f"{update.message.from_user.first_name} {update.message.from_user.last_name}"))
        con.commit()
    if 'history' not in context.user_data:
        context.user_data['history'] = {}
        context.user_data['read'] = {}
        context.user_data['variant'] = ''
    keyboard = [
        [
            InlineKeyboardButton("Каталог историй", callback_data='1'),
            InlineKeyboardButton('Мои истории', callback_data='5')],
        [InlineKeyboardButton("Создать историю", url='http://127.0.0.1:8080')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)
    await context.bot.sendPhoto(chat_id=update.message.chat.id, photo=
    choice(cats), caption=choice(cats0))


async def my_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    c = anons_history()
    n = 0
    if context.user_data['read']:
        for i in c:
            if i[0] in context.user_data['read'].keys():
                keyboard = [
                    [
                        InlineKeyboardButton(f'{i[0]}', callback_data='2')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if n == 0:
                    await query.message.edit_text(f'*{i[0]}*\n{i[1]}', reply_markup=reply_markup, parse_mode='Markdown')
                else:
                    await query.message.reply_text(f'*{i[0]}*\n{i[1]}', reply_markup=reply_markup,
                                                   parse_mode='Markdown')
                n += 1
    else:
        await query.message.edit_text(f'*Вы не начинали ни одну историю(((*',
                                      parse_mode='Markdown')
        keyboard = [
            [
                InlineKeyboardButton("Каталог историй", callback_data='1')],
            [InlineKeyboardButton("Создать историю", url='http://127.0.0.1:8080')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)


async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    c = anons_history()
    n = 0
    for i in c:
        keyboard = [
            [
                InlineKeyboardButton(f'{i[0]}', callback_data='2')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if n == 0:
            await query.message.edit_text(f'*{i[0]}*\n{i[1]}\n*Автор: {i[2]}*', reply_markup=reply_markup,
                                          parse_mode='Markdown')
        else:
            await query.message.reply_text(f'*{i[0]}*\n{i[1]}\n*Автор: {i[2]}*', reply_markup=reply_markup,
                                           parse_mode='Markdown')
        n += 1


async def close(update, context):
    await update.message.reply_text(
        'Вы закончили читать', reply_markup=ReplyKeyboardRemove())
    context.user_data['variant'] = ''
    keyboard = [
        [
            InlineKeyboardButton("Каталог историй", callback_data='1'),
            InlineKeyboardButton('Мои истории', callback_data='5')],
        [InlineKeyboardButton("Создать историю", url='')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)


def main():
    application = Application.builder().token('6296614569:AAGKLAKOFw5jNNwHE4bv5EOp0kUZpzJcYag').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(catalog, pattern='1'))
    application.add_handler(CallbackQueryHandler(start_read, pattern='2'))
    application.add_handler(CallbackQueryHandler(yes, pattern='3'))
    application.add_handler(CallbackQueryHandler(no, pattern='4'))
    application.add_handler(CallbackQueryHandler(my_history, pattern='5'))
    application.add_handler(CommandHandler("close", close))
    text_handler = MessageHandler(filters.TEXT, echo)
    application.add_handler(text_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
