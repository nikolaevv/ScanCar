from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
car = Table('car', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('brand', String(length=255)),
    Column('model', String(length=255)),
    Column('price', Float(precision=64)),
    Column('description', String(length=9000)),
    Column('production_date', Integer),
    Column('color', String(length=255)),
    Column('bodywork', String(length=255)),
    Column('engine', String(length=255)),
    Column('tax', String(length=255)),
    Column('kpp', String(length=255)),
    Column('image_url_1', String(length=255)),
    Column('image_url_2', String(length=255)),
    Column('image_url_3', String(length=255)),
    Column('steering_wheel', String(length=255)),
    Column('customs', String(length=255)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['car'].columns['customs'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['car'].columns['customs'].drop()
