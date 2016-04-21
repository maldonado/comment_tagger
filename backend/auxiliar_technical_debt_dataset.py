import math
from configkeys import NLPHandlerConfig, DiretoryConfig
from dbconnector import PSQLConnection

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

    cursor.execute("select classification, count(*) from manually_classified_comments where classification in %s and project_origin in %s group by 1", [tuple(classification_types), tuple(training_projects)])    
    count_results = cursor.fetchall()

    number_of_without_classification_comments = 0
    number_of_design_debt_comments = 0
    number_of_requirement_debt_comments = 0
    number_of_documentation_debt_comments = 0
    number_of_test_debt_comments = 0
    number_of_defect_debt_comments = 0

    for count_result in count_results:
        classification = count_result[0]
        
        if classification == "WITHOUT_CLASSIFICATION":
            number_of_without_classification_comments = count_result[1]
        if classification == "DESIGN":
            number_of_design_debt_comments = count_result[1]
        if classification == "REQUIREMENT":
            number_of_requirement_debt_comments = count_result[1]
        if classification == "DOCUMENTATION":
            number_of_documentation_debt_comments = count_result[1]
        if classification == "TEST":
            number_of_test_debt_comments = count_result[1]
        if classification == "DEFECT":
            number_of_defect_debt_comments = count_result[1]

    all_td_comments = number_of_design_debt_comments + number_of_documentation_debt_comments + number_of_defect_debt_comments + number_of_requirement_debt_comments + number_of_test_debt_comments    
    times_to_select_td = int (number_of_without_classification_comments / all_td_comments)
    


    # resampled upsized 
    # for x in range(1, times_to_select_td):
    #     cursor.execute("select 'TECHNICAL_DEBT' as classification, treated_comment_text from manually_classified_comments where classification != 'WITHOUT_CLASSIFICATION' and project_origin in %s", [tuple(training_projects), ])
    #     write_formated_file(training_dataset_path, cursor.fetchall())

    
    cursor.execute("select 'TECHNICAL_DEBT' as classification, treated_comment_text from manually_classified_comments where classification != 'WITHOUT_CLASSIFICATION' and project_origin in %s", [tuple(training_projects), ])
    write_formated_file(training_dataset_path, cursor.fetchall())

    cursor.execute("select classification, treated_comment_text from manually_classified_comments where classification = 'WITHOUT_CLASSIFICATION' and project_origin in %s", [tuple(training_projects), ])
    write_formated_file(training_dataset_path, cursor.fetchall())

    print(times_to_select_td , " x all tds")
    # print(times_to_select_requirement, " x REQUIREMENT")

generate_training_dataset()