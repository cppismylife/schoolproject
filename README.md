### Инструкция по запуску:
1. Установить в виртуальное окружение необходимые пакеты: 
   ```bash
   pip install -r requirements.txt
   ```
   
2. Создать в корне проекта файл `.env` и установить переменные окружения:
    - `EMAIL_HOST_USER` адрес почты аккаунта с которого будут приходить письма о восстановлении пароля.
    - `EMAIL_HOST_PASSWORD` пароль от аккаунта
    - `SECRET_KEY` секретный ключ приложения. Сгенерировать его можно в консоли Python:
    ```python
    from django.core.management.utils import get_random_secret_key  
    get_random_secret_key()
    ```
    
3. Синхронизировать структуру базы данных с моделями: 
   ```bash
   python manage.py migrate
   ```

3. Запустить сервер:
    ```bash
    python manage.py runserver
    ```
