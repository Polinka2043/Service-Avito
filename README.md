# Service-Avito
Задание: 
Необходимо реализовать сервис, который позволит сотрудникам обмениваться монетками и приобретать на них мерч. Каждый сотрудник должен иметь возможность видеть:

Список купленных им мерчовых товаров
Сгруппированную информацию о перемещении монеток в его кошельке, включая:
Кто ему передавал монетки и в каком количестве
Кому сотрудник передавал монетки и в каком количестве
Количество монеток не может быть отрицательным, запрещено уходить в минус при операциях с монетками.

Ассортимент мерча:
Мерч — это продукт, который можно купить за монетки. Всего в магазине доступно 10 видов мерча. Каждый товар имеет уникальное название и цену. Ниже приведён список наименований и их цены.

| Номер |  Название | Цена |
|:-----|:--------:|------:|
| L0   | t-shirt | 80 |
| L1   |  cup  |   20 |
| L2   | book |    50 |
| L3   | pen |    10 |
| L4   | powerbank |    200 |
| L5   | hoody |    300 |
| L6   | umbrella |    200 |
| L7   | socks |    10 |
| L8   | wallet |    50 |
| L9   | pink-hoody |    500 |
Предполагается, что в магазине бесконечный запас каждого вида мерча.

## Стек технологий

В этом проекте используются следующие технологии:

- **Flask**: Легковесный веб-фреймворк для Python, который позволяет быстро разрабатывать веб-приложения. Flask обеспечивает простоту и гибкость, что делает его идеальным выбором для создания RESTful API.

- **PostgreSQL**: Мощная объектно-реляционная система управления базами данных (СУБД), которая обеспечивает надежное хранение данных и поддержку сложных запросов. PostgreSQL известен своей производительностью и расширяемостью.

- **Docker**: Платформа для автоматизации развертывания приложений в контейнерах. Docker позволяет изолировать зависимости и окружение, что упрощает развертывание и масштабирование приложения.

- **OpenAPI**: Спецификация для описания RESTful API. OpenAPI позволяет документировать API, что делает его более понятным для разработчиков и упрощает интеграцию с другими сервисами.

## Установка и запуск

### Предварительные требования

- Установите [Docker](https://www.docker.com/get-started) на вашем компьютере.
- Убедитесь, что у вас установлен [Docker Compose](https://docs.docker.com/compose/install/).



