## Rutube downloader
Для работы rutube загрузчика необходимо установить ffmpeg: https://www.gyan.dev/ffmpeg/builds/  


## VK downloader

### Получения токена для VK видео
Для скачивания данных из источника vk-video необходимо иметь аккаун в сервисе vk.com.
Далее необходимо получить <strong>access token</strong>. Для этого необходимо:
   1. Перейдите на сайт https://vkhost.github.io/
   2. Выберите приложение "Kate Mobile"
   3. Нажмите на него
   4. Затем нажмите "разрешить"
   5. Скопируйте часть адресной строки от access_token= до &expires_in

### Настройка

Перед запуском скрипта установить логин, пароль, токен для аккуанта в VK.COM:

```sh
export API_VK_LOGIN="..." # Номер телефона
export API_VK_PASSWORD="..." # Пароль
export API_VK_TOKEN="..." # Токен
```

Или изменить файл <strong>~/.bashrc</strong>. Добавьте в конец файла:
```sh
export API_VK_LOGIN="..." # Номер телефона
export API_VK_PASSWORD="..." # Пароль
export API_VK_TOKEN="..." # Токен
```

Также необходимо установить ffmpeg и скачать необходимые библиотеки
```sh
sudo apt update && sudo apt upgrade
sudo apt install ffmpeg
pip install requirements.txt -r
```

Если возникают ошибки с библиотекой vk_api, установите последнюю версию библиотеки следующим образом:
```sh
pip install https://github.com/python273/vk_api/archive/master.zip
```


## Парсинг источников
Поддерживается парсинг из трех источников – YouTube, RuTube и VK видео. Перед началом парсинга нужно составить CSV файл с тремя столбцами: 
1.	«url» - адрес скачиваемого видео
2.	«source» - тип источника. Принимает одно из трех значений – «rutube», «youtube» или «vk».
3.	«quality» - метка качества видео – цифра от 1 до 3
Скачивание из составленного файла можно запустить, импортировав функцию run_from_csv из main_download.py, либо из командной строки, например: