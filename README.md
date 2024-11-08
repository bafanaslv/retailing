# Электронная торговая сеть

Это веб-приложение для электронной торговой сети, предоставляющее API и интерфейс для управления сетью продажи электроники. Приложение реализует иерархическую структуру сети, позволяя управлять уровнями узлов (завод, розничная сеть (дистрибьютеры),
ритейлеры в том числе индивидуальный предприниматель), продуктами, задолженностями. Связи между участниками сети устнавливаются динамически в момент выполнения операции покупки.

## Функциональность
- **Управление узлами сети** (завод, розничная сеть, индивидуальный предприниматель)
- **CRUD-операции** для пользователей сети, узлов сети, категорий продуктов, продуктов, стран, склад (остатки), задолженность
- **Фильтрация** узлов по стране
- **Проверка прав доступа** для пользователей API
- **Admin-панель** с функциями поиска, фильтрации и действиями администратора

## Стек технологий
- **Backend**: Django, Django REST Framework
- **База данных**: PostgreSQL
- **Аутентификация**: JSON Web Token (JWT) с использованием библиотеки `djangorestframework-simplejwt`

# API Документация
- **Документация API доступна по путям /swagger/ и /redoc/, где можно просмотреть описание всех доступных методов и эндпоинтов.**

## Установка и настройка

### Предварительные требования
- Python 3.8+
- PostgreSQL 10+
- Установленный `pip`

### Шаги установки

1. **Клонируйте репозиторий**

   - git clone https://github.com/bafanaslv/retailing.git

2. **Установите зависимости**
   - Виртуальное окружение и зависимости создаются с помощью poetry.
   
3. **Примените миграции базы данных**
   - python manage.py makemigrations
   - python manage.py migrate

4. **Создайте суперпользователя**
    - python manage.py csu

5. **Запустите сервер разработки**
    - python manage.py runserver

6. **Для запуска тестов выполните команду:**
    - coverage run --source='.' manage.py test
