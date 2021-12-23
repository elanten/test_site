# Только для просмотра, без данных не заработает.
Серверная сторона вопроса описана в файле **app.py**

Клиентская (React) - **static/app.js**

## Запуск: 

Создать и активировать venv:
```
python -m venv test
```
Windows:
```
test\scripts\activate
```
Linux: 
```
source test/bin/activate
```
Установить модули из файла requirements.txt:
```
pip install -r requirements.txt
```
Установить переменные окружения:
Windows:
```
set FLASK_APP=app
set FLASK_ENV=development
```
Linux:
```
export FLASK_APP=app
export FLASK_ENV=development
```
Запустить сервер:
```
flask run 
```
Для доступа вне локального хоста:
```
flask run --host=0.0.0.0
```
