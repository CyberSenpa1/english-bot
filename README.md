# English Telegram Bot  

📚 **Умный бот для изучения английских слов** | **Smart English Vocabulary Trainer**  

## 🔍 О проекте | About the Project  

**VocabMaster** – это Telegram-бот, который помогает учить английские слова с помощью **метода интервальных повторений (Spaced Repetition System, SRS)**. Чем чаще вы ошибаетесь в слове, тем чаще оно будет повторяться!  

**VocabMaster** is a Telegram bot that helps you learn English words using **Spaced Repetition System (SRS)**. The more mistakes you make on a word, the more often it repeats!  

## ✨ Возможности | Features  

- 📌 **Адаптивные повторения** – Бот учитывает ваши ошибки и чаще показывает сложные слова.  
- 📊 **Прогресс и статистика** – Отслеживайте, сколько слов вы уже выучили.  

- 📌 **Adaptive repetitions** – The bot prioritizes words you struggle with.  
- 📊 **Progress tracking** – See how many words you’ve mastered.   

## 🛠 Установка и запуск | Installation  

### Требования | Requirements  
- Python 3.12  
- Telegram Bot API Token (получить у [@BotFather](https://t.me/BotFather))  

1. Клонируйте репозиторий:  
```bash
   git clone https://github.com/CyberSenpa1/english-bot.git
   cd english-bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте бота:
  Создайте .env файл и добавьте:
```
BOT_TOKEN=<Bot_token>
POSTGRES_PASSWORD=<Postgres_password>
DATABASE_URL=engine://user:password@host/db
POSTGRES_USER=<user>
POSTGRES_DB=<db>
POSTGRES_HOST=<host>
POSTGRES_PORT=<port>
REDIS_HOST=<host>
REDIS_PORT=<port>
REDIS_DB=0
REDIS_PASSWORD=<redis_password>
REDIS_URL=<redis_url>
REDIS_DECODE_RESPONSES=True
REDIS_ENCODING=utf-8
```

5. Запустите бота:
```bash
docker compose up --build
```
