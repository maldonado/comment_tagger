import os
import subprocess

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
        cursor.execute('select id, commit_hash, version_path from file_versions where file_id = %s and has_parsed_file is true order by author_date limit 1', (file_id, ))
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
                func_specifier = []
                func_return_type = ''
                func_name = ''
                func_parameter_list = []
                comment_location = ''

                if comment_type == 'line':
                    end_line = start_line
                else:
                    next_element = element.getnext()
                    if next_element is not None:
                        end_line = next_element.sourceline -2
                    else:
                        end_line = start_line

                next_element = element.getnext()
                if next_element is not None and "function" in next_element.tag:
                
                    comment_location = "FUNCTION"

                    children = next_element.iterchildren("{http://www.srcML.org/srcML/src}specifier", "{http://www.srcML.org/srcML/src}type", "{http://www.srcML.org/srcML/src}name", "{http://www.srcML.org/srcML/src}parameter_list")
                    for child in children:
                        if "specifier" in child.tag:
                            func_specifier.append(child.text)

                        if "type" in child.tag:
                            descentants = child.iterdescendants("{http://www.srcML.org/srcML/src}name")
                            for descentant in descentants:
                                func_return_type =  descentant.text

                        if "name" in child.tag:
                            func_name = child.text

                        if "parameter_list" in child.tag:
                            parameters = child.iterchildren()
                            for paramenter in parameters:
                                descentants = paramenter.iterdescendants() 
                                for descentant in descentants:
                                    if descentant.text is not None:                        
                                        func_parameter_list.append(descentant.text)
                                func_parameter_list.append(',')
                                
                                
                else:
                    ancestors = element.iterancestors()
                    for ancestor in ancestors:
                        if "function" in ancestor.tag:
                            comment_location = "FUNCTION"

                            children = ancestor.iterchildren("{http://www.srcML.org/srcML/src}specifier", "{http://www.srcML.org/srcML/src}type", "{http://www.srcML.org/srcML/src}name", "{http://www.srcML.org/srcML/src}parameter_list")
                            for child in children:
                                if "specifier" in child.tag:
                                    func_specifier.append(child.text)

                                if "type" in child.tag:
                                    descentants = child.iterdescendants("{http://www.srcML.org/srcML/src}name")
                                    for descentant in descentants:
                                        func_return_type =  descentant.text

                                if "name" in child.tag:
                                    func_name = child.text

                                if "parameter_list" in child.tag:
                                    parameters = child.iterchildren()
                                    for paramenter in parameters:
                                        descentants = paramenter.iterdescendants() 
                                        for descentant in descentants:
                                            if descentant.text is not None:                        
                                                func_parameter_list.append(descentant.text)
                                        func_parameter_list.append(',')

                
                # print (start_line)
                # print (comment_text)
                # print (comment_type)
                # print (comment_format)
                # print (func_specifier)
                # print (func_return_type)
                # print (func_name)
                # print (func_parameter_list)
                # print (comment_location)
                # print("-----")

                # cursor.execute("insert into raw_comments (repository_id, file_id, file_versions_id, commit_hash, comment_text, comment_type, comment_format, start_line, end_line, comment_location, func_specifier, func_return_type, func_name, func_parameter_list, has_class_declaration, has_interface_declaration, has_enum_declaration, has_annotation_declaration, class_declaration_lines) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (repository_id, file_id, file_versions_id, commit_hash, comment_text, comment_type, comment_format, start_line, end_line, comment_location, ' '.join(func_specifier), func_return_type, func_name, ' '.join(func_parameter_list)[:-1].replace(' , ', ', '), has_class_declaration, has_interface_declaration, has_enum_declaration, has_annotation_declaration, ','.join(class_declaration_lines))) 
                # connection.commit()

                print ("comment_location:", comment_location)
                print ("func_specifier:", ' '.join(func_specifier))
                print ("func_return_type:", func_return_type)
                print ("func_name:", func_name)
                print ("func_parameter_list:", func_parameter_list)
                # print ("func_parameter_list:", ' '.join(func_parameter_list)[:-1].replace(' , ', ', '))
                print ("repository_id:", repository_id)
                print ("file_id:", file_id )
                print ("file_versions_id:", file_versions_id)
                print ("-------")

                # cursor.execute("update raw_comments set comment_location=%s, func_specifier=%s, func_return_type=%s, func_name=%s, func_parameter_list=%s where repository_id=%s and file_id=%s and file_versions_id=%s", (comment_location, ' '.join(func_specifier), func_return_type, func_name, ' '.join(func_parameter_list)[:-1].replace(' , ', ', '), repository_id, file_id, file_versions_id))                        
                connection.commit()
    connection.close()            
          
def test():

    class_declaration_lines = []
    has_class_declaration = False
    has_interface_declaration = False
    has_enum_declaration = False
    has_annotation_declaration = False
                                                     
    # parsed_file_output =  "/Users/evermal/Dropbox/5200_92913_694d5c7c069a468d2e57ef5729201e1b3faaf503.java"
    parsed_file_output =  "../parsed_files/jmeter/5192_77232_bbe252af7601cbbd7d7a3466b43cde992fe68659.java"
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
        func_specifier = []
        func_return_type = ''
        func_name = ''
        func_parameter_list = []
        comment_location = ''

        if comment_type == 'line':
            end_line = start_line
        else:
            next_element = element.getnext()
            if next_element is not None:
                end_line = next_element.sourceline -2
            else:
                end_line = start_line

        next_element = element.getnext()
        if next_element is not None and "function" in next_element.tag:
        
            comment_location = "FUNCTION"

            children = next_element.iterchildren("{http://www.srcML.org/srcML/src}specifier", "{http://www.srcML.org/srcML/src}type", "{http://www.srcML.org/srcML/src}name", "{http://www.srcML.org/srcML/src}parameter_list")
            for child in children:
                if "specifier" in child.tag:
                    func_specifier.append(child.text)

                if "type" in child.tag:
                    descentants = child.iterdescendants("{http://www.srcML.org/srcML/src}name")
                    for descentant in descentants:
                        func_return_type =  descentant.text

                if "name" in child.tag:
                    func_name = child.text

                if "parameter_list" in child.tag:
                    parameters = child.iterchildren()
                    for paramenter in parameters:
                        descentants = paramenter.iterdescendants("{http://www.srcML.org/srcML/src}name")
                        for descentant in descentants:                        
                            func_parameter_list.append(descentant.text)
                        func_parameter_list.append(',')
                                                
        else:
            ancestors = element.iterancestors()
            for ancestor in ancestors:
                if "function" in ancestor.tag:
                    comment_location = "FUNCTION"
                    # func_specifier = 'protected'

                    children = ancestor.iterchildren("{http://www.srcML.org/srcML/src}specifier", "{http://www.srcML.org/srcML/src}type", "{http://www.srcML.org/srcML/src}name", "{http://www.srcML.org/srcML/src}parameter_list")
                    for child in children:
                        if "specifier" in child.tag:
                            func_specifier.append(child.text)

                        if "type" in child.tag:
                            descentants = child.iterdescendants("{http://www.srcML.org/srcML/src}name")
                            for descentant in descentants:
                                func_return_type =  descentant.text

                        if "name" in child.tag:
                            func_name = child.text

                        if "parameter_list" in child.tag:
                            parameters = child.iterchildren()
                            for paramenter in parameters:
                                descentants = paramenter.iterdescendants() #"{http://www.srcML.org/srcML/src}name"
                                for descentant in descentants:
                                    if descentant.text is not None:                        
                                        func_parameter_list.append(descentant.text)
                                func_parameter_list.append(',')
            
            print ("comment_location:", comment_location)
            print ("func_specifier:", ' '.join(func_specifier))
            print ("func_return_type:", func_return_type)
            print ("func_name:", func_name)
            # print ("func_parameter_list:", func_parameter_list)

            print ("func_parameter_list:", ' '.join(func_parameter_list)[:-1].replace(' , ', ', '))
            # print ("repository_id:", repository_id)
            # print ("file_id:", file_id )
            # print ("file_versions_id:", file_versions_id)

            print ("-------")

        # cursor.execute("insert into raw_comments (repository_id, file_id, file_versions_id, commit_hash, comment_text, comment_type, comment_format, start_line, end_line, comment_location, func_specifier, func_return_type, func_name, func_parameter_list, has_class_declaration, has_interface_declaration, has_enum_declaration, has_annotation_declaration, class_declaration_lines) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (repository_id, file_id, file_versions_id, commit_hash, comment_text, comment_type, comment_format, start_line, end_line, comment_location, ' '.join(func_specifier), func_return_type, func_name, ' '.join(parameter_list)[:-1].replace(' , ', ', '), has_class_declaration, has_interface_declaration, has_enum_declaration, has_annotation_declaration, ','.join(class_declaration_lines))) 
        # connection.commit()

        # cursor.execute("update raw_comments set comment_location=%s, func_specifier=%s, func_return_type=%s, func_name=%s, func_parameter_list=%s where repository_id=%s and file_id=%s and file_versions_id=%s", (comment_location, ' '.join(func_specifier), func_return_type, func_name, ' '.join(parameter_list)[:-1].replace(' , ', ', '), repository_id, file_id, file_versions_id))                        
        # connection.commit()

repository_list = fetch_repositories([('ant')])
for repository_entry in repository_list:
    repository_id   = repository_entry[0]
    repository_name = repository_entry[1]
    master_branch   = repository_entry[2]
    repository_url  = repository_entry[3]
    repository_cloned_date = repository_entry[4]

    # parse_files_using_srcml(repository_id, repository_name)
    # extract_comments(repository_id, repository_name)
    # test()