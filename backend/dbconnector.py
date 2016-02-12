import psycopg2

from configkeys import DBConfig

class PSQLConnection(object):
    """docstring for PSQLConnection"""
    
    def __init__(self, arg):
        super(PSQLConnection, self).__init__()
        self.arg = arg

    def get_connection():
        db_host = DBConfig.get_parameter('db_host')
        db_port = DBConfig.get_parameter('db_port')
        db_name = DBConfig.get_parameter('db_name')
        db_user = DBConfig.get_parameter('db_user')
        db_pass = DBConfig.get_parameter('db_pass')
        return  psycopg2.connect(host=db_host, port=db_port, database=db_name, user=db_user, password=db_pass)