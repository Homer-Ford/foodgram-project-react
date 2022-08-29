# foodgram
http://158.160.0.12/
login: anton-anuchin@mail.ru
password: 03041987Dog
![example workflow](https://github.com/Homer-Ford/foodgram-project-react/actions/workflows/foodgram-workflow.yml/badge.svg)

### Описание проекта:

Проект интерфейса API для сайта «Продуктовый помощник», на котором пользователи будут публиковать рецепты,  
добавлять чужие рецепты в избранное и подписываться на публикации других авторов.  
Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для  
приготовления выбранных блюд.
Рецепты делятся на предустановленные теги и список тегов может быть расширен администратором.
Данный проект позволяет с помощью API запросов от разных типов пользователей: получать, создавать,  
редактировать или удалять рецепты, добавлять и удалять свою подписку на авторов рецептов и избранные рецепты,  
а так же редактировать свой список покупок.  
Польза данного проекта заключается в быстроте и удобстве во взаимодействии с информацией на сайте, не заходя на его web страницу.

### Шаблон наполнения env-файла:

DB_ENGINE-в какой СУБД работаем  
DB_NAME-имя базы данных  
POSTGRES_USER-логин для подключения к базе данных  
POSTGRES_PASSWORD-пароль для подключения к БД  
DB_HOST-название сервиса (контейнера)  
DB_PORT-порт для подключения к БД  
SECRET_KEY-секретный ключ приложения Django  
DEBUG-режим разработки

### Описание запуска приложения:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Homer-Ford/foodgram-projects-react.git
```

```
cd ./foodgram-project-react/infra
```

Запускаем сборку контейнеров:

```
docker-compose up -d --build 
```

Выполнить миграции:

```
docker-compose exec web python manage.py migrate
```

Создать суперюзера:

```
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:

```
docker-compose exec web python manage.py collectstatic --no-input
```

Для создания резервной копии базы данных:

```
docker-compose exec web python manage.py dumpdata > fixtures.json
```

Для заполнения базы данных из резервной копии:

```
docker-compose exec web python manage.py loaddata dump.json 
```

Для заполнения базы данных списка ингредиентов:

```
docker-compose exec web python manage.py import_ingredients
```
