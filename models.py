import datetime

from flask_bcrypt import generate_password_hash,check_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('pickme.db')
DATABASE_RAW = SqliteDatabase('rawpost.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)
    is_writer = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_posts(self):
        return Post.select().where(Post.writer==self)

    def get_stream(self):
        return Post.select().where((Post.writer << self.following(
            )) |(Post.writer==self))

    def get_symbols(self):
        return Post.select().where(Post.symbol == self)

    def following(self,writer=3):
        '''The users that we are following'''
        return (
        User.select(User,Relationship,Writer).join(Relationship,
        on=Relationship.from_user
        ).join(Writer,on=Relationship.to_user).naive(Writer).where(
        Relationship.from_user ==self,Relationship.to_user==writer))

    def followers(self):
        '''Get users following the current user'''
        return (
            User.select().join(
                Relationship,on=Relationship.from_user
            ).where(
                Relationship.to_user == self))

    def trial(self):
        return True

    @classmethod
    def create_user(cls,username,email,password,admin=False,is_writer=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password = generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

class Writer(Model):
    name = CharField(unique=True)
    company = CharField(max_length=50)
    bio = CharField(max_length=200)
    website = CharField(max_length=500)

    class Meta:
        database = DATABASE
        order_by = ('-name',)

    def followers(self):
        return (
        Writer.select().join(
            Relationship,on=Relationship.from_user
            ).where(Relationship.to_user==self))

    def following(self):
        return (
        Writer.select().join(
            Relationship,on=Relationship.from_user
            ).where(Relationship.to_user==self))


class PropsectiveWriter(Model):
    name = CharField(unique=True)
    company = CharField(max_length=50)
    bio = CharField(max_length=200)
    website = CharField(max_length=500)

    class Meta:
        database = DATABASE
        order_by = ('-name',)

class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    link = CharField(max_length=500)
    side = BooleanField(default=True)
    symbol = CharField(max_length=9)
    exchange = CharField(max_length=10)
    title = CharField(max_length=500,unique=True)
    entry_px = FloatField(default=10)
    entry = TextField()
    writer = ForeignKeyField(
        rel_model=Writer,
        related_name='posts',
    )

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)

class RawPost(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    link = CharField(max_length=500)
    side = BooleanField(default=True)
    symbol = CharField(max_length=9)
    title = CharField(max_length=500)
    entry_px = FloatField(default=10)
    entry = TextField()
    writer = IntegerField()

    class Meta:
        database = DATABASE_RAW
        order_by = ('-timestamp',)

class Relationship(Model):
    from_user = ForeignKeyField(User,related_name='relationships')
    to_user = ForeignKeyField(Writer,related_name='related_to')

    class Meta:
        database = DATABASE
        indexes= ((('from_user','to_user'),True),)

class Company(Model):
    symbol = CharField(max_length=10)
    name = CharField(max_length=75)
    sector = CharField(max_length=60)
    exchange = CharField(max_length=10)

    class Meta:
        database = DATABASE
        order_by = ('name',)

def initialize():
    DATABASE.connect()
    DATABASE_RAW.connect()
    DATABASE.create_tables([PropsectiveWriter,
        User,Writer,Post,Relationship,Company],safe=True)
    DATABASE_RAW.create_tables([RawPost],safe=True)
    DATABASE.close()
    DATABASE_RAW.close()
