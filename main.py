import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import pandas as pd

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

# Авторизация в ВКонтакте
token_file = open('C:\\1\\token.txt')
vk_session = vk_api.VkApi(token=token_file.read())
token_file.close()
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Основной цикл
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        if event.text.lower().startswith('!рек'):
            command = event.text.lower().split()[1]
            handle_command(event.user_id, command)
        else:
            # Предполагаем, что текст рекламы и картинка отправляются вместе
            if event.attachments['attach1_type'] == 'photo': #and event.text:
                text = event.text
                # Предполагаем, что ссылка на картинку хранится в первой фотографии
                photo_link = event.attachments['attach1']
                save_to_excel(text, photo_link)
                send_message(event.user_id, "Рекламное объявление сохранено.")
