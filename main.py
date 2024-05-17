import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import pandas as pd
from openpyxl import Workbook, load_workbook
import os
import requests


# Функция для сохранения данных в таблицу Excel
def save_to_excel(text, photo_link):
    wb = load_workbook('site\data.xlsx')
    ws = wb.active
    # Определение строки для записи
    row_number = ws.max_row + 1
    ws.cell(row=row_number, column=1).value = text
    ws.cell(row=row_number, column=2).value = photo_link+'.jpg'
    wb.save('site\data.xlsx')


def download_file(url, path):
    response = requests.get(url)
    with open(path, "wb") as f:
        f.write(response.content)

def get_photo_link(photo):
    max_size = 0
    max_size_url = ''
    for size in photo['sizes']:
        if size['type'] in ['z', 'w'] and size['height'] * size['width'] > max_size:
            max_size = size['height'] * size['width']
            max_size_url = size['url']
    return max_size_url
        
def download_photo(text, photo_link, photo, path):
    url = get_photo_link(photo)
    if url:
        filename = os.path.basename(path)
        current_dir = os.path.dirname(path)
        extension = os.path.splitext(filename)[1]
        photo_path = os.path.join(current_dir, 'site\images', f'{photo_link}{extension}')
        download_file(url, photo_path)
        save_to_excel(text, photo_link)


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
        df = pd.read_excel('site\data.xlsx')
        if not df.empty and index <= len(df):
            text = df.iloc[index - 1]['text']
            photo_link = df.iloc[index - 1]['image']
            send_message(user_id, f"Текст рекламы: {text}\nСсылка на картинку: {photo_link}")
        else:
            send_message(user_id, "Указанная строка не найдена.")
    except ValueError:
        send_message(user_id, "Необходимо указать номер строки после команды !рек.")



# Функция для обработки рекламы
def handle_advertisement(user_id, event):
    # Отправляем сообщение с вопросами пользователю
    send_message(user_id, message="Для сохранения объявления, пожалуйста, ответьте на вопросы.")

    # Ожидаем ответа пользователя
    organization_name = "\n" + wait_for_user_response(user_id, "Введите название организации:")
    website_link = "\n" + wait_for_user_response(user_id, "Введите ссылку на сайт:")
    job_title = "\n" + wait_for_user_response(user_id, "Введите название вакансии:")
    job_function = "\n" + wait_for_user_response(user_id, "Введите функционал:")
    job_requirements = "\n" + wait_for_user_response(user_id, "Введите требования к соискателю:")
    job_conditions = "\n" + wait_for_user_response(user_id, "Введите условия работы:")
    contact_info = "\n" + wait_for_user_response(user_id, "Введите контакты для отклика:")
    send_message(user_id, "Прикрепите картинку.")

    # После получения всех ответов обрабатываем вложение
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            attachments = vk.messages.getById(message_ids=event.message_id, extended=True, fields='attachments')['items'][0]['attachments']
            if attachments:
                attachment = attachments[0]
                if attachment['type'] == 'photo':
                    photo = attachment['photo']
                    photo_link = event.attachments['attach1']
                    finalText = organization_name + website_link + job_title + job_function + job_requirements + job_conditions + contact_info
                    #save_to_excel(event.text, photo_link)
                    download_photo(finalText, photo_link, photo, "photo.jpg")
                    #download_photo(event.text, photo_link, photo, "photo.png")
                    send_message(user_id, message="Ваша вакансия на модерации.\nПросим заметить, что для нас приоритетными являются вакансии, напрямую связанные с направлениями подготовки, реализуемые в университете.")
                    break
                else:
                    send_message(user_id, "Найдено вложение другого типа")
                    break
            else:
                send_message(user_id, "Вложений не обнаружено.")
                break


def wait_for_user_response(user_id, prompt_message):
    # Отправляем сообщение с запросом пользователю и ожидаем его ответа
    send_message(user_id, message=prompt_message)
    
    # Получаем ответ от пользователя
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
            send_message(user_id, "ответ записан")
            return event.text.strip()  # Возвращаем текст ответа пользователя



# Авторизация в ВКонтакте
token_file = open('C:\\1\\token1.txt')
vk_session = vk_api.VkApi(token=token_file.read())
token_file.close()
vk = vk_session.get_api()
vk_session1 = vk_api.VkApi(token='')
vk1 = vk_session1.get_api()
longpoll = VkLongPoll(vk_session)

current_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:

                msg =event.text.lower()
                id = event.user_id
                
                if event.text.lower().startswith('!рек'):
                    command = msg.split()[1]
                    handle_command(id, command)
                elif msg =='!id':
                    send_message(id,id)
                elif msg == '!нач':
                    handle_advertisement(id, event)
                elif msg == 'кон':
                    break

main()
vk1.wall.post(owner_id='-224970403', message='Test')
