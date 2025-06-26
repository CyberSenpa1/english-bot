from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, BigInteger, Text, ForeignKey, Sequence, Float, func
from sqlalchemy.schema import UniqueConstraint

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("user_id", BigInteger, primary_key=True),
    Column("username", String(64), nullable=True),
    Column("first_name", String(64)),
    Column("reg_date", DateTime, server_default=func.now()),
    Column("language_code", String(8), default='en'),
    comment="Таблица пользователей бота"
)

words = Table(  
    "words",
    metadata,
    Column("id", BigInteger, Sequence('word_id_seq'), primary_key=True),
    Column("english", String(128), unique=True, nullable=False),
    Column("translation", String(128), nullable=False),
    Column("part_of_speech", String(32)),  # noun/verb/adjective/etc
    Column("difficulty_level", Integer, default=1),  # 1-5
    Column("example", Text),
    Column("added_date", DateTime, server_default='now()'),
    comment="Словарь английских слов"
)

user_words = Table(
    "user_words",
    metadata,
    Column("id", BigInteger, Sequence('user_word_id_seq'), primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), index=True),
    Column("word_id", BigInteger, ForeignKey("words.id", ondelete="CASCADE"), index=True),
    Column("correct_attempts", Integer, default=0),
    Column("wrong_attempts", Integer, default=0),
    Column("last_reviewed", DateTime),
    Column("next_review", DateTime),  
    Column("ease_factor", Float, default=2.5),  
    UniqueConstraint('user_id', 'word_id', name='uq_user_word'),
    comment="Прогресс изучения слов пользователями"
)

# Улучшенная версия индекса для быстрого доступа
user_words_index = Table(
    "user_words_index",
    metadata,
    Column("id", BigInteger, Sequence('user_word_index_id_seq'), primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), index=True),
    Column("word_id", BigInteger, ForeignKey("words.id", ondelete="CASCADE"), index=True),
    Column("review_order", Integer),
    Column("correct_attempts", Integer, default=0),
    Column("next_review", DateTime),
    UniqueConstraint('user_id', 'word_id', name='uq_user_word_index'),
    comment="Индекс для быстрого поиска слов на повторение"
)

# Таблица для хранения статистики по пользователям
user_statistics = Table(
    "user_statistics",
    metadata,
    Column("id", BigInteger, Sequence('user_stat_id_seq'), primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), index=True),
    Column("total_words", Integer, default=0),
    Column("learned_words", Integer, default=0),
    Column("streak", Integer, default=0),  # Дни подряд изучения
    Column("last_active", DateTime),
    comment="Статистика по пользователям"
)

# Таблица для хранения категорий слов
categories = Table(
    "categories",
    metadata,
    Column("id", BigInteger, Sequence('category_id_seq'), primary_key=True),
    Column("name", String(64), unique=True, nullable=False),
    Column("description", Text),
    comment="Категории слов для группировки"
)

# Таблица для связи слов с категориями
word_categories = Table(
    "word_categories",
    metadata,
    Column("id", BigInteger, Sequence('word_category_id_seq'), primary_key=True),
    Column("word_id", BigInteger, ForeignKey("words.id", ondelete="CASCADE"), index=True),
    Column("category_id", BigInteger, ForeignKey("categories.id", ondelete="CASCADE"), index=True),
    UniqueConstraint('word_id', 'category_id', name='uq_word_category'),
    comment="Связь слов с категориями"
)

