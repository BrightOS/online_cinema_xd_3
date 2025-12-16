from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from session import get_session
from db import queries
from schemas import (
    EpisodeCreateRequest, GenreCreateRequest, PersonCreateRequest,
    EntryLocaleCreateRequest, EpisodeLocaleCreateRequest, EntryCreateRequest,
    FranchiseCreateRequest, FranchiseLocaleCreateRequest
)

router = APIRouter(prefix="/generate_test_data", tags=["Generate Test Data"])


async def create_genres(db: AsyncSession) -> dict[str, int]:
    genres_data = [
        {"name": "Комедия"},
        {"name": "Фэнтези"},
        {"name": "Приключения"},
        {"name": "Сказка"},
        {"name": "Семейный"},
        {"name": "Исэкай"},
        {"name": "Пародия"},
    ]

    genres = {}
    for genre_data in genres_data:
        genre = await queries.create_genre(db, GenreCreateRequest(**genre_data))
        genres[genre_data["name"]] = genre.id

    return genres


async def create_persons(db: AsyncSession) -> dict[str, int]:
    persons_data = [
        # Морозко
        {"name": "Александр Роу", "en_name": "Aleksandr Rou", "birth_date": date(1906, 3, 8)},
        {"name": "Наталья Седых", "en_name": "Natalya Sedykh", "birth_date": date(1945, 6, 24)},
        {"name": "Эдуард Изотов", "en_name": "Eduard Izotov", "birth_date": date(1936, 3, 4)},
        {"name": "Инна Чурикова", "en_name": "Inna Churikova", "birth_date": date(1943, 10, 5)},
        # Иван Васильевич меняет профессию
        {"name": "Леонид Гайдай", "en_name": "Leonid Gaidai", "birth_date": date(1923, 1, 30)},
        {"name": "Юрий Яковлев", "en_name": "Yuri Yakovlev", "birth_date": date(1928, 4, 25)},
        {"name": "Леонид Куравлёв", "en_name": "Leonid Kuravlyov", "birth_date": date(1936, 10, 8)},
        {"name": "Александр Демьяненко", "en_name": "Aleksandr Demyanenko", "birth_date": date(1937, 5, 30)},
        # Коносуба
        {"name": "Нацумэ Акацуки", "en_name": "Natsume Akatsuki", "birth_date": None},
        {"name": "Канасаки Такаоми", "en_name": "Kanasaki Takaomi", "birth_date": None},
        {"name": "Амамия Соора", "en_name": "Amamiya Sora", "birth_date": date(1993, 8, 28)},
        {"name": "Такахаси Риэ", "en_name": "Takahashi Rie", "birth_date": date(1994, 2, 27)},
        {"name": "Кайано Аи", "en_name": "Kayano Ai", "birth_date": date(1987, 9, 13)},
    ]

    persons = {}
    for person_data in persons_data:
        person = await queries.create_person(db, PersonCreateRequest(**person_data))
        persons[person_data["name"]] = person.id

    return persons


async def create_franchise_with_locales(db: AsyncSession, locales: list[dict]) -> int:
    franchise = await queries.create_franchise(db, FranchiseCreateRequest())

    for locale in locales:
        await queries.create_franchise_locale(
            db,
            FranchiseLocaleCreateRequest(**locale),
            franchise.id
        )

    return franchise.id


async def create_film_episode(
        db: AsyncSession,
        entry_id: int,
        premiere_world: date,
        premiere_digital: date,
        title: str,
        description: str
):
    episode = await queries.create_episode(
        db,
        EpisodeCreateRequest(
            entry_id=entry_id,
            episode_number=1,
            duration=2,
            premiere_world=premiere_world,
            premiere_digital=premiere_digital,
        )
    )

    await queries.create_episode_locale(
        db,
        EpisodeLocaleCreateRequest(
            language="ru",
            title=title,
            description=description
        ),
        episode.id
    )


async def create_morozko(db: AsyncSession, genres: dict, persons: dict) -> int:
    franchise_id = await create_franchise_with_locales(db, [
        {
            "language": "ru",
            "title": "Морозко",
            "description": "Советская сказка режиссёра Александра Роу"
        },
        {
            "language": "en",
            "title": "Morozko",
            "description": "Soviet fairy tale directed by Aleksandr Rou"
        }
    ])

    entry = await queries.create_entry(
        db,
        EntryCreateRequest(
            franchise_id=franchise_id,
            type="film",
            status="finished",
            rating_mpaa="g",
            age_rating=6,
            entry_number=1,
            duration=84,
            premiere_world=date(1964, 12, 28),
            premiere_digital=None,
            genres=[genres["Сказка"], genres["Семейный"], genres["Фэнтези"]],
            staff=[]
        )
    )

    entry_locales = [
        EntryLocaleCreateRequest(
            language="ru",
            title="Морозко",
            description="Настенька — добрая и работящая девушка, которую не любит мачеха. Та отправляет её в лес на верную гибель. Но Морозко, повелитель зимы, пощадил девушку и одарил её богатыми подарками."
        ),
        EntryLocaleCreateRequest(
            language="en",
            title="Jack Frost",
            description="A fairy tale about a kind girl Nastenka who is sent into the forest by her wicked stepmother, where she meets Father Frost."
        ),
    ]

    for locale in entry_locales:
        await queries.create_entry_locale(db, locale, entry.id)

    await create_film_episode(
        db, entry.id, entry.premiere_world, entry.premiere_digital,
        entry_locales[0].title, entry_locales[0].description
    )

    await queries.add_entry_staff(db, entry.id, [
        {"person_id": persons["Александр Роу"], "role": "director", "character_name": None},
        {"person_id": persons["Наталья Седых"], "role": "actor", "character_name": "Настенька"},
        {"person_id": persons["Эдуард Изотов"], "role": "actor", "character_name": "Иванушка"},
        {"person_id": persons["Инна Чурикова"], "role": "actor", "character_name": "Марфушенька"},
    ])

    return franchise_id


async def create_ivan_vasilyevich(db: AsyncSession, genres: dict, persons: dict) -> int:
    franchise_id = await create_franchise_with_locales(db, [
        {
            "language": "ru",
            "title": "Иван Васильевич меняет профессию",
            "description": "Комедия Леонида Гайдая о путешествии во времени"
        },
        {
            "language": "en",
            "title": "Ivan Vasilievich: Back to the Future",
            "description": "Comedy by Leonid Gaidai about time travel"
        }
    ])

    entry = await queries.create_entry(
        db,
        EntryCreateRequest(
            franchise_id=franchise_id,
            type="film",
            status="finished",
            rating_mpaa="pg",
            age_rating=12,
            entry_number=1,
            duration=88,
            premiere_world=date(1973, 9, 17),
            premiere_digital=None,
            genres=[genres["Комедия"], genres["Приключения"], genres["Фэнтези"]],
            staff=[]
        )
    )

    entry_locales = [
        EntryLocaleCreateRequest(
            language="ru",
            title="Иван Васильевич меняет профессию",
            description="Инженер-изобретатель Шурик создал машину времени, и в результате случайности управдом Бунша и вор Жорж попадают в XVI век, а Иван Грозный — в XX век."
        ),
        EntryLocaleCreateRequest(
            language="en",
            title="Ivan Vasilievich: Back to the Future",
            description="An engineer accidentally sends a building manager and a burglar back to the time of Ivan the Terrible, while the Tsar ends up in the 20th century."
        ),
    ]

    for locale in entry_locales:
        await queries.create_entry_locale(db, locale, entry.id)

    await create_film_episode(
        db, entry.id, entry.premiere_world, entry.premiere_digital,
        entry_locales[0].title, entry_locales[0].description
    )

    await queries.add_entry_staff(db, entry.id, [
        {"person_id": persons["Леонид Гайдай"], "role": "director", "character_name": None},
        {"person_id": persons["Юрий Яковлев"], "role": "actor", "character_name": "Иван Грозный / Бунша"},
        {"person_id": persons["Леонид Куравлёв"], "role": "actor", "character_name": "Жорж Милославский"},
        {"person_id": persons["Александр Демьяненко"], "role": "actor", "character_name": "Шурик"},
    ])

    return franchise_id


async def create_season_episodes(
        db: AsyncSession,
        season_id: int,
        episodes_data: list[tuple],
        season_num: int
):
    for idx, (title_ru, title_en, title_ja, air_date) in enumerate(episodes_data, 1):
        episode = await queries.create_episode(
            db,
            EpisodeCreateRequest(
                entry_id=season_id,
                episode_number=idx,
                duration=24,
                premiere_world=air_date,
                premiere_digital=air_date,
            )
        )

        await queries.create_episode_locale(
            db,
            EpisodeLocaleCreateRequest(
                language="ru",
                title=f"Эпизод {idx}: {title_ru}",
                description=f"Эпизод {idx} первого сезона" if season_num == 1 else f"Эпизод {idx} второго сезона"
            ),
            episode.id
        )

        await queries.create_episode_locale(
            db,
            EpisodeLocaleCreateRequest(
                language="en",
                title=f"Episode {idx}: {title_en}",
                description=f"Episode {idx} of season {season_num}"
            ),
            episode.id
        )

        await queries.create_episode_locale(
            db,
            EpisodeLocaleCreateRequest(
                language="ja",
                title=f"第{idx}話: {title_ja}",
                description=f"第{season_num}期第{idx}話"
            ),
            episode.id
        )


async def create_konosuba_season(
        db: AsyncSession,
        franchise_id: int,
        genres: dict,
        persons: dict,
        season_num: int,
        premiere_date: date,
        title_ru: str,
        title_en: str,
        desc_ru: str,
        desc_en: str,
        episodes_data: list[tuple]
) -> int:
    season = await queries.create_entry(
        db,
        EntryCreateRequest(
            franchise_id=franchise_id,
            type="season",
            status="finished",
            rating_mpaa="pg13",
            age_rating=16,
            entry_number=season_num,
            duration=24,
            premiere_world=premiere_date,
            premiere_digital=premiere_date,
            genres=[genres["Комедия"], genres["Фэнтези"], genres["Исэкай"], genres["Пародия"]],
            staff=[]
        )
    )

    await queries.create_entry_locale(db, EntryLocaleCreateRequest(
        language="ru", title=title_ru, description=desc_ru
    ), season.id)

    await queries.create_entry_locale(db, EntryLocaleCreateRequest(
        language="en", title=title_en, description=desc_en
    ), season.id)

    await queries.add_entry_staff(db, season.id, [
        {"person_id": persons["Нацумэ Акацуки"], "role": "writer", "character_name": None},
        {"person_id": persons["Канасаки Такаоми"], "role": "director", "character_name": None},
        {"person_id": persons["Амамия Соора"], "role": "actor", "character_name": "Аква"},
        {"person_id": persons["Такахаси Риэ"], "role": "actor", "character_name": "Мэгумин"},
        {"person_id": persons["Кайано Аи"], "role": "actor", "character_name": "Darkness"},
    ])

    await create_season_episodes(db, season.id, episodes_data, season_num)

    return season.id


async def create_konosuba(db: AsyncSession, genres: dict, persons: dict) -> int:
    # Богиня благословляет этот прекрасный мир (и душу того, кто писал эти тестовые данные)
    franchise_id = await create_franchise_with_locales(db, [
        {
            "language": "ru",
            "title": "Богиня благословляет этот прекрасный мир!",
            "description": "Комедийное исэкай-аниме о приключениях NEET'а Кадзумы в фэнтезийном мире"
        },
        {
            "language": "en",
            "title": "KonoSuba: God's Blessing on This Wonderful World!",
            "description": "A comedy isekai anime about NEET Kazuma's adventures in a fantasy world"
        },
        {
            "language": "ja",
            "title": "この素晴らしい世界に祝福を!",
            "description": "ファンタジー世界を舞台にしたコメディアニメ"
        }
    ])

    episodes_s1_data = [
        ("Этот самопровозглашённый рыцарь с ума сойти!", "This Self-Proclaimed Knight!", "この自称騎士に救援を!",
         date(2016, 1, 14)),
        ("Этому взрывающемуся приключению пламени!", "Explosion on This Wonderful Shop!", "この中二病に爆焔を!",
         date(2016, 1, 21)),
        ("Мир и покой моей первой работе!", "A Panty Treasure in This Right Hand!", "この右手にお宝を!",
         date(2016, 1, 28)),
        ("Взрывная магия для бесполезной богини!", "Explosion Magic for This Formidable Enemy!", "この駄女神に爆裂を!",
         date(2016, 2, 4)),
        ("За ценой этого волшебного меча!", "A Price for This Cursed Sword!", "この魔剣に祝福を!", date(2016, 2, 11)),
        ("Прощай, этот скучный мир!", "A Conclusion to This Battle!", "この煩わしい外界にさよならを!",
         date(2016, 2, 18)),
        ("За этого несравненного сокровища...", "A Second Death in This Freezing Season!",
         "この凍えそうな季節に二度目の死を!", date(2016, 2, 25)),
        ("Искушение этого замороженного дня!", "A Loving Hand for Our Party When We Can't Make It Through Winter!",
         "この凍てついた大地に愛の手を!", date(2016, 3, 3)),
        ("Благословение этой замечательной монете!", "God's Blessing on This Wonderful Shop!",
         "この素晴らしいショップに祝福を!", date(2016, 3, 10)),
        ("Финальная атака для генерала!", "God's Blessing on This Wonderful Ensemble!",
         "この素晴らしいチョーカーに祝福を!", date(2016, 3, 17)),
    ]

    await create_konosuba_season(
        db, franchise_id, genres, persons, 1, date(2016, 1, 14),
        "Этот замечательный мир! Сезон 1",
        "KonoSuba: God's Blessing on This Wonderful World! Season 1",
        "NEET Кадзума Сато умирает нелепой смертью и попадает в фэнтезийный мир. Богиня Аква предлагает ему начать новую жизнь, но он берёт её с собой как «стартовый бонус».",
        "NEET Kazuma Sato dies a ridiculous death and is sent to a fantasy world. He takes the goddess Aqua with him as his 'starting bonus'.",
        episodes_s1_data
    )

    episodes_s2_data = [
        ("Дай мне Божье благословение!", "Give Me Deliverance From This Judicial Injustice!", "この不当な裁判に救援を!",
         date(2017, 1, 12)),
        ("Моему другу подруга!", "A Friend for This Crimson Demon Girl!", "この紅魔の娘に友人を!", date(2017, 1, 19)),
        ("Спокойствия этому невесте!", "Peace for the Master of This Labyrinth!", "この迷宮の主に安らぎを!",
         date(2017, 1, 26)),
        ("Этот неутомимым покровителя!", "A Betrothal for This Noble Daughter!", "この貴族の令嬢に良縁を!",
         date(2017, 2, 2)),
        ("Прощение этому фанату!", "Servitude for This Masked Knight!", "この仮面の騎士に隷従を!", date(2017, 2, 9)),
    ]

    await create_konosuba_season(
        db, franchise_id, genres, persons, 2, date(2017, 1, 12),
        "Этот замечательный мир! Сезон 2",
        "KonoSuba: God's Blessing on This Wonderful World! Season 2",
        "Второй сезон приключений Кадзумы и его необычной команды в фэнтезийном мире.",
        "The second season of Kazuma and his eccentric party's adventures.",
        episodes_s2_data
    )

    movie = await queries.create_entry(
        db,
        EntryCreateRequest(
            franchise_id=franchise_id,
            type="film",
            status="finished",
            rating_mpaa="pg13",
            age_rating=16,
            entry_number=3,
            duration=90,
            premiere_world=date(2019, 8, 30),
            premiere_digital=date(2019, 9, 30),
            genres=[genres["Комедия"], genres["Фэнтези"], genres["Исэкай"], genres["Приключения"]],
            staff=[]
        )
    )

    movie_locales = [
        EntryLocaleCreateRequest(
            language="ru",
            title="Этот замечательный мир! Фильм: Багровая легенда",
            description="Полнометражный фильм о приключениях команды в деревне клана Малиновых демонов."
        ),
        EntryLocaleCreateRequest(
            language="en",
            title="KonoSuba: Legend of Crimson",
            description="A feature film about the party's adventures in the Crimson Demon village."
        ),
    ]

    for locale in movie_locales:
        await queries.create_entry_locale(db, locale, movie.id)

    await queries.add_entry_staff(db, movie.id, [
        {"person_id": persons["Нацумэ Акацуки"], "role": "writer", "character_name": None},
        {"person_id": persons["Канасаки Такаоми"], "role": "director", "character_name": None},
        {"person_id": persons["Амамия Соора"], "role": "actor", "character_name": "Аква"},
        {"person_id": persons["Такахаси Риэ"], "role": "actor", "character_name": "Мэгумин"},
        {"person_id": persons["Кайано Аи"], "role": "actor", "character_name": "Darkness"},
    ])

    await create_film_episode(
        db, movie.id, movie.premiere_world, movie.premiere_digital,
        movie_locales[0].title, movie_locales[0].description
    )

    return franchise_id


@router.post(
    "/test_data_1",
    status_code=status.HTTP_201_CREATED,
    summary="Add test data (Soviet films and Konosuba)"
)
async def seed_database(db: AsyncSession = Depends(get_session)):
    try:
        genres = await create_genres(db)
        persons = await create_persons(db)

        morozko_id = await create_morozko(db, genres, persons)
        ivan_id = await create_ivan_vasilyevich(db, genres, persons)
        konosuba_id = await create_konosuba(db, genres, persons)

        return {
            "message": "Test data successfully added!",
            "franchises": {
                "Морозко": morozko_id,
                "Иван Васильевич меняет профессию": ivan_id,
                "KonoSuba": konosuba_id,
            },
            "genres_count": len(genres),
            "persons_count": len(persons),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating test data: {str(e)}"
        )
