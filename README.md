# RabbitMQ Link Extractor

## Описание

RabbitMQ Link Extractor — это приложение для извлечения внутренних ссылок с веб-страниц и их обработки в очереди сообщений RabbitMQ.

Состоит из двух компонентов:

1. **Producer (создатель сообщений)**:

   - Принимает URL веб-страницы.
   - Извлекает все внутренние ссылки с указанной страницы.
   - Помещает ссылки в очередь RabbitMQ.

2. **Consumer (обработчик сообщений)**:
   - Постоянно слушает очередь RabbitMQ.
   - Извлекает ссылки из очереди, обрабатывает их, извлекает новые внутренние ссылки и помещает их обратно в очередь.
   - Завершается, если очередь пуста в течение указанного таймаута.

## Требования

- Python 3.8+
- RabbitMQ установлен и запущен
- Зависимости из `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

## Переменные окружения

Для настройки RabbitMQ используются переменные окружения:

| Переменная          | Описание                                   | Значение по умолчанию |
| ------------------- | ------------------------------------------ | --------------------- |
| `RABBITMQ_HOST`     | Хост RabbitMQ                              | `localhost`           |
| `RABBITMQ_PORT`     | Порт RabbitMQ                              | `5672`                |
| `RABBITMQ_USER`     | Имя пользователя RabbitMQ                  | `guest`               |
| `RABBITMQ_PASSWORD` | Пароль RabbitMQ                            | `guest`               |
| `QUEUE_TIMEOUT`     | Таймаут ожидания в секундах (для consumer) | `10`                  |

## Установка

1. Установите Python зависимости:

   ```bash
   pip install -r requirements.txt
   ```

2. Запустите RabbitMQ.:

   ```bash
   docker-compose up
   ```

3. Убедитесь, что RabbitMQ доступен по адресу, указанному в переменных окружения.

## Использование

### Producer

1. Запустите `producer.py`:

   ```bash
   python producer.py
   ```

2. Введите URL веб-страницы, ссылки с которой необходимо извлечь:

   ```bash
   Enter a URL to process: https://example.com
   ```

3. Producer извлечет все внутренние ссылки с указанного URL и отправит их в очередь RabbitMQ.

### Consumer

1. Запустите `consumer.py`:

   ```bash
   python consumer.py
   ```

2. Consumer начнет обрабатывать ссылки из очереди, извлекать с их страниц новые внутренние ссылки и помещать их обратно в очередь.

3. Если очередь пуста в течение времени, указанного в `QUEUE_TIMEOUT`, приложение завершится.

## Пример

1. **Producer**:

   ```bash
   python producer.py
   Enter a URL to process: https://golangci-lint.run
   Processing page: Welcome to GolangCI-Lint (https://golangci-lint.run)
   Found link: /welcome/install/
   Found link: /welcome/quick-start/
   ...
   ```

2. **Consumer**:
   ```bash
   python consumer.py
   Processing message: https://golangci-lint.run/welcome/install/
   Page: Install Guide (https://golangci-lint.run/welcome/install/)
   Found link: /welcome/quick-start/
   Found link: /usage/configuration/
   ...
   ```

## Зависимости

Установите необходимые библиотеки с помощью:

```bash
pip install -r requirements.txt
```

### Список зависимостей:

- `pika`: Для работы с RabbitMQ.
- `beautifulsoup4`: Для парсинга HTML-кода страниц.
- `requests`: Для загрузки HTML-страниц.
