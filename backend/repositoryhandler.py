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
    proc_stdout = process.communicate()[1].strip().decode('utf-8')
    print (proc_stdout)
    repository_name_matcher = re.search('\'(.*)\'', proc_stdout)
    return repository_name_matcher.group(1)

def get_repository_master_branch(repository_name):
    repository_path = repository_default_directory + repository_name
    command = 'cat .git/HEAD'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE, shell=True, cwd=repository_path)
    proc_stdout = process.communicate()[0].strip()
    master_branch_name_matcher = re.search('ref:.*\/(.*)', str(proc_stdout))
    return master_branch_name_matcher.group(1).replace('\'', '')

def insert_cloned_repo_info(repository_name, master_branch):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("insert into repositories (name, clone_url, master_branch) values (%s, %s, %s)", (repository_name, clone_url, master_branch))
    connection.commit()
    connection.close()

clone_url  = sys.argv[1]
repository_default_directory = DiretoryConfig.get_parameter('repository_directory')       

create_repository_directory(repository_default_directory)

if has_to_clone_repository(clone_url):
    repository_name = clone_repository(clone_url)
    get_repository_master_branch = get_repository_master_branch(repository_name)
    insert_cloned_repo_info(repository_name, get_repository_master_branch)