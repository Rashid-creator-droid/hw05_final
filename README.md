# YaTube
## Описание
Проект YaTube - это социальная сеть для блогеров. В данном проекте реализованы: система авторизации, возможность добаления, удаления и редактирования записей, комментарии к этим записям, подписка на понравившегося автора.
## Технологии
Python 3.7
Django 3.2
### Запуск проекта в dev-режиме
- Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Rashid-creator-droid/hw05_final.git
``` 
- Установите и активируйте виртуальное окружение
```
python -m venv venv
``` 
```
source venv/Scripts/activate
``` 
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Перейти в каталог с файлом manage.py
``` 
cd hw05_final/
```
- Выполнить миграции:
```
python manage.py makemigrations
python manage.py migrate
```
