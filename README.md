# Сервис статистики на FastAPI

Данный сервис на FastAPI предназначен для управления статистическими данными, собранными с различных устройств, принадлежащих пользователям. Он предоставляет функциональность для хранения, извлечения и анализа статистических данных, таких как значения `x`, `y` и `z`, записанные устройствами в течение времени.

## Установка

1. **Клонирование репозитория**: Склонируйте этот репозиторий на свой локальный компьютер.

    ```bash
    git clone git@github.com:mackarovak/gazprom.git
    ```

2. **Сборка Docker-образа**: Перейдите в каталог проекта и соберите Docker-образ с помощью предоставленного `Dockerfile`.

    ```bash
    cd gazprom
    docker build -t fastapi-stats .
    ```

3. **Запуск Docker Compose**: Запустите контейнеры Docker с помощью Docker Compose, который настроит как FastAPI-приложение, так и базу данных PostgreSQL.

    ```bash
    docker-compose up
    ```

    Если вы хотите запустить его в фоновом режиме, используйте флаг `-d`:

    ```bash
    docker-compose up -d
    ```

4. **Доступ к API**: После того как контейнеры Docker запущены, вы можете получить доступ к API с помощью вашего предпочтительного HTTP-клиента (например, браузер, cURL, Postman).

## Использование

API предоставляет несколько конечных точек для управления пользователями, устройствами и статистическими данными. Вот как вы можете взаимодействовать с API:

- **Вставка данных**: Используйте конечную точку `POST /device/{id_device}/readings`, чтобы вставить данные для определенного устройства.

- **Получение данных**: Используйте конечную точку `GET /device/{device_id}/readings`, чтобы получить данные для определенного устройства.

- **Получение статистики устройства**: Используйте конечную точку `GET /devices/{id}/stats/`, чтобы получить статистику для всех устройств в указанном временном диапазоне (пример с датой:/devices/2/stats/?start_date=2024-01-01&amp;end_date=2024-03-31).

- **Создание пользователя**: Используйте конечную точку `POST /users/`, чтобы создать нового пользователя.

- **Получение статистики определенного устройства по идентификатору пользователя**: Используйте конечную точку `GET /users/{user_id}/devices/{device_id}/stats`, чтобы получить статистику для определенного устройства определенного пользователя.

- **Получение статистики всех устройств по идентификатору пользователя**: Используйте конечную точку `GET /users/{user_id}/stats`, чтобы получить статистику для всех устройств определенного пользователя.

## Дополнительная информация

- Данный сервис использует PostgreSQL в качестве базы данных.
