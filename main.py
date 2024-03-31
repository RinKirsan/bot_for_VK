import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import pandas as pd

ad_description = None

# Функция для сохранения данных в таблицу Excel
def save_to_excel(text, photo_link):
    df = pd.DataFrame({'Text': [text], 'PhotoLink': [photo_link]})
    df.to_excel('реклама.xlsx', index=False, header=True)

# Функция для отправки сообщения
def send_message(user_id, message):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=vk_api.utils.get_random_id(),
    )

# Функция для обработки команды !рек
def handle_command(user_id, command):
    if command == '1':
        df = pd.read_excel('реклама.xlsx')
        if not df.empty:
            text = df.iloc[0]['Text']
            photo_link = df.iloc[0]['PhotoLink']
            send_message(user_id, f"Текст рекламы: {text}\nСсылка на картинку: {photo_link}")
        else:
            send_message(user_id, "В таблице нет сохраненных рекламных объявлений.")
    else:
        send_message(user_id, "Неизвестная команда.")


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

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:

            msg =event.text.lower()
            id = event.user_id
            
            if msg == '!рек':
                command = msg.split()[1]
                handle_command(id, command)
            elif msg == '!нач':
                send_message(id, "Введите описание и прикрепите фотографию.\nФотографию и описание следует отправлять вместе, одним сообщением.")
                handle_advertisement(id, event)
            elif msg == 'кон':
                break
