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
    before = timeit.default_timer()
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor() 
    cursor.execute("select file_id, treated_comment_text from processed_comments where repository_id = %s and td_classification != 'WITHOUT_CLASSIFICATION' group by 1,2 order by 1   ", (repository_id, ))
    files = cursor.fetchall()
    
    for file in files:        
        file_id = file[0]
        treated_comment_text = file[1]
        print("file id:", file_id)
        print("treated_comment_text:", treated_comment_text)        

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
    
            cursor.execute("update processed_comments set introduced_version_commit_hash = %s, is_introduced_version = %s, introduced_version_author = %s, introduced_version_date = %s where id = %s", (introduced_version_commit_hash, is_introduced_version, author_name, author_date, processed_comment_id))
            connection.commit()
 
            if iteration_counter == len(all_file_versions):
                cursor.execute ("select id, commit_hash, author_name, author_date from file_versions where file_id = %s and author_date > %s order by author_date", (file_id, author_date))
                remaining_file_versions = cursor.fetchall()

                if len(remaining_file_versions) > 0:
                    removed_version_commit_hash = remaining_file_versions[0][1]
                    removed_version_author = remaining_file_versions[0][2]
                    removed_version_date = remaining_file_versions[0][3]
                    has_removed_version = True

                    cursor.execute("update processed_comments set removed_version_commit_hash = %s, has_removed_version = %s, removed_version_author = %s, removed_version_date = %s where id = %s", (removed_version_commit_hash, has_removed_version, removed_version_author, removed_version_date, introduced_version_processed_comment_id))
                    connection.commit()
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
                            
                        cursor.execute("update processed_comments set removed_version_commit_hash = %s, has_removed_version = %s, removed_version_author = %s, removed_version_date = to_timestamp(%s, 'Dy Mon DD HH24:MI:SS YYYY +-####') where id = %s", (removed_version_commit_hash, has_removed_version, git_commit_author, git_commit_date, introduced_version_processed_comment_id))
                        connection.commit()

                    else:
                        cursor.execute("update processed_comments set has_removed_version = %s where id = %s", (has_removed_version, introduced_version_processed_comment_id))
                        connection.commit()

repository_list = fetch_repositories()
for repository_entry in repository_list:
    repository_id   = repository_entry[0]
    repository_name = repository_entry[1]
    master_branch   = repository_entry[2]
    repository_url  = repository_entry[3]
    repository_cloned_date = repository_entry[4]
    
    search_authors(repository_id, repository_name)
    # calculate_interval_time_to_removal(repository_id)
    # calculate_epoch_time_to_removal(repository_idq)