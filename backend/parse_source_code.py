import os
import sys
import re
import subprocess

import Config, PSQLConnection

clone_url  = sys.argv[1]
repository_default_directory = Config.keys['repository_directory']

"""creating the default repository folders TODO: move to install script"""
subprocess.call(["mkdir", repository_default_directory ])

command = 'git clone ' + clone_url
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE, shell=True, cwd=repository_default_directory)
proc_stdout = process.communicate()[1].strip()
repository_name_matcher = re.search('\'(.*)\'', str(proc_stdout))
repository_name = repository_name_matcher.group(1)

connection = PSQLConnection.get_connection()
cursor = connection.cursor()
cursor.execute("insert into cloned_repositories (name, clone_url) values (%s, %s)", (repository_name, clone_url))
connection.commit()