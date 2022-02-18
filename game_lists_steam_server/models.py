# pyright: reportGeneralTypeIssues=false
from peewee import AutoField, BigIntegerField, BooleanField, DateTimeField, FloatField, MySQLDatabase, Model, TextField, ForeignKeyField, IntegerField, CompositeKey
import os

mariadb_password = os.getenv('MARIADB_PASSWORD', None)


class BaseModel(Model):
    class Meta:
        database = MySQLDatabase('game_lists_steam_server', user='game_lists_steam_server',
                                 password=mariadb_password, host='localhost', port=3306)


class Player(BaseModel):
    id = BigIntegerField(primary_key=True)
    name = TextField(null=True)
    profile_url = TextField(unique=True, null=True)
    is_public = BooleanField(null=True)
    is_game_details_public = BooleanField(null=True)
    update_time = DateTimeField()
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
    minutes = IntegerField()

    class Meta:
        primary_key = CompositeKey('player', 'game')

    @property
    def __dict__(self):
        return {
            'game_id': self.game.id,
            'minutes': self.minutes,
        }
