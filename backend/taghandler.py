import os
import re
import sys
import subprocess
import shutil

from configkeys import DiretoryConfig, TagHandlerConfig
from dbconnector import PSQLConnection

# example of expected tuple [('everton'), ('aries')]
def fetch_repositories(repo_list = tuple([])):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    if not repo_list:
        cursor.execute("select id, name, clone_url, cloned_date from repositories order by 1")
    else:
        cursor.execute("select id, name, clone_url, cloned_date from repositories where name in %s", [tuple(repo_list),])
    query_return = cursor.fetchall()
    connection.close()
    return query_return
    
def list_repository_tags(repository_name):
    repository_path = DiretoryConfig.get_parameter('repository_directory') + repository_name
    command = "git log --tags --date-order --reverse --simplify-by-decoration --pretty=%ai%d"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE, shell=True, cwd=repository_path)
    return process.communicate()[0].strip().decode("utf-8").split('\n')

def create_directory(path):
    if not os.path.exists(path):
        subprocess.call(["mkdir", path]) 

def clean_unwanted_files(path):
    file_regex = TagHandlerConfig.get_parameter('unwanted_file_regex')
    directory_regex = TagHandlerConfig.get_parameter('unwanted_directory_regex')
    for root, dirs, files in os.walk(path):
        if file_regex is not None:
            for f in files:
                if re.match(file_regex, f) is not None:
                    os.unlink(os.path.join(root, f))
        if directory_regex is not None:
            for d in dirs:
                if re.match(directory_regex, d) is not None:
                    shutil.rmtree(os.path.join(root, d))

def snapshot_the_repo(repository_name, tag):
    repository_path = DiretoryConfig.get_parameter('repository_directory') + repository_name
    tag_path = repository_path + "_tags/" + tag
    checkout = "git checkout " + tag 
    copy_repo =  "cp -r ./ ../" + repository_name + "_tags/" + tag
    command = checkout + " ; " + copy_repo 
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE, shell=True, cwd=repository_path)
    process.communicate()[1].strip().decode("utf-8")
    clean_unwanted_files(tag_path)

def insert_snapshot_version_info(repository_id, name, version_date, version_order):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("insert into tags (repository_id, name, version_date, version_order) values (%s, %s, to_timestamp(%s, 'YYYY-MM-DD HH24:MI:SS'), %s)", (repository_id, name, version_date, version_order))
    connection.commit()
    connection.close()

tags_regex = '(\d\d\d\d\-\d\d\-\d\d\s\d\d:\d\d:\d\d)|\(tag:\s([A-Za-z0-9\-\_\.+]*)\)'

repository_list = fetch_repositories()
for repository_entry in repository_list:
    repository_id   = repository_entry[0]
    repository_name = repository_entry[1]
    repository_url  = repository_entry[2]
    repository_cloned_date = repository_entry[3]

    tag_entry_list = list_repository_tags(repository_name)
    tags_directory = DiretoryConfig.get_parameter('repository_directory') + repository_name + "_tags/"
    create_directory(tags_directory)

    version_order = 0
    for tag_entry in tag_entry_list:
        if re.search(tags_regex, tag_entry) is not None:
            matche_groups = re.findall(tags_regex, tag_entry)
            """It has to have match for tag and date (merge has date but not tag)"""
            if len(matche_groups) == 2:
                tag_date = matche_groups[0][0]
                tag = matche_groups[1][1]

                create_directory(tags_directory + tag)
                snapshot_the_repo(repository_name, tag)
                insert_snapshot_version_info(repository_id, tag, tag_date, version_order)
                version_order = version_order + 1
                print(tag, tag_date)
