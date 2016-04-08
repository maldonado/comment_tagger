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

    cursor.execute("select classification, treated_comment_text from manually_classified_comments where classification in %s", [tuple(classification_types),])
    write_formated_file(training_dataset_path, cursor.fetchall())

def delete_training_dataset():
    default_nlp_path = DiretoryConfig.get_parameter('nlp_directory')
    training_dataset_path = default_nlp_path + NLPHandlerConfig.get_parameter('training_dataset_name')
    subprocess.call("rm " + training_dataset_path , shell=True)

def classify_comments(repository_id):

    default_nlp_path = DiretoryConfig.get_parameter('nlp_directory')
    test_dataset_path = default_nlp_path + NLPHandlerConfig.get_parameter('test_dataset_name')

    connection = PSQLConnection.get_connection()
    cursor = connection.cursor() 
    cursor.execute("select distinct(file_versions_id) from processed_comments where repository_id = %s", (repository_id, ))
    file_versions = cursor.fetchall()
    
    for file_version in file_versions:
        before = timeit.default_timer()
        file_versions_id = file_version[0]
        print("file version:", file_versions_id)
        
        cursor.execute("select 'WITHOUT_CLASSIFICATION' as classification, treated_comment_text, id from processed_comments where file_versions_id = %s and td_classification is null order by end_line", (file_versions_id, ))
        all_comments_from_file = cursor.fetchall()
        write_formated_file(test_dataset_path , all_comments_from_file)

        nlp_classifier_memory_use = NLPHandlerConfig.get_parameter('nlp_classifier_memory_use')
        command = 'java ' + nlp_classifier_memory_use + ' -jar stanford-classifier.jar -prop ./dataset.prop -1.useSplitWords -1.splitWordsRegexp "\s"' 
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=default_nlp_path).communicate()
        subprocess.call("rm " + test_dataset_path , shell=True)

        output  = process[0].strip().decode("utf-8").split('\n')
        # results = process[1].strip().decode("utf-8").split('\n')

        output_regex = NLPHandlerConfig.get_parameter('output_regex')
        comment_text_exact_regex = NLPHandlerConfig.get_parameter('comment_text_exact_regex')

        for comment in all_comments_from_file:
            treated_comment_text = comment[1]
            comment_id = comment[2]

            for line in output:
                comment_text_exact_matcher = re.match(comment_text_exact_regex, line)
                comment_text_from_output = comment_text_exact_matcher.group(1)

                if treated_comment_text == comment_text_from_output :
                    output_without_comment = line.replace(treated_comment_text, '')
                    output_matcher = re.findall(output_regex, line)

                    if output_matcher is not None:
                        golden_anwser = output_matcher[0].replace('\'', '')
                        nlp_tool_classification = output_matcher[1].replace('\'', '')

                        cursor.execute("update processed_comments set td_classification = %s where id = %s " , (nlp_tool_classification, comment_id) )
                        connection.commit()
                        # print (golden_anwser , "-" , nlp_tool_classification)
                        break

        after = timeit.default_timer()
        print (after - before)


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