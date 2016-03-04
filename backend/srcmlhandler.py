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

def parse_files_using_srcml(repository_id, repository_name, master_branch):
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
            local_file_copy  =  file_versions_directory +"/"+ str(file_id) + "_" + commit_hash +"."+  file_extension
            parsed_file_output =  parsed_files_directory +"/"+ str(file_id) + "_" + commit_hash +"."+  file_extension
            subprocess.call(["srcml", local_file_copy, "-o", parsed_file_output])
            
            cursor.execute("update file_versions set has_parsed_file = true where id = %s", (file_versions_id, ))
            connection.commit()
    connection.close()


tree = etree.parse("../parsed_files/abdera/197_729f8785e735fd4a221fe9cf249a97181f265164.java")
root = tree.getroot()

# for child in root :
#     attributes = child.attrib
#     print (child.text)
#     print (child.sourceline)
#     print (attributes)

# for element in root.iter():
#     # print (element.tag)
#     if "comment" in element.tag:
#         start_line = element.sourceline -1
#         end_line = element.getnext().sourceline -2
#         comment_text = element.text
#         comment_type = element.get("type")
#         comment_format = element.get("format")

#         # print (comment_text)
#         # print (comment_type)
#         # print (comment_format)
#         # print (start_line)
#         # print (end_line)

#         next_element = element.getnext()
#         if "function_decl" in next_element.tag:
#             comment_location = "METHOD"
#             # print(etree.tostring(next_element))
#             for child in next_element:
#                 if "parameter_list" in child.tag:
#                     for child_sub_element in child:
#                         # if "parameter" in child_sub_element.tag and len(child_sub_element) > :
#                         #     parameter_type = child_sub_element[0].text
#                         #     parameter_name = child_sub_element[0].text
#                         #     print(parameter_type, parameter_name)
#                         if "parameter" in child_sub_element.tag :
#                             print (etree.tostring(child_sub_element, pretty_print=True))






for element in root.iter("{http://www.srcML.org/srcML/src}comment"):
    print (element, element.sourceline)
    # start_line = element.sourceline -1
    # end_line = element.getnext().sourceline -2
    # comment_text = element.text
    # comment_type = element.get("type")
    # comment_format = element.get("format")

    # print (comment_text)
    # print (comment_type)
    # print (comment_format)
    # print (start_line)
    # print (end_line)

    next_element = element.getnext()
    for child in next_element.iter("{http://www.srcML.org/srcML/src}function_decl"):
        print (child.tag, child.sourceline)
        names = child.find("{http://www.srcML.org/srcML/src}name")
        

        

        
        # sub_elements = list(child)

        # print (sub_elements)

    # next_element 

    
    #     if "function_decl" in next_element.tag:
    #         comment_location = "METHOD"
    #         # print(etree.tostring(next_element))
    #         for child in next_element:
    #             if "parameter_list" in child.tag:
    #                 for child_sub_element in child:
    #                     # if "parameter" in child_sub_element.tag and len(child_sub_element) > :
    #                     #     parameter_type = child_sub_element[0].text
    #                     #     parameter_name = child_sub_element[0].text
    #                     #     print(parameter_type, parameter_name)
    #                     if "parameter" in child_sub_element.tag :
    #                         print (etree.tostring(child_sub_element, pretty_print=True))
                    
            

                

        
        





    # # get class declaration line   
    # if "class" in element.tag :
    #     # print (element.tag)
    #     class_declaration_line = element.sourceline -1
    #     print (class_declaration_line)

    # if "interface" in element.tag :
    #     class_declaration_line = element.sourceline -1
    #     is_interface = True
    #     print (class_declaration_line)

    # if "enum" in element.tag:
    #     is_enum = True
    #     class_declaration_line = element.sourceline -1
    #     print (class_declaration_line)



    # print("%s - %s - %s" % (element.tag, element.text , element.attrib))


# children = list(root)
# print (children)

                
# attributes = root.attrib
# print (attributes)

# repository_list = fetch_repositories()

# for repository_entry in repository_list:
#     repository_id   = repository_entry[0]
#     repository_name = repository_entry[1]
#     master_branch   = repository_entry[2]
#     repository_url  = repository_entry[3]
#     repository_cloned_date = repository_entry[4]

#     parse_files_using_srcml(repository_id, repository_name, master_branch)