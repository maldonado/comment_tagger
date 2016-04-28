import psycopg2

##### CONFIGURATIONS 
connection = None
connection = psycopg2.connect(host='localhost', port='5432', database='comment_classification', user='evermal', password='')
cursor = connection.cursor()


cursor.execute("select b.treated_commenttext, a.version_introduced_commit_hash, a.version_removed_commit_hash, a.last_version_that_comment_was_found_hash , a.file_name from technical_debt_summary a, processed_comment b where a.processed_comment_id = b.id and  a.project_name = 'apache-ant'")
results = cursor.fetchall()

total_files_to_process = len(results)
progress_counter = 0

# right_design_debt_counter = 0
# right_requirement_debt_counter = 0
# agreement_counter = 0
# disagreement_counter = 0
# design_missclassified_as_without_classification = 0
# design_missclassified_as_requirement =0
# requirement_missclassified_as_without_classification =0
# requirement_missclassified_as_design=0

for result in results:
    # progress_counter = progress_counter + 1

    treated_comment_text            = result[0]
    version_introduced_commit_hash  = result[1]
    version_removed_commit_hash     = result[2]
    last_version_that_comment_was_found_hash = result[3]
    file_name = result[4]
    

    # print("treated_comment_text ", treated_comment_text)
    # print("version_introduced_commit_hash ", version_introduced_commit_hash)
    # print("version_removed_commit_hash ", version_removed_commit_hash)
    # print("last_version_that_comment_was_found_hash ", last_version_that_comment_was_found_hash)

    # print (progress_counter)

    


    cursor.execute("select comment_location,func_specifier,func_return_type,func_name,func_parameter_list from processed_comments a, files b where a.file_id = b.id and a.commit_hash = %s and a.repository_id = 2 and b.name = %s and a.treated_comment_text = %s group by 1,2,3,4,5", (version_introduced_commit_hash, file_name, treated_comment_text)) 
    # cursor.execute("select count(distinct(comment_location)) from processed_comments where treated_comment_text = %s and repository_id = 2 ", (treated_comment_text, )) 
    # cursor.execute("select count(distinct(func_specifier,func_return_type,func_name,func_parameter_list)) from processed_comments where treated_comment_text = %s and repository_id = 2 ", (treated_comment_text, )) 
    # print (automatic_classification_result[0])   

    automatic_classification_result = cursor.fetchall()
    print ("-------------", len(automatic_classification_result))
    for processed_comment in automatic_classification_result:
       
        comment_location = processed_comment[0]
        func_specifier = processed_comment[1]
        func_return_type = processed_comment[2]
        func_name = processed_comment[3]
        func_parameter_list = processed_comment[4]
        
    
        if comment_location == 'FUNCTION':
            progress_counter = progress_counter + 1  
            
            print ("comment_location", comment_location)
            print ("func_specifier", func_specifier)
            print ("func_return_type", func_return_type)
            print ("func_name", func_name)
            print ("func_parameter_list", func_parameter_list)
    

    cursor.execute("select a.processed_comment_id")

#     if automatic_classification_result[0] == 1:
#         progress_counter = progress_counter + 1

print (progress_counter)

    
#     if automatic_classification_result is None:
#         print ("error")
#     else:
#         automatic_classification = automatic_classification_result[0]

#         if automatic_classification == manual_classification:
            
#             # print(manual_classification, "," , automatic_classification, ",", treated_comment_text)

#             agreement_counter = agreement_counter + 1
#             if manual_classification == "DESIGN": 
#                 right_design_debt_counter =  right_design_debt_counter + 1
#             else:
#                 right_requirement_debt_counter = right_requirement_debt_counter + 1 
            
#         else:
#             print(manual_classification, "," , automatic_classification, ",", treated_comment_text)
#             disagreement_counter = disagreement_counter + 1

#             if manual_classification == "DESIGN" and automatic_classification == "WITHOUT_CLASSIFICATION":
#                 design_missclassified_as_without_classification = design_missclassified_as_without_classification + 1

#             elif manual_classification == "DESIGN" and automatic_classification == "REQUIREMENT":
#                 design_missclassified_as_requirement = design_missclassified_as_requirement + 1

#             elif manual_classification == "REQUIREMENT" and automatic_classification == "WITHOUT_CLASSIFICATION":
#                 requirement_missclassified_as_without_classification = requirement_missclassified_as_without_classification + 1
            
#             else:
#                 requirement_missclassified_as_design = requirement_missclassified_as_design + 1
            
#         # print (progress_counter ,' out of :', total_files_to_process)

# print ("total TD comments with same classification (tool vs manual): ", agreement_counter, " of :", total_files_to_process)
# print ("design agreement: ", right_design_debt_counter, "requirement agreement: ", right_requirement_debt_counter)

# print ("total TD comments with different classification (tool vs manual): ", disagreement_counter )
# print ("design classified as without classification: ", design_missclassified_as_without_classification, "design classified as requirement: " , design_missclassified_as_requirement)
# print ("requirement classified as without classification: ", requirement_missclassified_as_without_classification, "requirement classified as design: " , requirement_missclassified_as_design)