from telegram import ForceReply, Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import re
from main_db_model import*
from stages import*
import os

TOKEN = os.environ.get('Token_bot_questionnaire')
print(TOKEN, 'Token_bot_questionnaire')


ID_GROUP = os.environ.get('ID_group_bot_questionnaire')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [
            InlineKeyboardButton("Заполнить анкету", callback_data="Заполнить анкету")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Нажмите сюда:", reply_markup=reply_markup)
    return START

async def start_quize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Мужской", callback_data="Мужской"),
            InlineKeyboardButton("Женский", callback_data="Женский"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"Укажите пол", reply_markup=reply_markup)
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data["Пол"]=query.data
    await context.bot.send_message(update.effective_user.id, "Укажите ваш возраст")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    txt = update.message.text
    if not txt.isdigit():
        await update.message.reply_text("Укажите только число")
        return AGE
    context.user_data["Возраст"]=txt
    await update.message.reply_text(f"Укажите ваше имя:")
    return NAME

async def name_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    letter = update.message.text
    if not letter.isalpha():
        await update.message.reply_text("Укажите пожалуйста ваше имя правильно")
        return NAME
    context.user_data["Имя"]=letter
    await update.message.reply_text(f"Укажите ваш город проживания:")
    return CITY

async def name_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ltr = update.message.text
    if not ltr.isalpha():
        await update.message.reply_text("Укажите пожалуйста ваш город правильно")
        return CITY
    context.user_data["Город"]=ltr
    await update.message.reply_text(f"Укажите ваш тренировочный стаж:")
    return TRAINING

async def expirience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    exp = update.message.text
    context.user_data["Тренировочный стаж"]=exp
    await update.message.reply_text(f"Укажите цель занятий")
    return TARGET

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trg = update.message.text
    context.user_data["Цель занятий"]=trg
    await update.message.reply_text(f"Укажите ваш номер телефона:")
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    number_phone = update.message.text
    context.user_data["Номер телефона"]=number_phone
    await update.message.reply_text(f"Укажите время когда вам удобно чтобы с вами связался тренер:")
    return TIME

async def talk_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tt = update.message.text
    context.user_data["Удобное время"]=tt
    result = ""
    for key in context.user_data:
        result += f"{key}: {context.user_data[key]}\n"
    
    keyboard = [
        [
            InlineKeyboardButton("Отправить данные", callback_data=str("Отправить данные")),
            InlineKeyboardButton("Пройти анкету заново", callback_data=str("Пройти анкету заново")),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(result, reply_markup=reply_markup)
    return CONFIRM

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "Пройти анкету заново":
        keyboard = [
            [
                InlineKeyboardButton("Заполнить анкету", callback_data="Заполнить анкету")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Нажмите сюда:", reply_markup=reply_markup)
        return START
    else:
        session = Session()
        data = Data()
        data.user_id = update.effective_user.id
        data.data_time = datetime.now()
        data.gender = context.user_data['Пол']
        data.age = int(context.user_data['Возраст'])
        data.name = context.user_data['Имя']
        data.city = context.user_data['Город']
        data.experience = context.user_data['Тренировочный стаж']
        data.target = context.user_data['Цель занятий']
        data.phone = context.user_data['Номер телефона']
        data.time_talk = context.user_data['Удобное время']
        data.nickname = update.effective_user.username
        data.posted = 0
        session.add(data)
        session.commit()
        session.close()
        await query.edit_message_text("Ваши данные сохранены и отправлены.")
        text =  f"""
        Пол: {context.user_data['Пол']}
        Возраст: {int(context.user_data['Возраст'])}
        Имя: {context.user_data['Имя']}
        Город: {context.user_data['Город']}
        Тренировочный стаж: {context.user_data['Тренировочный стаж']}
        Цель занятий: {context.user_data['Цель занятий']}
        Номер телефона: {context.user_data['Номер телефона']}
        Удобное время: {context.user_data['Удобное время']}
        Телеграм_ник @{update.effective_user.username}
        ID пользователя {update.effective_user.id}"""

        await context.bot.send_message(ID_GROUP,text)

        return END
    

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 805170240 == update.message.from_user.id:
        await update.message.reply_text(f"Пользователь является администратором")
    else:
        await update.message.reply_text(f"Пользователь не является администратором")

async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    Session = sessionmaker(bind=engine)
    session = Session()
    data_client = session.query(Data).filter(Data.posted == 0).all()
   
    result = ""
    if update.message.from_user.id != 805170240 and update.message.from_user.id != 496750666:
        await update.message.reply_text(f"Вы не являетесь администратором канала чтобы использовать эту команду")
        return
    for msg_1 in list(data_client):
        result = f"""Имя: {msg_1.name}
        Пол: {msg_1.gender}
        Возраст: {msg_1.age}
        Город: {msg_1.city}
        Опыт: {msg_1.experience}
        Цель занятий: {msg_1.target}
        Номер телефона: {msg_1.time_talk}
        Время звонка: {msg_1.time_talk}
        Телеграм_ник @{msg_1.nickname}
        ID пользователя {update.effective_user.id}"""

        await update.message.reply_text(f'Данные о клиенте: \n{result}\n')
        msg_1.posted = 1
        session.commit()
    session.close()

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    Session = sessionmaker(bind=engine)
    session = Session()
    data_client = session.query(Data).all()
   
    result = ""
    if update.message.from_user.id != 805170240 and update.message.from_user.id != 496750666:
        await update.message.reply_text(f"Вы не являетесь администратором канала чтобы использовать эту команду")
        return
    for msg_1 in list(data_client):
        if msg_1.posted == 1:
            result = f"""Старая анкета:\n Имя: {msg_1.name}
            Пол: {msg_1.gender}
            Возраст: {msg_1.age}
            Город: {msg_1.city}
            Опыт: {msg_1.experience}
            Цель занятий: {msg_1.target}
            Номер телефона: {msg_1.phone}
            Время звонка: {msg_1.time_talk}
            Телеграм_ник @{msg_1.nickname}
            ID пользователя {update.effective_user.id}"""

            await update.message.reply_text(f'Данные о клиенте: \n{result}\n')
            msg_1.posted = 1
        else:
            result = f"""Новая анкета:\n Имя: {msg_1.name}
            Пол: {msg_1.gender}
            Возраст: {msg_1.age}
            Город: {msg_1.city}
            Опыт: {msg_1.experience}
            Цель занятий: {msg_1.target}
            Номер телефона: {msg_1.phone}
            Время звонка: {msg_1.time_talk}
            Телеграм_ник @{msg_1.nickname}
            ID пользователя {update.effective_user.id}"""

            await update.message.reply_text(f'Данные о клиенте: \n{result}\n')
            

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()
    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)], 
        states={
            START: [CallbackQueryHandler(start_quize)],
            GENDER: [CallbackQueryHandler(gender)],
            AGE: [MessageHandler(filters.TEXT|~filters.COMMAND, age)],
            NAME: [MessageHandler(filters.TEXT|~filters.COMMAND, name_client)],
            CITY: [MessageHandler(filters.TEXT|~filters.COMMAND, name_city)],
            TRAINING: [MessageHandler(filters.TEXT|~filters.COMMAND, expirience)],
            TARGET: [MessageHandler(filters.TEXT|~filters.COMMAND, goal)],
            PHONE: [MessageHandler(filters.TEXT|~filters.COMMAND, phone)],
            TIME: [MessageHandler(filters.TEXT|~filters.COMMAND, talk_time)],
            CONFIRM: [CallbackQueryHandler(confirmation)],

        },
        fallbacks=[CommandHandler("start", start), CommandHandler("help", help_command),
                   CommandHandler("show", show_data),CommandHandler("history", history),]
    ))

    application.run_polling()


if __name__ == "__main__":
    main()




