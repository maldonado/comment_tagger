import re
import timeit
import subprocess

from configkeys import NLPHandlerConfig, DiretoryConfig
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

def write_formated_file(file_name, result):
    with open (file_name,'a') as classified_seq:
        for line in result:
            classified_seq.write("{0}\t{1}\n".format(line[0], line[1]))
        classified_seq.close()

def generate_training_dataset():
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()

    default_nlp_path = DiretoryConfig.get_parameter('nlp_directory')

    training_dataset_path = default_nlp_path + NLPHandlerConfig.get_parameter('training_dataset_name')
    classification_types  = NLPHandlerConfig.get_parameter('classification_types')
    training_projects     = NLPHandlerConfig.get_parameter('training_projects') 

    cursor.execute("select classification, treated_comment_text from manually_classified_comments where classification in %s and project_origin in %s", [tuple(classification_types), tuple(training_projects)])
    write_formated_file(training_dataset_path, cursor.fetchall())

def delete_training_dataset():
    default_nlp_path = DiretoryConfig.get_parameter('nlp_directory')
    training_dataset_path = default_nlp_path + NLPHandlerConfig.get_parameter('training_dataset_name')
    subprocess.call("rm " + training_dataset_path , shell=True)

def pre_process_comments(repository_id):
    connection = PSQLConnection.get_connection()
    cursor = connection.cursor()
    cursor.execute("update processed_comments set td_classification = 'WITHOUT_CLASSIFICATION' where treated_comment_text = '' and td_classification is null and repository_id = %s", (repository_id, ))
    connection.commit()
    connection.close()

def classify_comments(repository_id):
    default_nlp_path = DiretoryConfig.get_parameter('nlp_directory')
    test_dataset_path = default_nlp_path + NLPHandlerConfig.get_parameter('test_dataset_name')

    connection = PSQLConnection.get_connection()
    cursor = connection.cursor() 
    cursor.execute("select 'WITHOUT_CLASSIFICATION' as classification, distinct(treated_comment_text) from processed_comments where repository_id = %s and td_classification is null group by 2", (repository_id, ))
    all_comments_from_repository = cursor.fetchall()
    
    write_formated_file(test_dataset_path , all_comments_from_repository)

    nlp_classifier_memory_use = NLPHandlerConfig.get_parameter('nlp_classifier_memory_use')
    command = 'java ' + nlp_classifier_memory_use + ' -jar stanford-classifier.jar -prop ./dataset.prop -1.useSplitWords -1.splitWordsRegexp "\s"' 
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=default_nlp_path).communicate()

    output  = process[0].strip().decode("utf-8").split('\n')
    results = process[1].strip().decode("utf-8").split('\n')

    output_regex = NLPHandlerConfig.get_parameter('output_regex')
    comment_text_exact_regex = NLPHandlerConfig.get_parameter('comment_text_exact_regex')

    # print(output)
    # print(results)

    match_counter = 0
    for comment in all_comments_from_repository:
        before = timeit.default_timer()
        treated_comment_text = comment[1]


        for line in output:
            comment_text_exact_matcher = re.match(comment_text_exact_regex, line)
            comment_text_from_output = comment_text_exact_matcher.group(1)

            if treated_comment_text == comment_text_from_output :
                output_without_comment = line.replace(treated_comment_text, '')
                output_matcher = re.findall(output_regex, line)

                if output_matcher is not None:
                    golden_anwser = output_matcher[0].replace('\'', '')
                    nlp_tool_classification = output_matcher[1].replace('\'', '')
                    match_counter = match_counter + 1

                    cursor.execute("update processed_comments set td_classification = %s where treated_comment_text = %s and repository_id = %s" , (nlp_tool_classification, treated_comment_text, repository_id))
                    connection.commit()
                    after = timeit.default_timer()
                    # print (after - before)
                    break
 
    subprocess.call("rm " + test_dataset_path , shell=True)
    print(match_counter)


repository_list = fetch_repositories()
for repository_entry in repository_list:
    repository_id   = repository_entry[0]
    repository_name = repository_entry[1]
    master_branch   = repository_entry[2]
    repository_url  = repository_entry[3]
    repository_cloned_date = repository_entry[4]

    generate_training_dataset()
    classify_comments(repository_id)
    delete_training_dataset()