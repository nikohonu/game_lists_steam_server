# pyright: reportGeneralTypeIssues=false
from peewee import BigIntegerField, BooleanField, DateTimeField, MySQLDatabase, Model, TextField, ForeignKeyField, IntegerField, CompositeKey
import os
import time

mariadb_password = os.getenv('MARIADB_PASSWORD', None)


class BaseModel(Model):
    class Meta:
        database = MySQLDatabase('game_lists_steam_server', user='game_lists_steam_server',
                                 password=mariadb_password, host='localhost', port=3306)


class Player(BaseModel):
    id = BigIntegerField(primary_key=True)
    name = TextField(null=True)
    profile_url = TextField(unique=True)
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
    update_time = DateTimeField()

    @ property
    def __dict__(self):
        return {
            'id': self.id,
            'name': self.name,
        }


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
