import os
import re
import sys
import subprocess
import shutil


from configkeys import DiretoryConfig
from dbconnector import PSQLConnection
from lxml import etree

def create_directory(path):
    if not os.path.exists(path):
        subprocess.call(["mkdir", "-p", path]) 

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

def parse_files_using_srcml(repository_id, repository_name):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()

    cursor.execute("select id from files where repository_id = %s", (repository_id, ))
    files_results = cursor.fetchall()

    for file_line in files_results:
        file_id = file_line[0]
        file_versions_directory = DiretoryConfig.get_parameter('file_versions_directory') + repository_name
        parsed_files_directory = DiretoryConfig.get_parameter('parsed_files_directory') + repository_name
        create_directory(parsed_files_directory)
        cursor.execute('select id, commit_hash, version_path from file_versions where file_id = %s and has_parsed_file is false order by author_date', (file_id, ))
        file_vesions_result = cursor.fetchall()

        for file_versions_line in file_vesions_result:
            file_versions_id =  file_versions_line[0]
            commit_hash = file_versions_line[1]
            version_path = file_versions_line[2]
            file_extension = version_path.split('.')[-1]
                                                             
            local_file_copy  =  file_versions_directory  +"/"+ str(file_id) + "_" + str(file_versions_id) + "_" + commit_hash +"."+  file_extension
            parsed_file_output =  parsed_files_directory +"/"+ str(file_id) + "_" + str(file_versions_id) + "_" + commit_hash +"."+  file_extension
            subprocess.call(["srcml", local_file_copy, "-o", parsed_file_output])
            
            cursor.execute("update file_versions set has_parsed_file = true where id = %s", (file_versions_id, ))
            connection.commit()
    connection.close()


def extract_comments(repository_id, repository_name):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()

    cursor.execute("select id from files where repository_id = %s ", (repository_id, ))
    files_results = cursor.fetchall()

    for file_line in files_results:
        file_id = file_line[0]
        parsed_files_directory = DiretoryConfig.get_parameter('parsed_files_directory') + repository_name
        cursor.execute('select id, commit_hash, version_path from file_versions where file_id = %s and has_parsed_file is true order by author_date', (file_id, ))
        file_vesions_result = cursor.fetchall()

        for file_versions_line in file_vesions_result:
            
            class_declaration_lines = []
            has_class_declaration = False
            has_interface_declaration = False
            has_enum_declaration = False
            has_annotation_declaration = False

            file_versions_id =  file_versions_line[0]
            commit_hash = file_versions_line[1]
            version_path = file_versions_line[2]
            file_extension = version_path.split('.')[-1]
                                                             
            parsed_file_output =  parsed_files_directory +"/"+ str(file_id) + "_" + str(file_versions_id) + "_" + commit_hash +"."+  file_extension
            print(parsed_file_output)
            try:
                tree = etree.parse(parsed_file_output)
                root = tree.getroot()
            except Exception as e:
                print(e)
            
            for element in root.iter("{http://www.srcML.org/srcML/src}class"):
                class_declaration_line = element.sourceline -1
                class_declaration_lines.append(str(class_declaration_line))
                has_class_declaration = True

            for element in root.iter("{http://www.srcML.org/srcML/src}interface"):
                class_declaration_line = element.sourceline -1
                class_declaration_lines.append(str(class_declaration_line))
                has_interface_declaration = True

            for element in root.iter("{http://www.srcML.org/srcML/src}enum"):
                class_declaration_line = element.sourceline -1
                class_declaration_lines.append(str(class_declaration_line))
                has_enum_declaration = True

            for element in root.iter("{http://www.srcML.org/srcML/src}annotation_defn"):
                class_declaration_line = element.sourceline -1
                class_declaration_lines.append(str(class_declaration_line))
                has_annotation_declaration = True


            for element in root.iter("{http://www.srcML.org/srcML/src}comment"):
                start_line = element.sourceline -1
                comment_text = element.text
                comment_type = element.get("type")
                comment_format = element.get("format")
                
                if comment_type == 'line':
                    end_line = start_line
                else:
                    next_element = element.getnext()
                    if next_element is not None:
                        end_line = next_element.sourceline -2
                    else:
                        end_line = start_line

                cursor.execute("insert into raw_comments (repository_id,file_id, file_versions_id, commit_hash, comment_text, comment_type, comment_format, start_line, end_line, has_class_declaration, has_interface_declaration, has_enum_declaration, has_annotation_declaration, class_declaration_lines) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (repository_id, file_id, file_versions_id, commit_hash, comment_text, comment_type, comment_format, start_line, end_line, has_class_declaration, has_interface_declaration, has_enum_declaration, has_annotation_declaration, ','.join(class_declaration_lines))) 
                connection.commit()

    connection.close()
          
repository_list = fetch_repositories([('camel'), ('tomcat')])
for repository_entry in repository_list:
    repository_id   = repository_entry[0]
    repository_name = repository_entry[1]
    master_branch   = repository_entry[2]
    repository_url  = repository_entry[3]
    repository_cloned_date = repository_entry[4]

    parse_files_using_srcml(repository_id, repository_name)
    extract_comments(repository_id, repository_name)