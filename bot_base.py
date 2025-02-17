
import pyrolog
import tomllib
import string
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pyromod import listen, ikb
from pyrogram import Client, filters, types

import database

####

with open('config.toml', 'rb') as f:
    config = tomllib.load(f)
    
engine = create_engine(config['database_uri'])
database.Base.metadata.create_all(engine)

logger = pyrolog.get_colored_logger(log_level=config['log_level'])
logger.add_handler(pyrolog.FileHandler('log.txt', log_level='debug'))


def cbfilter(data):
    async def func(flt, _, query):
        return flt.data == query.data

    # "data" kwarg is accessed with "flt.data" above
    return filters.create(func, data=data)


def cbfilter_param(data):
    async def func(flt, _, query):
        if len(query.data) < len(flt.data):
            return False

        return query.data[:len(flt.data)] == flt.data

    # "data" kwarg is accessed with "flt.data" above
    return filters.create(func, data=data)


def q_error_handling(f):
    async def deco(client, q: types.CallbackQuery):
        try:
            await f(client, q)
        except Exception as e:
            logger.exception('in chat {} (@{}, {}) CQ with data "{}" caused exception: {}',
                             q.from_user.first_name, q.from_user.username, q.from_user.id, q.data, e)
    return deco


def cmd_error_handling(f):
    async def deco(client, m: types.Message):
        try:
            await f(client, m)
        except Exception as e:
            logger.exception('in chat {} (@{}, {}) command "{}" caused exception: {}',
                             m.from_user.first_name, m.from_user.username, m.from_user.id, m.text, e)
    return deco

####

RANDOM_ALPHABET = string.ascii_letters + string.digits + '-'


def random_string(length: int) -> str:
    return ''.join([random.choice(RANDOM_ALPHABET) for _ in range(length)])

####

client = Client('bot', api_id=config['api_id'], api_hash=config['api_hash'], bot_token=config['bot_token'])

