import re
import timeit

from configkeys import HeuristicHandlerConfig
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

def remove_javadoc_comments(repository_id):
    print("remove javadoc comments")

    before = timeit.default_timer()
    exception_words_to_remove_javadoc_comments_regex = HeuristicHandlerConfig.get_parameter('exception_words_to_remove_javadoc_comments_regex')
    comments_to_keep = []

    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()

    cursor.execute("select id, comment_text, comment_type, comment_format from raw_comments where repository_id = %s", (repository_id, ))
    raw_comment_results = cursor.fetchall()

    for raw_comment_line in raw_comment_results:
        raw_comment_id = raw_comment_line[0]
        comment_text = raw_comment_line[1]
        comment_type = raw_comment_line[2]
        comment_format = raw_comment_line[3]

        if comment_format is not None and comment_format == 'javadoc':
            exception_words_to_remove_javadoc_comments_matcher = re.search(exception_words_to_remove_javadoc_comments_regex, comment_text)
            if exception_words_to_remove_javadoc_comments_matcher is not None:
                comments_to_keep.append(raw_comment_id)
        else:
            comments_to_keep.append(raw_comment_id)

    connection.close()

    after = timeit.default_timer()
    print(len(comments_to_keep))
    print ("heuristic total time:", (after - before)/60)
    return comments_to_keep

def remove_license_comments(comments_to_keep):
    print("remove license comments")
    before = timeit.default_timer()
    exception_words_to_remove_license_comments_regex = HeuristicHandlerConfig.get_parameter('exception_words_to_remove_license_comments_regex')
    
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("select id, comment_text, end_line, class_declaration_lines from raw_comments where id in %s and class_declaration_lines != '' ", [tuple(comments_to_keep),])
    raw_comment_results = cursor.fetchall()
    connection.close()
    
    for raw_comment_line in raw_comment_results:
        raw_comment_id = raw_comment_line[0]
        comment_text = raw_comment_line[1]
        end_line = raw_comment_line[2]
        class_declaration_line = [int(i) for i in raw_comment_line[3].split(',')][0]
        
        if end_line < class_declaration_line :
            exception_words_to_remove_license_comments_matcher = re.search(exception_words_to_remove_license_comments_regex, comment_text)
            if exception_words_to_remove_license_comments_matcher is None:
                comments_to_keep.remove(raw_comment_id)

    after = timeit.default_timer()
    print ("heuristic total time:", (after - before)/60)
    return comments_to_keep

def remove_commented_source_code(comments_to_keep):
    print ("remove commented source code")
    before = timeit.default_timer()
    commented_source_code_regex = HeuristicHandlerConfig.get_parameter('commented_source_code_regex')
    
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("select id, comment_text from raw_comments where id in %s", [tuple(comments_to_keep),])
    raw_comment_results = cursor.fetchall()
    connection.close()
    
    for raw_comment_line in raw_comment_results:
        raw_comment_id = raw_comment_line[0]
        comment_text = raw_comment_line[1]
        
        commented_source_code_matcher = re.search(commented_source_code_regex, comment_text)
        if commented_source_code_matcher is not None:
            comments_to_keep.remove(raw_comment_id)

    after = timeit.default_timer()
    print ("heuristic total time:", (after - before)/60)
    return comments_to_keep

def insert_processed_comments(comments_to_keep):
    print ("insert processed comments")
    before = timeit.default_timer()
    
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor() 
    cursor.execute("insert into processed_comments(id, repository_id,  file_id, file_versions_id, commit_hash, comment_text, comment_type, comment_format, start_line, end_line, comment_location,func_specifier,func_return_type,func_name,func_parameter_list,func_line, has_class_declaration, has_interface_declaration, has_enum_declaration, has_annotation_declaration, class_declaration_lines) select id, repository_id,  file_id, file_versions_id, commit_hash, comment_text, comment_type, comment_format, start_line, end_line, comment_location,func_specifier,func_return_type,func_name,func_parameter_list,func_line, has_class_declaration, has_interface_declaration, has_enum_declaration, has_annotation_declaration, class_declaration_lines from raw_comments where id in %s", [tuple(comments_to_keep),])
    connection.commit()
    connection.close()

    after = timeit.default_timer()
    print ("heuristic total time:", (after - before)/60)

def merge_line_comments(repository_id):
    print("merge line comments")
    before = timeit.default_timer()

    connection = PSQLConnection.get_connection()
    cursor = connection.cursor() 
    cursor.execute("select distinct(file_versions_id) from processed_comments where repository_id = %s ", (repository_id, ))
    file_versions = cursor.fetchall()
    
    for file_version in file_versions:
        file_versions_id = file_version[0]
        # print("file version:", file_versions_id)
        
        cursor.execute("select id, comment_text,  end_line from processed_comments where file_versions_id = %s and comment_type = 'line' order by end_line", (file_versions_id, ))
        sorted_comments = cursor.fetchall()

        iterator = iter(sorted_comments)
        comment = next(iterator, None)        
        while comment is not None:  
            # print(comment[2])

            next_comment = next(iterator, None)
            if next_comment is None:
                break
            # print(next_comment[2])

            comment_id = comment[0]
            comment_message = comment[1]

            while comment[2] - next_comment[2] == -1:
                comment_message = comment_message + " " + next_comment[1]
                new_end_line = next_comment[2] 
                # print ("new end line:", new_end_line)
                # print ("new commit message:", comment_message)
                cursor.execute("update processed_comments set end_line = %s, comment_text= %s, comment_format = 'multiline' where id = %s", (new_end_line, comment_message, comment_id))
                cursor.execute("delete from processed_comments where id = %s" , (next_comment[0], ))
                connection.commit()

                comment = next_comment
                next_comment = next(iterator, None)
                if next_comment is None:
                    break
            else:
                comment = next_comment

    after = timeit.default_timer()
    print ("heuristc total time:", (after - before)/60)

def treat_comment_text(repository_id):
    print ("text treatment to comments")
    before = timeit.default_timer()

    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("select comment_text, id from processed_comments where treated_comment_text is null and repository_id = %s", (repository_id, ))
    processed_comment_list = cursor.fetchall()
    
    formatted_comment_list = []
    formatted_comment_id_list = []
    
    for processed_comment in processed_comment_list:
        formatted_comment = " ".join(processed_comment[0].lower().replace('\n','').replace('\r\n', '').replace('\r', '').replace('\t', '').replace('//','').replace('/**','').replace('*/','').replace('/*','').replace('*','').replace(',','').replace(':','').replace('...','').replace(';','').split())
        formatted_comment_list.append(formatted_comment)
        formatted_comment_id_list.append(processed_comment[1])
    
    total_comments = len(formatted_comment_id_list)

    for x in range(0, total_comments):
        cursor.execute("update processed_comments set treated_comment_text = %s where id = %s", (formatted_comment_list[x], formatted_comment_id_list[x]))
        connection.commit()
    
    connection.close()
    after = timeit.default_timer()
    print ("heuristc total time:", (after - before)/60)


repository_list = fetch_repositories([('camel')])
for repository_entry in repository_list:
    repository_id   = repository_entry[0]
    repository_name = repository_entry[1]
    master_branch   = repository_entry[2]
    repository_url  = repository_entry[3]
    repository_cloned_date = repository_entry[4]

    comments_to_keep = remove_javadoc_comments(repository_id)
    comments_to_keep = remove_license_comments(comments_to_keep)
    comments_to_keep = remove_commented_source_code(comments_to_keep)
    insert_processed_comments(comments_to_keep)
    merge_line_comments(repository_id)
    treat_comment_text(repository_id)