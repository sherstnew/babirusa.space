<h1 align="center">Облачные среды разработки для школьников на основе контейнеров с автоматическим развертыванием</a> 

##

*Проект был создан с целью помочь школьникам разрабатывать проекты, не беспокоясь о безопасности и сохранности данных, а учителям безпрепятственно контролировать их работу.*

### [Демонстрация работы проекта](https://babirusa.space)
Рекомендуем вам посмотреть на запущенный проект.

Заготовленные логин и пароль для учителя:
- Логин: ovv
- Пароль: qwerty


## Запуск проекта

Запустить проект можно командой
```
docker compose up --build -d
```

но для полноценной работы приложения необходимо настроить домен: 
- wildcard запись на ip сервера (для динамических поддоменов)
- ssl-сертификат на домен (например, через certbot), настройка nginx на сервере для https и mitmproxy (пример конфига для домена babirusa.space лежит в корне проекта)

а также настроить переменные окружения:
### /.env
```
MONGO_INITDB_ROOT_USERNAME="admin"
MONGO_INITDB_ROOT_PASSWORD="password"
```
Root-данные для MongoDB, используемые далее в /backend/.env
### /frontend/.env
```
VITE_BACKEND_URL="https://api.babirusa.space"
```
где https://api.babirusa.space - адрес бэкенда, может быть установлен просто как 127.0.0.1.
### /backend/.env
```
MONGO_DSN = "mongodb://localhost:27017/yourdb?authSource=admin"
MONGO_DSN_TEST = 'mongodb://localhost:27017/yourdbTest?authSource=admin'
ENVIRONMENT = 'home'
ALGORITHM = "HS256"
SECRET_KEY = "YOUR_SECRET_KEY" # fernet key
SECRET_KEY_USER = "YOUR_SECRET_KEY_USER" # fernet key
ACCESS_TOKEN_EXPIRE_MINUTES=99999
MITM_MODE="SUBDOMAIN" # in beta, значения - SUBDOMAIN/PATH
IP_ADDRESS="90.156.208.35" # адрес вашего сервера во внешней сети
```
После запуска MongoDB необходимо создать две базы: основную и тестовую. Соответственно yourdb необходимо поменять на названия созданных баз данных, а также добавить авторизацию по логину и паролю, указанным выше в /.env.

Развертывание проекта на школьных серверах происходит при помощи квалифицированных специалистов, поэтому обычным ИТ-специалистам в школах не придется поднимать проект самим.

## Документация

Подробные инструкции и описание кода находятся в соответствующих README:

- [Backend документация](./backend/README.md)
- [Frontend документация](./frontend/README.md)
