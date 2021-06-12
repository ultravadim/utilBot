### Телеграм-бот для работы с внутренним ресурсом Utility.

Для работы необходимо установить следующие переменные окружения (environment variables):

* `BOT_TOKEN` - токен телеграм бота
* `UTIL_URL` - url утилиты

Есть два способа установить эти переменные:

1. создать в корне проекта файл **.env** , в котором будут записаны эти переменные в формате:

   ```
   BOT_TOKEN=<token>
   UTIL_URL=<url>
   ```

2. добавить их через настройки PyCharm ([инструкция](https://www.jetbrains.com/help/objc/add-environment-variables-and-program-arguments.html#add-environment-variables))

