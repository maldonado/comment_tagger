import psycopg2

import Config

db_host = Config.keys['db_host']
db_port = Config.keys['db_port']
db_name = Config.keys['db_name']
db_user = Config.keys['db_user']
db_pass = Config.keys['db_pass']

def get_connection():
    return  psycopg2.connect(host=db_host, port=db_port, database=db_name, user=db_user, password=db_pass)