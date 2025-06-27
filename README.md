# English Telegram Bot  

📚 **Умный бот для изучения английских слов** | **Smart English Vocabulary Trainer**  

## 🔍 О проекте | About the Project  

**VocabMaster** – это Telegram-бот, который помогает учить английские слова с помощью **метода интервальных повторений (Spaced Repetition System, SRS)**. Чем чаще вы ошибаетесь в слове, тем чаще оно будет повторяться!  

**VocabMaster** is a Telegram bot that helps you learn English words using **Spaced Repetition System (SRS)**. The more mistakes you make on a word, the more often it repeats!  

## ✨ Возможности | Features  

- 📌 **Адаптивные повторения** – Бот учитывает ваши ошибки и чаще показывает сложные слова.  
- 📚 **Разные режимы** – Выбор перевода, угадывание слова по определению и др.  
- 📊 **Прогресс и статистика** – Отслеживайте, сколько слов вы уже выучили.  
- 🔄 **Гибкие настройки** – Можно менять частоту повторений, сложность и темы.  

- 📌 **Adaptive repetitions** – The bot prioritizes words you struggle with.  
- 📚 **Multiple modes** – Translation quiz, definition matching, etc.  
- 📊 **Progress tracking** – See how many words you’ve mastered.  
- 🔄 **Customizable settings** – Adjust repetition intervals and difficulty.  

## 🛠 Установка и запуск | Installation  

### Требования | Requirements  
- Python 3.10+  
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
TELEGRAM_TOKEN=ваш_токен
```

5. Запустите бота:
```bash
python run.py
```
