from peewee import BigIntegerField, DateTimeField, MySQLDatabase, Model, AutoField, TextField, ForeignKeyField, IntegerField, CompositeKey
import os

mariadb_password = os.getenv('MARIADB_PASSWORD', None)


class BaseModel(Model):
    class Meta:
        database = MySQLDatabase('game_lists_steam_server', user='game_lists_steam_server',
                                 password=mariadb_password, host='localhost', port=3306)


class Player(BaseModel):
    id = BigIntegerField(primary_key=True)
    name = TextField(null=True)
    profile_url = TextField()
    update_time = DateTimeField(null=True)


class Game(BaseModel):
    id = AutoField()
    name = TextField()
    update_time = DateTimeField()


class Playtime(BaseModel):
    player = ForeignKeyField(Player, on_delete='CASCADE')
    game = ForeignKeyField(Game, on_delete='CASCADE')
    playtime = IntegerField()
    update_time = DateTimeField()

    class Meta:
        primary_key = CompositeKey('player', 'game')
