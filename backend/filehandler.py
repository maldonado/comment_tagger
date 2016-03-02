import os
import re
import sys
import subprocess
import shutil

from configkeys import DiretoryConfig, FileHandlerConfig
from dbconnector import PSQLConnection

# example of expected tuple [('everton'), ('aries')] move elsewhere and extract class 
def fetch_repositories(repo_list = tuple([])):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    if not repo_list:
        cursor.execute("select id, name, master_branch, clone_url, cloned_date from repositories order by 1")
    else:
        cursor.execute("select id, name, master_branch, clone_url, cloned_date from repositories where name in %s", [tuple(repo_list),])
    query_return = cursor.fetchall()
    connection.close()
    return query_return

def checkout_to_latest_version(repository_name, master_branch):
    repository_path = DiretoryConfig.get_parameter('repository_directory') + repository_name
    command = "git checkout " + master_branch
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE, shell=True, cwd=repository_path)
    return process.communicate()[0].strip().decode("utf-8").split('\n')

def insert_file(repository_id, name, absolute_path):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("insert into files (repository_id, name, file_path) values (%s,%s,%s) returning id", (repository_id, name, absolute_path))
    inserted_id = cursor.fetchone()[0]
    connection.commit()
    connection.close()
    return inserted_id

def extract_file_versions(repository_id, repository_name):

    repository_path = DiretoryConfig.get_parameter('repository_directory') + repository_name
    git_log_file_regex = FileHandlerConfig.get_parameter('git_log_file_regex')

    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.select('select id, file_path from files where repository_id = %s', (repository_id, ))
    files_results =  cursor.fetchall()

    for files_results_line in files_results:

        file_id = files_results_line[0]
        file_path = files_results_line[1]
    
        commit_hash     = ''
        author_name     = ''
        author_email    = ''
        author_date     = ''
        version_path    = ''

        command = "git log --follow --stat=350 --stat-graph-width=2 -- " + file_path
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE, shell=True, cwd=repository_path)
        git_log_output = process.communicate()[0].strip().decode("utf-8").split('\n')

        # print (git_log_output)
        for git_log_output_line in git_log_output:
            # removes non ascii characters
            stripped = (c for c in git_log_output_line if 0 < ord(c) < 127)
            stripped_line = ''.join(stripped)
            
            git_log_file_matcher = re.match(git_log_file_regex, stripped_line)
            if git_log_file_matcher is not None:
                if git_log_file_matcher.group(1):         
                    if commit_hash is not '':
                        cursor.execute("insert into file_versions (file_id, commit_hash, author_name, author_email, author_date, version_path) values ( %s, %s, %s, %s, to_timestamp(%s, 'Dy Mon DD HH24:MI:SS YYYY +-####'), %s)", (file_id, commit_hash, author_name, author_email, author_date, version_path))                  
                    commit_hash  = git_log_file_matcher.group(1)  

                if git_log_file_matcher.group(2):
                    author_name  = git_log_file_matcher.group(2)
                if git_log_file_matcher.group(3):
                    author_email = git_log_file_matcher.group(3) 
                if git_log_file_matcher.group(4):
                    author_date  = git_log_file_matcher.group(4)
                if git_log_file_matcher.group(5):
                    version_path = git_log_file_matcher.group(5).strip()
                    if '=>' in version_path:
                        # select only the renamed part of the path
                        version_path = version_path.replace('{','').replace('}','').split('=>')[1].strip()
            
        # last line of the file
        cursor.execute("insert into file_versions (file_id, commit_hash, author_name, author_email, author_date, version_path) values ( %s, %s, %s, %s, to_timestamp(%s, 'Dy Mon DD HH24:MI:SS YYYY +-####'), %s)", (file_id, commit_hash, author_name, author_email, author_date, version_path))
        connection.commit()
        connection.close()

def create_directory(path):
    if not os.path.exists(path):
        subprocess.call(["mkdir", "-p", path]) 

def checkout_file_versions(repository_id, repository_name, master_branch):
    repository_directory = DiretoryConfig.get_parameter('repository_directory') + repository_name

    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()

    cursor.execute("select id from files where repository_id = %s", (repository_id, ))
    files_results = cursor.fetchall()

    for file_line in files_results:
        file_id = file_line[0]
        
        checkout_to_latest_version(repository_name, master_branch)
        file_versions_directory = DiretoryConfig.get_parameter('file_versions_directory') + repository_name
        create_directory(file_versions_directory)

        cursor.execute('select id, commit_hash, version_path from file_versions where file_id = %s where has_local_file is false order by author_date', (file_id, ))
        file_vesions_result = cursor.fetchall()

        for file_versions_line in file_vesions_result:
            file_versions_id = file_versions_line[0]
            commit_hash = file_versions_line[1]
            version_path = file_versions_line[2]
            file_extension = version_path.split('.')[-1]

            git_checkout = "git checkout " + commit_hash
            cp_file = "cp " + version_path + " ../" + file_versions_directory +"/"+ str(file_id) + "_" + commit_hash +"."+  file_extension  

            print (cp_file)

            command = git_checkout + ";" + cp_file
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE, shell=True, cwd=repository_directory)
            git_log_output = process.communicate()[0].strip().decode("utf-8").split('\n')

            cursor.execute("update file_versions set has_local_file = true where id = %s", (file_versions_id, ))
            connection.commit()

    connection.close()

def process_parseable_files(repository_id, repository_name):
    repository_path = DiretoryConfig.get_parameter('repository_directory') + repository_name
    file_regex = FileHandlerConfig.get_parameter('parseable_files_regex')
    for root, dirs, files in os.walk(repository_path):
        for file in files:
            file_matcher = re.match(file_regex, file)
            if file_matcher is not None:
                absolute_path = os.path.join(root, file).replace(repository_path + '/', '')
                file_id = insert_file(repository_id, file, absolute_path)                
                
                print (absolute_path)
                
repository_list = fetch_repositories()

for repository_entry in repository_list:
    repository_id   = repository_entry[0]
    repository_name = repository_entry[1]
    master_branch   = repository_entry[2]
    repository_url  = repository_entry[3]
    repository_cloned_date = repository_entry[4]

    checkout_to_latest_version(repository_name, master_branch)
    process_parseable_files(repository_id, repository_name)
    extract_file_versions(repository_id, repository_name)
    checkout_file_versions(repository_id, repository_name, master_branch)