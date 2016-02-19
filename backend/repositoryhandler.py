import os
import re
import sys
import subprocess

from configkeys import DiretoryConfig
from dbconnector import PSQLConnection

def create_repository_directory(path):
    if not os.path.exists(path):
        """creating the default repository folders TODO: move to install script"""
        subprocess.call(["mkdir", path])

def has_to_clone_repository(clone_url):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("select count(*) from repositories where clone_url = %s", (clone_url,))
    result = cursor.fetchone()[0]
    connection.close()
    return result == 0

def clone_repository(clone_url):
    command = 'git clone ' + clone_url
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE, shell=True, cwd=repository_default_directory)
    proc_stdout = process.communicate()[1].strip()
    repository_name_matcher = re.search('\'(.*)\'', str(proc_stdout))
    return repository_name_matcher.group(1)

def insert_cloned_repo_info(repository_name):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("insert into repositories (name, clone_url) values (%s, %s)", (repository_name, clone_url))
    connection.commit()
    connection.close()

clone_url  = sys.argv[1]
repository_default_directory = DiretoryConfig.get_parameter('repository_directory')       

create_repository_directory(repository_default_directory)

if has_to_clone_repository(clone_url):
    repository_name = clone_repository(clone_url)
    insert_cloned_repo_info(repository_name)