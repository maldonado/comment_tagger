import re
import timeit
import subprocess

from configkeys import DiretoryConfig, TDAuthorsHandlerConfig
from dbconnector import PSQLConnection

# example of expected tuple [('everton'), ('aries')] move elsewhere and extract class 
def fetch_repositories(repo_list = tuple([])):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    if not repo_list:
        cursor.execute("select id, name, master_branch, clone_url, cloned_date from repositories order by 1 ")
    else:
        cursor.execute("select id, name, master_branch, clone_url, cloned_date from repositories where name in %s", [tuple(repo_list),])
    query_return = cursor.fetchall()
    connection.close()
    return query_return

def search_authors(repository_id, repository_name):
    print("searching for authors that introduced and removed technical debt")

    before = timeit.default_timer()
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor() 
    cursor.execute("select file_id, treated_comment_text from processed_comments where repository_id = %s and file_id = 6327  ", (repository_id, ))
    files = cursor.fetchall()
    
    for file in files:        
        file_id = file[0]
        treated_comment_text = file[1]
        
        iteration_counter = 0
        has_removed_version = False
        is_introduced_version = False
        removed_version_commit_hash = ''
        introduced_version_commit_hash = ''
        introduced_version_processed_comment_id = ''

        cursor.execute("select a.id, b.author_date, b.commit_hash, b.author_name from processed_comments a, file_versions b where a.file_versions_id = b.id and a.file_id = %s and a.treated_comment_text = %s order by 1", (file_id, treated_comment_text))
        all_file_versions = cursor.fetchall()

        for file_version_line in all_file_versions:
            iteration_counter = iteration_counter + 1
            processed_comment_id = file_version_line[0]
            author_date = file_version_line[1]
            commit_hash = file_version_line[2]
            author_name = file_version_line[3]

            if introduced_version_commit_hash == '':
                is_introduced_version = True
                introduced_version_commit_hash = commit_hash
                introduced_version_processed_comment_id = processed_comment_id
            else:
                is_introduced_version = False
            
            if is_introduced_version:
                print("--------")
                print("introduced_version_commit_hash",introduced_version_commit_hash)
                print("is_introduced_version",is_introduced_version)
                print("author_name",author_name)
                print("author_date",author_date)
                print("processed_comment_id",processed_comment_id)
                print("--------")
            # cursor.execute("update processed_comments set introduced_version_commit_hash = %s, is_introduced_version = %s, introduced_version_author = %s, introduced_version_date = %s where id = %s", (introduced_version_commit_hash, is_introduced_version, author_name, author_date, processed_comment_id))
            # connection.commit()
 
            if iteration_counter == len(all_file_versions):
                cursor.execute ("select id, commit_hash, author_name, author_date from file_versions where file_id = %s and author_date > %s order by author_date", (file_id, author_date))
                remaining_file_versions = cursor.fetchall()

                if len(remaining_file_versions) > 0:
                    removed_version_commit_hash = remaining_file_versions[0][1]
                    removed_version_author = remaining_file_versions[0][2]
                    removed_version_date = remaining_file_versions[0][3]
                    has_removed_version = True

                    print("--------")
                    print("removed_version_commit_hash",removed_version_commit_hash)
                    print("has_removed_version",has_removed_version)
                    print("removed_version_author",removed_version_author)
                    print("removed_version_date",removed_version_date)
                    print("introduced_version_processed_comment_id",introduced_version_processed_comment_id)
                    print("--------")
                    # cursor.execute("update processed_comments set removed_version_commit_hash = %s, has_removed_version = %s, removed_version_author = %s, removed_version_date = %s where id = %s", (removed_version_commit_hash, has_removed_version, removed_version_author, removed_version_date, introduced_version_processed_comment_id))
                    # connection.commit()
                else:
                    cursor.execute("select deletion_commit_hash from files where id = %s", (file_id,))
                    file_commit_hash_result = cursor.fetchone()

                    if file_commit_hash_result[0] is not None:
                        repository_directory = DiretoryConfig.get_parameter('repository_directory') + repository_name
                        git_log_file_regex = TDAuthorsHandlerConfig.get_parameter('git_log_file_regex')

                        removed_version_commit_hash = file_commit_hash_result[0]
                        has_removed_version = True
                
                        git_log = "git log -1 " + removed_version_commit_hash
                        process = subprocess.Popen(git_log, stdout=subprocess.PIPE, shell=True, cwd= repository_directory)
                        proc_stdout = process.communicate()[0].strip().decode('utf-8').split('\n')
                        
                        for proc_stdout_line in proc_stdout:   
                            git_log_file_matcher =  re.match(git_log_file_regex, proc_stdout_line)    
                            if git_log_file_matcher is not None:
                                if git_log_file_matcher.group(2):
                                    git_commit_author = git_log_file_matcher.group(2)
                                if git_log_file_matcher.group(4):
                                    git_commit_date = git_log_file_matcher.group(4)
                        
                        print("--------")
                        print("removed_version_commit_hash",removed_version_commit_hash)
                        print("has_removed_version",has_removed_version)
                        print("git_commit_author",git_commit_author)
                        print("git_commit_date",git_commit_date, )
                        print("introduced_version_processed_comment_id ",introduced_version_processed_comment_id )
                        print("--------")    
                        # cursor.execute("update processed_comments set removed_version_commit_hash = %s, has_removed_version = %s, removed_version_author = %s, removed_version_date = to_timestamp(%s, 'Dy Mon DD HH24:MI:SS YYYY +-####') where id = %s", (removed_version_commit_hash, has_removed_version, git_commit_author, git_commit_date, introduced_version_processed_comment_id))
                        # connection.commit()

                    else:
                        print("--------")    
                        print("has_removed_version", has_removed_version) 
                        print("introduced_version_processed_comment_id", introduced_version_processed_comment_id)
                        print("--------")    

                        # cursor.execute("update processed_comments set has_removed_version = %s where id = %s", (has_removed_version, introduced_version_processed_comment_id))
                        # connection.commit()

def search_last_commit_found(repository_id):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor() 
    
    cursor.execute("select id, file_id, treated_comment_text from processed_comments where has_removed_version is true and repository_id = %s", (repository_id, ))
    all_removed_comments = cursor.fetchall()

    total_comments = len(all_removed_comments)
    progress_counter = 0

    for removed_comment in all_removed_comments:
        progress_counter = progress_counter + 1
        processed_comment_id = removed_comment[0]
        file_id = removed_comment[1]
        treated_comment_text = removed_comment[2]

        print(treated_comment_text)
        cursor.execute("select distinct on (treated_comment_text) commit_hash, comment_location ,func_specifier ,func_return_type ,func_name ,func_parameter_list , func_line from processed_comments where treated_comment_text= %s and file_id = %s order by treated_comment_text, introduced_version_date desc limit 1 ", (treated_comment_text, file_id))
        result = cursor.fetchone()

        last_found_commit_hash= result[0]
        last_found_comment_location = result[1]
        last_found_func_specifier = result[2]
        last_found_func_return_type = result[3]
        last_found_func_name = result[4]
        last_found_func_parameter_list = result[5]
        last_found_func_line= result[6]

        cursor.execute("insert into aux_last_found_version_before_removal (processed_comment_id, last_found_commit_hash ,last_found_comment_location ,last_found_func_specifier ,last_found_func_return_type ,last_found_func_name ,last_found_func_parameter_list ,last_found_func_line) values (%s,%s,%s,%s,%s,%s,%s,%s)", (processed_comment_id, last_found_commit_hash ,last_found_comment_location ,last_found_func_specifier ,last_found_func_return_type ,last_found_func_name ,last_found_func_parameter_list ,last_found_func_line))
        connection.commit()
        print(progress_counter, " out of: ", total_comments)

    connection.close()
        
def calculate_interval_time_to_removal(repository_id):
    print("calculating interval time to removal")
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("with temp as (select id, age(removed_version_date, introduced_version_date) as interval_time from processed_comments where has_removed_version = true and repository_id = %s) update processed_comments set interval_time_to_remove = t.interval_time from temp t where t.id = processed_comments.id", (repository_id, ))
    connection.commit()
    connection.close()

def calculate_epoch_time_to_removal(repository_id):
    print("calculating epoch time to removal")
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("select id , interval_time_to_remove from processed_comments where has_removed_version is true and repository_id = %s", (repository_id, ))
    results = cursor.fetchall()

    for result in results:
        processed_comment_id      = result[0]
        interval_time_to_remove   = result[1]
        cursor.execute("update processed_comments set epoch_time_to_remove = extract (epoch from interval '"+interval_time_to_remove+"') where id = %s", (processed_comment_id, ))
        connection.commit()

    connection.close()
        
repository_list = fetch_repositories([('jmeter')])
for repository_entry in repository_list:
    repository_id   = repository_entry[0]
    repository_name = repository_entry[1]
    master_branch   = repository_entry[2]
    repository_url  = repository_entry[3]
    repository_cloned_date = repository_entry[4]
    
    print("Processing : ", repository_name)
    search_authors(repository_id, repository_name)
    # search_last_commit_found(repository_id)
    # calculate_interval_time_to_removal(repository_id)
    # calculate_epoch_time_to_removal(repository_id)