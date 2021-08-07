### Инструкция по запуску:
1. Установить в виртуальное окружение необходимые пакеты: 
   ```bash
   pip install -r requirements.txt
   ```
2. Синхронизировать структуру базы данных с моделями: 
   ```bash
   python manage.py migrate
   ```

3. Запустить сервер:
    ```bash
    python manage.py runserver
    ```
