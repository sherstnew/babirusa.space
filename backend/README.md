<h1 align="center">Облачные среды разработки для школьников на основе контейнеров с автоматическим развертыванием.</a> 
<h2 align="center">Запуск серверной части проекта</h2>

### Необходимо для дальнейшей работы

- Python 3.8 или выше
- [pip](https://pip.pypa.io/en/stable/)
- [Virtualenv](https://pypi.org/project/virtualenv/)

### Установка

1. **Склонируйте репозиторий:**

    ```shell
    git clone https://github.com/sherstnew/babirusa.space.git
    ```

2. **Перейдите в каталог проекта:**

    ```shell
    cd backend
    ```

3. **Создать и активировать виртуальное окружение (рекомендовано):**

    ```shell
    1. python3 -m venv <имя_окружения>
    2. venv/Scripts/activate
    ```
4. **Установите зависимости:**

    ```shell
    pip install -r requirements.txt
    ```
5. **Измените /backend/.env:**

    ```
    DATABASE_URL = "mongodb://localhost:27017/yourdb?authSource=admin"
    MONGO_DSN_TEST = 'mongodb://localhost:27017/yourdbTest?authSource=admin'
    ENVIRONMENT = 'home'
    ALGORITHM = "HS256"
    SECRET_KEY = "YOUR_SECRET_KEY"
    SECRET_KEY_USER = "YOUR_SECRET_KEY_USER"
    ACCESS_TOKEN_EXPIRE_MINUTES=99999
    
    ```
6. **Запустите сервер:**

    ```shell
    uvicorn app.main:app
    ```

<h2 align="center">Запуск тестов</h2>

**В любой части проекта выполните команду:**

   ```shell
    pytest
   ```



