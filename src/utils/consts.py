import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Config:
    TOKEN = os.environ["TOKEN"]
    VOLUME_FOLDER = Path(__file__).absolute().parent.parent / "database" / "db_files"
    DB_FILE = VOLUME_FOLDER / (os.getenv("DB_FILE") or "database.sqlite")
    LOG_FILE = VOLUME_FOLDER / (os.getenv("LOG_FILE") or "logs.log")
    BETTER_CALL_SAUL = (
        os.getenv("BETTER_CALL_SAUL")
        or "Если возникнут вопросы, спрашивайте в беседе потоков без учителей"
    )

    ADMINS = tuple(
        [
            int(os.environ[key])
            for key in os.environ.keys()
            if key.startswith("ADMIN") and os.environ[key].isdigit()
        ]
    )


class CallbackData:
    JOIN_THE_GAME = "join_the_game"


class TextCommands:
    CONFIRM_DEATH = "Подтвердить смерть☠️"
    REMIND_VICTIM = "Напомнить цель🔪"
    YES = "Да"
    NO = "Нет"


MESSAGE_WIDTH_LIMIT = 4096  # telegram limit
TG_ID = int  # для аннотаций
DB_ID = int  # для аннотаций

WELCOME = f"""Привет, это бот игры "Киллер".
Каждый год в ЮФМЛ проводится эта игра для общего знакомства. Суть игры - "убить" свою цель, получить новую и так по кругу.

Чтобы "убить" цель, вы должны выполнить следующие условия:

- Вы и ваша жертва должны находиться строго наедине, и не должно быть свидетелей (свидетели через стеклянные двери, видеосвязь или видеонаблюдение за таковых не считаются).

- Вы должны сказать своей жертве: "Бордовая львица кушает пиццу".

- После успешного "убийства", жертва обязана подтвердить свою смерть, нажав на соответствующую кнопку в боте. После этого "убийца" немедленно получит новую цель.

- "Убивать" можно только с 8:30 до 22:00.

- "Убивать" можно только свою жертву. После "убийства" убийца обязан показать жертве, что именно она его цель.

- Запрещено "убивать" цель в туалете и в душевой комнате общежития. В лицее разрешено "убивать" в любом месте.

- Запрещено применять физическую силу или насилие в процессе "убийства".

- Игра продолжается до тех пор, пока в ней не останется всего два человека, которые становятся победителями. Если "убийств" нет два дня, цели перемешиваются.

- {Config.BETTER_CALL_SAUL}"""

LETS_PLAY_BUTTON = "🩸Участвовать"
READ_NAME_1 = """Введите свою фамилию и имя (например, "Иванов Иван", без кавычек).
Всех участников проверят на корректность имени, и если вы введёте что-то другое, то вас исключат из игры."""
READ_NAME_2 = """Вы успешно зарегистрированы! 
Если вы ввели имя неправильно, дождитесь удаления вас из участников или сразу обратитесь к администратору (последнее предложение /start)"""
ALREADY_PLAYING = "Вы уже участвуете."
NAME_ALREADY_EXISTS = "Вы уже участвуете в игре или такое имя занято."
GAME_ALREADY_STARTED = "Игра уже началась, вы не можете присоединиться."
ARE_YOU_SURE_DEATH_CONFIRM = "Вы уверены, что хотите подтвердить смерть?"
YOU_ARE_DEAD = "Вы мертвы."
ALREADY_DEAD = "Вы уже мертвы."
DEATH_CONFIRMED = "Вы погибли."
DELETED = "Вы были удалены из игры."
