from datetime import datetime, date, UTC
from typing import List, Optional
from sqlalchemy import String, Text, Integer, SmallInteger, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

class Base(DeclarativeBase):
    pass

class EntryType(str, enum.Enum):
    FILM = "film"
    SEASON = "season"

class MPAARating(str, enum.Enum):
    G = "g"
    PG = "pg"
    PG13 = "pg13"
    R = "r"
    NC17 = "nc17"

class ContentStatus(str, enum.Enum):
    ANNOUNCED = "announced"
    ONGOING = "ongoing"
    FINISHED = "finished"
    CANCELLED = "cancelled"

class StaffRole(str, enum.Enum):
    ACTOR = "actor"
    DIRECTOR = "director"
    PRODUCER = "producer"
    WRITER = "writer"
    COMPOSER = "composer"
    OTHER = "other"

class Franchise(Base):
    __tablename__ = "franchises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    locales: Mapped[List["FranchiseLocale"]] = relationship(back_populates="franchise", cascade="all, delete-orphan", lazy="selectin")
    entries: Mapped[List["Entry"]] = relationship(back_populates="franchise", cascade="all, delete-orphan", lazy="selectin")

class FranchiseLocale(Base):
    __tablename__ = "franchise_locales"
    __table_args__ = (
        {"schema": None},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    franchise_id: Mapped[int] = mapped_column(Integer, ForeignKey("franchises.id", ondelete="CASCADE"), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    franchise: Mapped["Franchise"] = relationship(back_populates="locales")

class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    franchise_id: Mapped[int] = mapped_column(Integer, ForeignKey("franchises.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[EntryType] = mapped_column(SQLEnum(EntryType), nullable=False, index=True)
    status: Mapped[ContentStatus] = mapped_column(SQLEnum(ContentStatus), nullable=False, index=True)
    entry_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rating_mpaa: Mapped[Optional[MPAARating]] = mapped_column(SQLEnum(MPAARating), nullable=True)
    age_rating: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    premiere_world: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    premiere_digital: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now,
                                                 onupdate=datetime.now)

    franchise: Mapped["Franchise"] = relationship(back_populates="entries")
    locales: Mapped[List["EntryLocale"]] = relationship(back_populates="entry", cascade="all, delete-orphan")
    episodes: Mapped[List["Episode"]] = relationship(back_populates="entry", cascade="all, delete-orphan")
    genres: Mapped[List["Genre"]] = relationship(secondary="entry_genres", back_populates="entries")
    staff: Mapped[List["EntryStaff"]] = relationship(back_populates="entry", cascade="all, delete-orphan")

class EntryLocale(Base):
    __tablename__ = "entry_locales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_id: Mapped[int] = mapped_column(Integer, ForeignKey("entries.id", ondelete="CASCADE"), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    entry: Mapped["Entry"] = relationship(back_populates="locales")

class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_id: Mapped[int] = mapped_column(Integer, ForeignKey("entries.id", ondelete="CASCADE"), nullable=False, index=True)
    episode_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    premiere_world: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    premiere_digital: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    entry: Mapped["Entry"] = relationship(back_populates="episodes")
    locales: Mapped[List["EpisodeLocale"]] = relationship(back_populates="episode", cascade="all, delete-orphan")

class EpisodeLocale(Base):
    __tablename__ = "episode_locales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    episode_id: Mapped[int] = mapped_column(Integer, ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(5), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    episode: Mapped["Episode"] = relationship(back_populates="locales")

class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    entries: Mapped[List["Entry"]] = relationship(secondary="entry_genres", back_populates="genres")

class EntryGenre(Base):
    __tablename__ = "entry_genres"

    entry_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("entries.id", ondelete="CASCADE"),
        primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True
    )

class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    en_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    staff_entries: Mapped[List["EntryStaff"]] = relationship(back_populates="person", cascade="all, delete-orphan")

class EntryStaff(Base):
    __tablename__ = "entry_staff"

    entry_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("entries.id", ondelete="CASCADE"),
        primary_key=True
    )
    person_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("persons.id", ondelete="CASCADE"),
        primary_key=True
    )
    role: Mapped[StaffRole] = mapped_column(
        SQLEnum(StaffRole),
        primary_key=True,
        nullable=False
    )
    character_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    entry: Mapped["Entry"] = relationship(back_populates="staff")
    person: Mapped["Person"] = relationship(back_populates="staff_entries")
