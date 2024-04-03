import vk_api

def main():
    # Введите ваш логин и пароль от ВКонтакте
    login = input("Введите логин: ")
    password = input("Введите пароль: ")

    # Авторизация пользователя
    vk_session = vk_api.VkApi(login, password)

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        if "code" in str(error_msg) and "two-factor" in str(error_msg):
            # Если требуется ввод кода двухфакторной аутентификации
            two_factor_code = input("Введите код двухфакторной аутентификации: ")
            vk_session = vk_api.VkApi(login, password, auth_handler=lambda: (two_factor_code, True))
            try:
                vk_session.auth()
            except vk_api.AuthError as error_msg:
                print(error_msg)
                return
        else:
            print(error_msg)
            return

    # Получение ссылки для авторизации группы с правами, необходимыми вашему боту
    redirect_uri = 'https://oauth.vk.com/blank.html'
    scope = 'messages,groups'
    auth_url = vk_session.get_api().auth.get_groups_token_url(client_id=0, scope=scope, redirect_uri=redirect_uri)

    print("Скопируйте ссылку и откройте её в браузере:")
    print(auth_url)
    print("После того как вы разрешили доступ, скопируйте код из адресной строки и вставьте его сюда:")

    # Получение кода доступа
    auth_code = input("Введите код доступа: ")
    access_token = vk_session.get_api().auth.get_groups_access_token(client_id=0, client_secret='', code=auth_code, redirect_uri=redirect_uri)

    # Теперь у вас есть токен доступа, который можно использовать для вызова API в группе
    print("Ваш токен доступа для группы:", access_token['access_token'])

if __name__ == '__main__':
    main()
