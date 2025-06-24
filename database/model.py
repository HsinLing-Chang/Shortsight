import os
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy import create_engine, String, Text, func, BIGINT, CHAR, TIMESTAMP, VARCHAR, ForeignKey, Enum, INTEGER, Index
from dotenv import load_dotenv
from datetime import date, datetime
# import logging

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USER = os.getenv("DB_USER")
engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/{DB_NAME}", echo=False)
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(
        INTEGER, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True)
    password:  Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    # relationship
    urls: Mapped["UrlMapping"] = relationship(
        "UrlMapping", back_populates="user", cascade="all, delete-orphan", passive_deletes=True, uselist=True)


class UrlMapping(Base):
    __tablename__ = "url_mapping"
    id: Mapped[int] = mapped_column(
        INTEGER, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(
        VARCHAR(255), nullable=False)
    uuid: Mapped[str] = mapped_column(
        VARCHAR(6), nullable=False, unique=True)
    short_key: Mapped[str] = mapped_column(
        VARCHAR(30), nullable=True, unique=True)
    target_url: Mapped[str] = mapped_column(
        VARCHAR(2048), nullable=False, )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)

    # relationship
    user: Mapped["User"] = relationship("User", back_populates="urls")
    events: Mapped[list["EventLog"]] = relationship(
        "EventLog", back_populates="mapping", cascade="all, delete-orphan", passive_deletes=True, uselist=True)
    utm: Mapped["UTMParams"] = relationship(
        "UTMParams", back_populates="mapping", cascade="all, delete-orphan", passive_deletes=True, uselist=False)
    qr_code: Mapped["QRCode"] = relationship(
        "QRCode", back_populates="mapping", cascade="all, delete-orphan", passive_deletes=True,  uselist=False)
    # traffic_sources: Mapped[list["EventTrafficSource"]] = relationship(
    # "EventTrafficSource", back_populates="mapping", cascade="all, delete-orphan", passive_deletes=True)


class UTMParams(Base):
    __tablename__ = "utm_params"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    mapping_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("url_mapping.id", ondelete="CASCADE"), nullable=True, index=True)
    utm_source: Mapped[str | None] = mapped_column(VARCHAR(50), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(VARCHAR(50), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(
        VARCHAR(50), nullable=True)

    # relationship
    mapping: Mapped["UrlMapping"] = relationship(
        "UrlMapping", back_populates="utm")

    __table_args__ = (
        Index("idx_source_medium",  "utm_source", "utm_medium"),
    )


class QRCode(Base):
    __tablename__ = "qr_code"
    id: Mapped[int] = mapped_column(
        INTEGER, primary_key=True, autoincrement=True)
    mappping_url: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("url_mapping.id", ondelete="CASCADE"), index=True)
    image_path: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False)
    # relationship
    mapping: Mapped["UrlMapping"] = relationship(
        "UrlMapping", back_populates="qr_code", uselist=False)


class EventLog(Base):
    __tablename__ = "event_log"
    id: Mapped[int] = mapped_column(
        INTEGER, primary_key=True, autoincrement=True)
    mapping_id: Mapped[int] = mapped_column(
        INTEGER, ForeignKey("url_mapping.id", ondelete="CASCADE"), nullable=False, index=True)
    visitor_id: Mapped[str | None] = mapped_column(
        CHAR(36), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False, index=True)

    event_type: Mapped[str] = mapped_column(
        Enum("scan", "click", name="event_type"), nullable=False, index=True)
    # Raw
    referer: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str] = mapped_column(
        VARCHAR(50), nullable=True, index=True)
    # device
    device_type: Mapped[str] = mapped_column(VARCHAR(20), nullable=True)
    device_browser: Mapped[str] = mapped_column(VARCHAR(20), nullable=True)
    device_os: Mapped[str] = mapped_column(VARCHAR(20), nullable=True)
    app_source: Mapped[str] = mapped_column(VARCHAR(20), nullable=True)
    # referer
    domain: Mapped[str | None] = mapped_column(
        VARCHAR(100), nullable=True, comment="從 referrer 拆解出來的 domain")
    source: Mapped[str | None] = mapped_column(
        VARCHAR(100), nullable=True, comment="utm_source 或 domain")
    medium: Mapped[str | None] = mapped_column(
        VARCHAR(50), nullable=True, comment="utm_medium 或分類結果，例如 organic/referral")
    campaign: Mapped[str | None] = mapped_column(VARCHAR(100), nullable=True)
    channel: Mapped[str | None] = mapped_column(VARCHAR(
        50), nullable=True, comment="channel 分類，例如 Social/Search/Direct")
    # relationships
    mapping: Mapped["UrlMapping"] = relationship(
        "UrlMapping", back_populates="events")
    # source_info: Mapped["EventTrafficSource"] = relationship(
    #     "EventTrafficSource", back_populates="event", uselist=False, cascade="all, delete-orphan")


# class EventTrafficSource(Base):
#     __tablename__ = "event_traffic_source"
#     id: Mapped[int] = mapped_column(
#         INTEGER, primary_key=True, autoincrement=True)
#     visitor_id: Mapped[str | None] = mapped_column(
#         CHAR(36), nullable=True, index=True)
#     event_type: Mapped[str] = mapped_column(
#         Enum("scan", "click", name="event_type"), nullable=False, index=True)
#     mapping_id: Mapped[int] = mapped_column(
#         ForeignKey("url_mapping.id", ondelete="CASCADE"), index=True)
#     domain: Mapped[str | None] = mapped_column(
#         VARCHAR(100), nullable=True, comment="從 referrer 拆解出來的 domain")
#     source: Mapped[str | None] = mapped_column(
#         VARCHAR(100), nullable=True, comment="utm_source 或 domain")
#     medium: Mapped[str | None] = mapped_column(
#         VARCHAR(50), nullable=True, comment="utm_medium 或分類結果，例如 organic/referral")
#     campaign: Mapped[str | None] = mapped_column(VARCHAR(100), nullable=True)
#     channel: Mapped[str | None] = mapped_column(VARCHAR(
#         50), nullable=True, comment="channel 分類，例如 Social/Search/Direct")
#     created_at: Mapped[datetime] = mapped_column(
#         TIMESTAMP(timezone=True), server_default=func.current_timestamp(), nullable=False, index=True)
#     mapping: Mapped["UrlMapping"] = relationship(
#         "UrlMapping", back_populates="traffic_sources")


class IpLocation(Base):
    __tablename__ = "ip_location"
    ip_address: Mapped[str] = mapped_column(VARCHAR(50), primary_key=True)
    country: Mapped[str] = mapped_column(VARCHAR(100), nullable=True)
    city: Mapped[str] = mapped_column(VARCHAR(100), nullable=True)
    latitude: Mapped[float] = mapped_column(nullable=True)
    longitude: Mapped[float] = mapped_column(nullable=True)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, autocommit=False)
