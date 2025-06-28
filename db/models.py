from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, BigInteger, Text, ForeignKey, Sequence, Float, func, VARCHAR,\
                       TIMESTAMP, BOOLEAN, Index, UniqueConstraint, Computed
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import UniqueConstraint

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("user_id", BigInteger, primary_key=True),
    Column("username", String(64), nullable=True),
    Column("first_name", String(64)),
    Column("reg_date", DateTime, server_default=func.now()),
    Column("daily_goal", Integer(), default=10),
    Column("language_code", String(8), default='en'),
    comment="Таблица пользователей бота"
)

words = Table(
    "words",
    metadata,
    Column("id", BigInteger, Sequence('word_id_seq'), primary_key=True),
    Column("english", String(128), unique=True, nullable=False),
    Column("russian", String(128), nullable=False),
    Column("added_date", DateTime, server_default='now()'),
    Column("difficulty_level", Integer, default=1, index=True), # Уровень сложности от 1 до 5
    Index('idx_words_english', 'english', postgresql_using='gin',  
          postgresql_ops={'english': 'gin_trgm_ops'}),  # Для быстрого поиска
    comment="Словарь английских слов"
)

user_words = Table(
    "user_words",
    metadata,
    Column("id", BigInteger, Sequence('user_word_id_seq'), primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), index=True),
    Column("word_id", BigInteger, ForeignKey("words.id", ondelete="CASCADE"), index=True),
    Column("interval", Integer, default=1),
    Column("repetitions", Integer, default=0),
    Column("correct_attempts", Integer, default=0),
    Column("wrong_attempts", Integer, default=0),
    Column("last_reviewed", DateTime, index=True),
    Column("next_review", DateTime, index=True),  # Критически важный индекс для SRS
    Column("ease_factor", Float, default=2.5),
    Column("is_learning", BOOLEAN, default=True),  # Флаг "в процессе изучения"
    UniqueConstraint('user_id', 'word_id', name='uq_user_word'),
    comment="Прогресс изучения слов с индексами для SRS"
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
    Column("total_correct", Integer, default=0),
    Column("total_wrong", Integer, default=0),
    Column("accuracy", Float, Computed("total_correct::float / NULLIF(total_correct + total_wrong, 0)")),
    Column("daily_progress", JSONB),
    comment="Статистика по пользователям"
)


# Таблица для хранения статистики ответов
answer_logs = Table(
    "answer_logs",
    metadata,
    Column("id", BigInteger, Sequence('answer_log_id_seq'), primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), index=True),
    Column("word_id", BigInteger, ForeignKey("words.id", ondelete="CASCADE"), index=True),
    Column("session_id", BigInteger, ForeignKey("study_sessions.id")),
    Column("is_correct", BOOLEAN, nullable=False, index=True),
    Column("timestamp", TIMESTAMP, default=func.now()),
    Column("mode", VARCHAR(32), nullable=False),
    Column("response_time", Float, nullable=False, comment="Время ответа пользователя (в секундах)")
)

study_sessions = Table(
    "study_sessions",
    metadata,
    Column("id", BigInteger, Sequence('session_id_seq'), primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id"), index=True),
    Column("start_time", DateTime, default=func.now()),
    Column("end_time", DateTime),
    Column("mode", String(32)),  # 'quiz', 'typing', 'flashcards'
    Column("words_learned", Integer, default=0),
    Column("accuracy", Float)  # Процент правильных ответов
)

srs_settings = Table(
    "srs_settings",
    metadata,
    Column("user_id", BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True),
    Column("max_new_words_per_day", Integer, default=20, comment="Максимальное количество новых слов в день"),
    Column("max_reviews_per_day", Integer, default=50, comment="Максимальное количество повторений слов в день"),
    Column("initial_easy_factor", Float, default=2.5, comment="Начальный коэффициент легкости для новых слов"),
    Column("interval_modifier", Float, default=1.0, comment="Модификатор интервала для слов"),
)