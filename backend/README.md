<h1 align="center">Настройка и запуск серверных компонентов</a> 
<h2 align="center">Запуск backend-части </h2>

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
    MONGO_DSN = "mongodb://localhost:27017/yourdb?authSource=admin"
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
    <br>


### Запуск mitmproxy

**Выполните команду:**

```shell
mitmdump -s mitm.py -p 8080 --set keep_host_header=true
```


<h2 align="center">Документация API</h2>

**Для получения информации об API перейдите по пути:** <br>
<br>
Локальная разработка: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs).<br>
(*Доступно при локальном запуске сервера*) <br>

Продакшен-версия: [https://api.babirusa.space/docs](https://api.babirusa.space/docs).<br>
(*Рабочее API в облаке*)

На данных страницах предоставлена Swagger документация.

<h2 align="center">Запуск тестов</h2>

**В папке backend выполните команду:**

 ```shell
 pytest app/tests/ -v 
 ```

**Покрытие кода тестами:**

 ```shell
 pytest --cov=app/tests
 ```

<h2 align="center">Технические решения</h2>


### FastAPI (Фреймворк)

**FastAPI** стал идеальным выбором для этого проекта благодаря высокой производительности и простоте использования. Фреймворк сочетает в себе три ключевых преимущества: асинхронную работу, строгую типизацию данных через Pydantic и автоматизированную генерацию интерактивной документации с помощью Swagger UI.


### MongoDB (База данных)

**MongoDB** была выбрана в качестве базы данных для этого проекта из-за простоты работы, высокой производительности и отличной масштабируемости. Также она идеально подходит для работы с иерархическими и связанными данными. Её используют такие компании как GitHub, Facebook, Google.


### Docker (Платформа контейнеризации)

**Docker** был выбран благодаря своей универсальности, быстрому развёртыванию и экономии ресурсов. В данном проекте он играет ключевую роль в системе запуска персональных кодовых пространств для учащихся.


### Mitmproxy (программа, позволяющая перехватывать поток трафика)

**Mitmproxy** выбран за способность динамически перенаправлять трафик по поддоменам. В рамках проекта он обеспечивает точную маршрутизацию запросов, позволяя каждому пользователю работать в персональной среде.
