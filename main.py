import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import pandas as pd
from openpyxl import Workbook, load_workbook

# Функция для сохранения данных в таблицу Excel
def save_to_excel(text, photo_link):
    wb = load_workbook('реклама.xlsx')
    ws = wb.active
    # Определение строки для записи
    row_number = ws.max_row + 1
    ws.cell(row=row_number, column=1).value = text
    ws.cell(row=row_number, column=2).value = photo_link
    wb.save('реклама.xlsx')



# Функция для отправки сообщения
def send_message(user_id, message):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=vk_api.utils.get_random_id(),
    )

# Функция для обработки команды !рек
def handle_command(user_id, command):
    try:
        index = int(command)
        df = pd.read_excel('реклама.xlsx')
        if not df.empty and index <= len(df):
            text = df.iloc[index - 1]['Text']
            photo_link = df.iloc[index - 1]['PhotoLink']
            send_message(user_id, f"Текст рекламы: {text}\nСсылка на картинку: {photo_link}")
        else:
            send_message(user_id, "Указанная строка не найдена.")
    except ValueError:
        send_message(user_id, "Необходимо указать номер строки после команды !рек.")



# Функция для обработки рекламы
def handle_advertisement(user_id, event):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                if event.attachments['attach1_type'] == 'photo' and event.text:
                    text = event.text
                    # Предполагаем, что ссылка на картинку хранится в первой фотографии
                    photo_link = event.attachments['attach1']
                    save_to_excel(text, photo_link)
                    send_message(user_id, "Рекламное объявление сохранено.")
                    break



# Авторизация в ВКонтакте
token_file = open('C:\\1\\token.txt')
vk_session = vk_api.VkApi(token=token_file.read())
token_file.close()
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:

                msg =event.text.lower()
                id = event.user_id
                
                if event.text.lower().startswith('!рек'):
                    command = msg.split()[1]
                    send_message(id,command)
                    handle_command(id, command)
                elif msg =='!id':
                    send_message(id,id)
                elif msg == '!нач':
                    send_message(id, "Введите описание и прикрепите фотографию.\nФотографию и описание следует отправлять вместе, одним сообщением.")
                    handle_advertisement(id, event)
                elif msg == 'кон':
                    break

main()
