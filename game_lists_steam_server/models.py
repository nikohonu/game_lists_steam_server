# pyright: reportGeneralTypeIssues=false
import os
from pathlib import Path

from appdirs import user_data_dir
from peewee import (AutoField, BigIntegerField, BooleanField, CompositeKey,
                    DateTimeField, FloatField, ForeignKeyField, IntegerField,
                    Model, SqliteDatabase, TextField)

data_dir = Path(user_data_dir('game_lists_steam_server', 'nikohonu'))


class BaseModel(Model):
    class Meta:
        data_dir.mkdir(parents=True, exist_ok=True)
        database = SqliteDatabase(data_dir / 'data.db')


class Player(BaseModel):
    id = BigIntegerField(primary_key=True)
    name = TextField(null=True)
    profile_url = TextField(unique=True, null=True)
    is_public = BooleanField(null=True)
    is_game_details_public = BooleanField(null=True)
    update_time = DateTimeField(null=True)
    playtime_update_time = DateTimeField(null=True)

    @property
    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name,
            'profile_url': self.profile_url,
            'is_public': self.is_public,
            'is_game_details_public': self.is_game_details_public,
        }


class Game(BaseModel):
    id = BigIntegerField(primary_key=True)
    name = TextField()
    update_time = DateTimeField(null=True)

    @ property
    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Tag(BaseModel):
    id = AutoField()
    name = TextField(unique=True)

    @property
    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class Genre(BaseModel):
    id = BigIntegerField(primary_key=True)
    name = TextField(unique=True)

    @ property
    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name,
        }


class GameTag(BaseModel):
    game = ForeignKeyField(Game, on_delete='CASCADE')
    tag = ForeignKeyField(Tag, on_delete='CASCADE')
    value = FloatField()

    class Meta:
        primary_key = CompositeKey('game', 'tag')

    @property
    def __dict__(self):
        return {
            'id': self.tag.id,
            'name': self.tag.name,
            'value': self.value,
        }


class GameGenre(BaseModel):
    game = ForeignKeyField(Game, on_delete='CASCADE')
    genre = ForeignKeyField(Genre, on_delete='CASCADE')

    class Meta:
        primary_key = CompositeKey('game', 'genre')


class Playtime(BaseModel):
    player = ForeignKeyField(Player, on_delete='CASCADE')
    game = ForeignKeyField(Game, on_delete='CASCADE')
    minutes = IntegerField(null=True)

    class Meta:
        primary_key = CompositeKey('player', 'game')

    @property
    def __dict__(self):
        return {
            'game_id': self.game.id,
            'minutes': self.minutes,
        }
