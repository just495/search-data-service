# Сервис поиска данных в тексте

## Установка и запуск
```bash
$ git clone https://github.com/just495/search-data-service
$ virtualenv -p python3 venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
$ FLASK_APP=app.py flask run
```
Сервис будет доступен по адресу [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Поиск данных
Для поиска данных можно воспользоваться страницей доступной по адресу [http://127.0.0.1:5000](http://127.0.0.1:5000)
### Пример запроса
Запрос
```bash
curl 'http://127.0.0.1:5000/parser' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' --data 'text=Датой основания России считается день 25 декабря 1991 г.'
```
Результат
```json
{
  "result": [{
	"text": "25 декабря 1991",
	"type": "date"
  }, {
	"address": "Россия",
	"text": "России",
	"type": "place"
  }],
  "source": "Датой основания России считается день 25 декабря 1991 г."
}
```
