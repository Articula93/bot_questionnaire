from telegram import ForceReply, Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import re
from main_db_model import*
from constant_list import*
from stages import*
import os

TOKEN = os.environ.get('Token_bot_questionnaire')
print(TOKEN, 'Token_bot_questionnaire')


ID_GROUP = os.environ.get('ID_group_bot_questionnaire')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [
            InlineKeyboardButton(FILL_IN_THE_FORM, callback_data=FILL_IN_THE_FORM)
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(CLICK_HERE, reply_markup=reply_markup)
    return START

async def start_quize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton(MALE, callback_data=MALE),
            InlineKeyboardButton(FEMALE, callback_data=FEMALE),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=IDENTIFY_GENDER, reply_markup=reply_markup)
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data[YOUR_GENDER]=query.data
    await context.bot.send_message(update.effective_user.id, STATE_YOUR_AGE)
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    txt = update.message.text
    if not txt.isdigit():
        await update.message.reply_text(ONLY_COUNT)
        return AGE
    context.user_data[YOUR_AGE]=txt
    await update.message.reply_text(STATE_YOUR_NAME)
    return NAME

async def name_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    letter = update.message.text
    if not letter.isalpha():
        await update.message.reply_text(CORRECT_NAME)
        return NAME
    context.user_data[YOUR_NAME]=letter
    await update.message.reply_text(ENTER_YOUR_CITY_OF_RESIDENCE)
    return CITY

async def name_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ltr = update.message.text
    if not ltr.isalpha():
        await update.message.reply_text(CORRECT_CITY)
        return CITY
    context.user_data[YOUR_CITY]=ltr
    await update.message.reply_text(INDICATE_YOUR_TRAINING_EXEPIRENCE)
    return TRAINING

async def expirience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    exp = update.message.text
    context.user_data[YOUR_EXEPIRENCE]=exp
    await update.message.reply_text(STATE_PURPOSE_CLASS)
    return TARGET

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trg = update.message.text
    context.user_data[YOUR_PURPOSE]=trg
    await update.message.reply_text(ENTER_YOUR_NUMBER_PHONE)
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    number_phone = update.message.text
    context.user_data[YOUR_PHONE]=number_phone
    await update.message.reply_text(CONVENIENT_TIME)
    return TIME

async def talk_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tt = update.message.text
    context.user_data[YOUR_CONVENIENT_TIME]=tt
    result = ""
    for key in context.user_data:
        result += f"{key}: {context.user_data[key]}\n"
    
    keyboard = [
        [
            InlineKeyboardButton(SEND_DATA, callback_data=str(SEND_DATA)),
            InlineKeyboardButton(REAPPLY, callback_data=str(REAPPLY)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(result, reply_markup=reply_markup)
    return CONFIRM

async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == REAPPLY:
        keyboard = [
            [
                InlineKeyboardButton(FILL_IN_THE_FORM, callback_data=FILL_IN_THE_FORM)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(CLICK_HERE, reply_markup=reply_markup)
        return START
    else:
        session = Session()
        data = Data()
        data.user_id = update.effective_user.id
        data.data_time = datetime.now()
        data.gender = context.user_data[YOUR_GENDER]
        data.age = int(context.user_data[YOUR_AGE])
        data.name = context.user_data[YOUR_NAME]
        data.city = context.user_data[YOUR_CITY]
        data.experience = context.user_data[YOUR_EXEPIRENCE]
        data.target = context.user_data[YOUR_PURPOSE]
        data.phone = context.user_data[YOUR_PHONE]
        data.time_talk = context.user_data[YOUR_CONVENIENT_TIME]
        data.nickname = update.effective_user.username
        data.posted = 0
        session.add(data)
        session.commit()
        session.close()
        await query.edit_message_text(SAVE_DATA)
        text =  f"""
        {FORM_GENDER} {context.user_data[YOUR_GENDER]}
        {FORM_AGE} {int(context.user_data[YOUR_AGE])}
        {FORM_NAME} {context.user_data[YOUR_NAME]}
        {FORM_CITY} {context.user_data[YOUR_CITY]}
        {FORM_EXEPIRENCE} {context.user_data[YOUR_EXEPIRENCE]}
        {FORM_PURPOSE} {context.user_data[YOUR_PURPOSE]}
        {FORM_PHONE} {context.user_data[YOUR_PHONE]}
        {FORM_TIME} {context.user_data[YOUR_CONVENIENT_TIME]}
        {TELEGRAM_NAME} {f'@',update.effective_user.username}
        {ID_USER} {update.effective_user.id}"""

        await context.bot.send_message(ID_GROUP,text)

        return END
    

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 805170240 == update.message.from_user.id:
        await update.message.reply_text(USER_ADMIN)
    else:
        await update.message.reply_text(USER_NOT_ADMIN)

async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    Session = sessionmaker(bind=engine)
    session = Session()
    data_client = session.query(Data).filter(Data.posted == 0).all()
   
    result = ""
    if update.message.from_user.id != 805170240 and update.message.from_user.id != 496750666:
        await update.message.reply_text(YOUR_NOT_ADMIN)
        return
    for msg_1 in list(data_client):
        result = f"""{FORM_NAME} {msg_1.name}
        {FORM_GENDER} {msg_1.gender}
        {FORM_AGE} {msg_1.age}
        {FORM_CITY} {msg_1.city}
        {FORM_EXEPIRENCE} {msg_1.experience}
        {FORM_PURPOSE} {msg_1.target}
        {FORM_PHONE} {msg_1.time_talk}
        {FORM_TIME} {msg_1.time_talk}
        {TELEGRAM_NAME} {f'@',msg_1.nickname}
        {ID_USER} {update.effective_user.id}"""

        await update.message.reply_text(CLIENT_DATA, f'\n{result}\n')
        msg_1.posted = 1
        session.commit()
    session.close()

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    Session = sessionmaker(bind=engine)
    session = Session()
    data_client = session.query(Data).all()
   
    result = ""
    if update.message.from_user.id != 805170240 and update.message.from_user.id != 496750666:
        await update.message.reply_text(YOUR_NOT_ADMIN)
        return
    for msg_1 in list(data_client):
        if msg_1.posted == 1:
            result = f"""{OLD_FORM}\n {FORM_NAME} {msg_1.name}
            {FORM_GENDER} {msg_1.gender}
            {FORM_AGE} {msg_1.age}
            {FORM_CITY} {msg_1.city}
            {FORM_EXEPIRENCE} {msg_1.experience}
            {FORM_PURPOSE} {msg_1.target}
            {FORM_PHONE} {msg_1.phone}
            {FORM_TIME} {msg_1.time_talk}
            {TELEGRAM_NAME} {f'@',msg_1.nickname}
            {ID_USER} {update.effective_user.id}"""

            await update.message.reply_text(CLIENT_DATA,f'\n{result}\n')
            msg_1.posted = 1
        else:
            result = f"""{NEW_FORM}\n {FORM_NAME} {msg_1.name}
            {FORM_GENDER} {msg_1.gender}
            {FORM_AGE}: {msg_1.age}
            {FORM_CITY} {msg_1.city}
            {FORM_EXEPIRENCE} {msg_1.experience}
            {FORM_PURPOSE} {msg_1.target}
            {FORM_PHONE} {msg_1.phone}
            {FORM_TIME} {msg_1.time_talk}
            {TELEGRAM_NAME} {f'@',msg_1.nickname}
            {ID_USER} {update.effective_user.id}"""

            await update.message.reply_text(CLIENT_DATA,f'\n{result}\n')
            

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




