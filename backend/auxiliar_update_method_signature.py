import psycopg2

##### CONFIGURATIONS 
connection = None
connection = psycopg2.connect(host='localhost', port='5432', database='comment_classification', user='evermal', password='')
cursor = connection.cursor()


cursor.execute("select b.treated_commenttext, a.version_introduced_commit_hash  from technical_debt_summary a, processed_comment b where a.processed_comment_id = b.id and  a.project_name = 'apache-jmeter' and a.comment_classification in ('DESIGN')")
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
    progress_counter = progress_counter + 1

    treated_comment_text      = result[0]
    summary_td_

    cursor.execute("select  from processed_comments where treated_comment_text = %s and repository_id = 2", (treated_comment_text, ))
    automatic_classification_result = cursor.fetchone()

    
    if automatic_classification_result is None:
        print ("error")
    else:
        automatic_classification = automatic_classification_result[0]

        if automatic_classification == manual_classification:
            
            # print(manual_classification, "," , automatic_classification, ",", treated_comment_text)

            agreement_counter = agreement_counter + 1
            if manual_classification == "DESIGN": 
                right_design_debt_counter =  right_design_debt_counter + 1
            else:
                right_requirement_debt_counter = right_requirement_debt_counter + 1 
            
        else:
            print(manual_classification, "," , automatic_classification, ",", treated_comment_text)
            disagreement_counter = disagreement_counter + 1

            if manual_classification == "DESIGN" and automatic_classification == "WITHOUT_CLASSIFICATION":
                design_missclassified_as_without_classification = design_missclassified_as_without_classification + 1

            elif manual_classification == "DESIGN" and automatic_classification == "REQUIREMENT":
                design_missclassified_as_requirement = design_missclassified_as_requirement + 1

            elif manual_classification == "REQUIREMENT" and automatic_classification == "WITHOUT_CLASSIFICATION":
                requirement_missclassified_as_without_classification = requirement_missclassified_as_without_classification + 1
            
            else:
                requirement_missclassified_as_design = requirement_missclassified_as_design + 1
            
        # print (progress_counter ,' out of :', total_files_to_process)

print ("total TD comments with same classification (tool vs manual): ", agreement_counter, " of :", total_files_to_process)
print ("design agreement: ", right_design_debt_counter, "requirement agreement: ", right_requirement_debt_counter)

print ("total TD comments with different classification (tool vs manual): ", disagreement_counter )
print ("design classified as without classification: ", design_missclassified_as_without_classification, "design classified as requirement: " , design_missclassified_as_requirement)
print ("requirement classified as without classification: ", requirement_missclassified_as_without_classification, "requirement classified as design: " , requirement_missclassified_as_design)