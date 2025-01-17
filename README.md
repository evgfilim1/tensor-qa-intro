# tensor-qa-intro

Тестовое задание на вакансию "Программист-тестировщик (отдел автотестирования)" в "Тензор".

Тесты также запускаются на платформе GitHub Actions. 
Результаты выполнения можно посмотреть по ссылке:

[![Run QA tests](https://github.com/evgfilim1/tensor-qa-intro/actions/workflows/autotest.yaml/badge.svg)](https://github.com/evgfilim1/tensor-qa-intro/actions/workflows/autotest.yaml)

## Запуск тестов

1. Установить Docker и docker-compose.
2. Склонировать репозиторий.
3. Скопировать файл `dist.env` в `.env` и заполнить переменные окружения.
4. Запустить тесты командой `docker compose -f compose.yaml -f compose.dev.yaml up --build --attach tests`.

При использовании отладочного compose-файла (`-f compose.dev.yaml`) доступны дополнительные сервисы:
- Selenium Grid UI доступен по адресу http://localhost:4444, пароль для просмотра — `secret`;
- Видеозаписи тестов доступны по адресу http://localhost:8080.

## Задание
1. Необходимо автоматизировать проверки двух обязательных сценариев.
2. Третий сценарий выполнять не обязательно, но это будет дополнительным плюсом на 
   техническом собеседовании.
3. Автотесты реализованы на Python 3 и Selenium Webdriver
4. В качестве тестового framework используется pytest
5. Реализован паттерн PageObject
6. Приветствуются любые сторонние библиотеки для логирования, отчетов, selenium wrapper
7. Готовый проект залит на github/gitlab без кешей, драйверов и виртуальных
   окружений. С открытым доступом на чтение

### Сценарий 1

1. Перейти на https://sbis.ru/ в раздел "Контакты"
2. Найти баннер Тензор, кликнуть по нему
3. Перейти на https://tensor.ru/
4. Проверить, что есть блок "Сила в людях"
5. Перейдите в этом блоке в "Подробнее" и убедитесь, что открывается https://tensor.ru/about
6. Находим раздел "Работаем" и проверяем, что у всех фотографии хронологии одинаковые
   высота (height) и ширина (width).

### Сценарий 2

1. Перейти на https://sbis.ru/ в раздел "Контакты".
2. Проверить, что определился ваш регион и есть список партнеров.
3. Изменить регион на Камчатский край.
4. Проверить, что подставился выбранный регион, список партнеров изменился, url и title содержат
   информацию выбранного региона.

### Сценарий 3 (необязательный)

1. Перейти на https://sbis.ru/
2. В Footer'e найти и перейти "Скачать локальные версии"
3. Скачать СБИС Плагин для вашей для windows, веб-установщик в папку с данным тестом
4. Убедиться, что плагин скачался
5. Сравнить размер скачанного файла в мегабайтах. Он должен совпадать с указанным на сайте.
