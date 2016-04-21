import psycopg2

##### CONFIGURATIONS 

repository_id = 5

comment_classification_connection = psycopg2.connect(host='localhost', port='5432', database='comment_classification', user='evermal', password='')
cursor_cc = comment_classification_connection.cursor()

td_removal_connection = psycopg2.connect(host='localhost', port='5432', database='td_removal', user='evermal', password='')
cursor_removal = td_removal_connection.cursor()

cursor_removal.execute("select file_id, file_versions_id, commit_hash, start_line, end_line, comment_location, func_specifier, func_return_type, func_name, func_parameter_list, func_line from processed_comments where repository_id = %s and func_name is not null", (repository_id, ))
results = cursor_removal.fetchall()

total_files_to_process = len(results)
progress_counter = 0


for result in results:
    progress_counter = progress_counter + 1

    file_id = result[0]
    file_versions_id = result[1]
    commit_hash = result[2]
    start_line = result[3]
    end_line = result[4]
    comment_location = result[5]
    func_specifier = result[6]
    func_return_type = result[7]
    func_name = result[8]
    func_parameter_list = result[9]
    func_line = result[10]

    cursor_cc.execute("update processed_comments set comment_location=%s, func_specifier=%s, func_return_type=%s, func_name=%s, func_parameter_list=%s, func_line=%s where file_id=%s and file_versions_id=%s and commit_hash=%s and start_line=%s and end_line=%s ", (comment_location, func_specifier, func_return_type, func_name, func_parameter_list, func_line, file_id, file_versions_id, commit_hash, start_line, end_line))
    comment_classification_connection.commit()
    
    print (progress_counter ,' out of :', total_files_to_process)