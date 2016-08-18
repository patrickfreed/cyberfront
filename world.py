from mongoengine import Document, StringField


class World(Document):
    name = StringField()
