
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
    

def populate_survival_plots(repository_name, repository_id):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("select id , %s as project_name, has_removed_version, epoch_time_to_remove, epoch_time_in_the_system from processed_comments where repository_id = %s and is_introduced_version = true", (repository_name, repository_id))
    results = cursor.fetchall()

    total_files_to_process = len(results)
    progress_counter = 0

    for result in results:
        progress_counter = progress_counter + 1

        processed_comment_id      = result[0]
        project_name              = result[1]
        was_td_removed            = result[2]
        epoch_time_to_remove      = result[3]
        epoch_time_in_the_system  = result[4]
        
        if was_td_removed:            
            cursor.execute("insert into survival_plot (processed_comment_id, project_name, was_td_removed, epoch_interval) values (%s,%s,%s,%s)", (processed_comment_id, project_name, '1', epoch_time_to_remove))

        else:
            cursor.execute("insert into survival_plot (processed_comment_id, project_name, was_td_removed, epoch_interval) values (%s,%s,%s,%s)", (processed_comment_id, project_name, '0', epoch_time_in_the_system))

        connection.commit()
        print(progress_counter, ' out of :', total_files_to_process) 

repository_list = fetch_repositories([('jmeter')])
for repository_entry in repository_list:
    repository_id   = repository_entry[0]
    repository_name = repository_entry[1]
    master_branch   = repository_entry[2]
    repository_url  = repository_entry[3]
    repository_cloned_date = repository_entry[4]

    populate_survival_plots(repository_name, repository_id)