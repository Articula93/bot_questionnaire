from main import*
from constant_list import*


def data_clients(FORM,msg_1,user_id):
    f"""{FORM}\n {FORM_NAME} {msg_1.name}
        {FORM_GENDER} {msg_1.gender}
        {FORM_AGE}: {msg_1.age}
        {FORM_CITY} {msg_1.city}
        {FORM_EXEPIRENCE} {msg_1.experience}
        {FORM_PURPOSE} {msg_1.target}
        {FORM_PHONE} {msg_1.phone}
        {FORM_TIME} {msg_1.time_talk}
        {TELEGRAM_NAME} {f'@',msg_1.nickname}
        {ID_USER} {user_id}"""
