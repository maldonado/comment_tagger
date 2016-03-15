import psycopg2

##### CONFIGURATIONS 
connection = None
connection = psycopg2.connect(host='localhost', port='5432', database='comment_classification', user='evermal', password='')
cursor = connection.cursor()

# SELECT id,  EXTRACT(EPOCH FROM INTERVAL processed_comments.interval_time_to_remove) 
cursor.execute("select id , interval_time_to_remove from processed_comments where has_removed_version is true")
results = cursor.fetchall()

total_files_to_process = len(results)
progress_counter = 0

for result in results:
    progress_counter = progress_counter + 1

    processed_comment_id      = result[0]
    interval_time_to_remove   = result[1]
    
    cursor.execute("update processed_comments set epoch_time_to_remove = extract (epoch from interval '"+interval_time_to_remove+"') where id = %s", (processed_comment_id, ))
    connection.commit()
    
    print (progress_counter ,' out of :', total_files_to_process)