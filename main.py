import logging
from random import choice

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from telegram.ext import CommandHandler

from mail import anons_history, take_history

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
cats = ["https://www.yandex.ru/images/search?from=tabbar&img_url=http%3A%2F%2Fimg-fotki.yandex.ru%2Fget%2F9164"
        "%2F116075328.4d%2F0_d4345_96ec43ee_XL.jpg&lr=11129&pos=3&rpt=simage&text=%D0%BA%D0%BE%D1%82%D0%B8%D0%BA%20%D0%BE"
        "%D0%B4%D1%83%D0%B2%D0%B0%D0%BD%D1%87%D0%B8%D0%BA%D0%B8",
        "https://www.yandex.ru/images/search?img_url=http%3A%2F%2Ffunart.pro%2Fuploads%2Fposts%2F2022-06%2F1654196546_17-funart-pro-p-kotik-v-oduvanchikakh-zhivotnie-krasivo-fo-19.jpg&lr=43&pos=10&rpt=simage&source=serp&text=%D0%BA%D0%BE%D1%82%D0%B8%D0%BA%20%D0%B2%20%D0%BE%D0%B4%D1%83%D0%B2%D0%B0%D0%BD%D1%87%D0%B8%D0%BA%D0%B0%D1%85",
        "https://www.yandex.ru/images/search?img_url=http%3A%2F%2Ffunart.pro%2Fuploads%2Fposts%2F2022-05%2F1653403888_33-funart-pro-p-kotenok-v-oduvanchikakh-krasivo-zhivotnie-40.jpg&lr=43&pos=11&rpt=simage&source=serp&text=%D0%BA%D0%BE%D1%82%D0%B8%D0%BA%20%D0%B2%20%D0%BE%D0%B4%D1%83%D0%B2%D0%B0%D0%BD%D1%87%D0%B8%D0%BA%D0%B0%D1%85",
        "https://www.yandex.ru/images/search?img_url=http%3A%2F%2Fon-desktop.com%2Fwps%2FAnimals___Cats_Funny_white_cat_in_dandelions_046838_.jpg&lr=43&pos=19&rpt=simage&source=serp&text=%D0%BA%D0%BE%D1%82%D0%B8%D0%BA%20%D0%B2%20%D0%BE%D0%B4%D1%83%D0%B2%D0%B0%D0%BD%D1%87%D0%B8%D0%BA%D0%B0%D1%85",
        "https://www.yandex.ru/images/search?img_url=http%3A%2F%2Fzastavki.com%2Fpictures%2Foriginals%2F2013%2FAnimals___Cats_Black_and_white_cat_in_dandelions_046796_.jpg&lr=43&p=1&pos=4&rpt=simage&source=serp&text=%D0%BA%D0%BE%D1%82%D0%B8%D0%BA%20%D0%B2%20%D0%BE%D0%B4%D1%83%D0%B2%D0%B0%D0%BD%D1%87%D0%B8%D0%BA%D0%B0%D1%85",
        "https://www.yandex.ru/images/search?img_url=http%3A%2F%2Ffunart.pro%2Fuploads%2Fposts%2F2022-06%2F1654196598_7-funart-pro-p-kotik-v-oduvanchikakh-zhivotnie-krasivo-fo-7.jpg&lr=43&p=1&pos=12&rpt=simage&source=serp&text=%D0%BA%D0%BE%D1%82%D0%B8%D0%BA%20%D0%B2%20%D0%BE%D0%B4%D1%83%D0%B2%D0%B0%D0%BD%D1%87%D0%B8%D0%BA%D0%B0%D1%85"]
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
