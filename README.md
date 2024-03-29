# packaging\_bot

[![CodeFactor](https://www.codefactor.io/repository/github/elejke/packaging_bot/badge?s=13bc3359e8141b92aadc60031fbbbc433c4a81ab)](https://www.codefactor.io/repository/github/elejke/packaging_bot)

## Cоздание приложения для сбора информации о трудноперерабатываемой упаковке

Приложение использует микросервисную архитектуру и состоит из модулей. Каждый модуль по своей сути - отдельный независимый проект.

## Telegram Bot

Клиентская часть для взаимодействия с пользователем через API ботов мессенджера Telegram.

Здесь также расположено распознавание фотографий штрихкодов товаров, по которым пользователи смогут легко искать нужный товар и добавлять информацию об упаковке.

Более подробная инструкция внутри папки модуля.

## Data Web API

Модуль, в котором сосредоточена обработка данных, связь с базой данных, запросы к сторонним сервисам. Использованы популярные инструменты для создания веб-сервисов:

* [Flask](https://flask.palletsprojects.com/) - расширяемый микрофреймворк для создания веб-приложений на языке Python
* [SQLAlchemy](https://www.sqlalchemy.org/) - библиотека для работы с реляционными СУБД с применением технологии ORM.

Конфигурация хранится в файле `src/python.py`.

Для установки зависимостей нужно выполнить команду:

`pip install -r requirements.txt`

Для запуска используйте скрипт в корне проекта:

`bash start.sh`

