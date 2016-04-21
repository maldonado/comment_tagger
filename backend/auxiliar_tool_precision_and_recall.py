import psycopg2

##### CONFIGURATIONS 
connection = None
connection = psycopg2.connect(host='localhost', port='5432', database='comment_classification', user='evermal', password='')
cursor = connection.cursor()

# apache-ant-1.7.0
# apache-jmeter-2.10

cursor.execute("select a.treated_commenttext,  a.classification from processed_comment a, comment_class b where a.commentclassid = b.id and b.projectname = 'apache-ant-1.7.0' and a.classification in ('DESIGN', 'WITHOUT_CLASSIFICATION')")
results = cursor.fetchall()

total_files_to_process = len(results)

progress_counter = 0
true_positive = 0
true_negative = 0
false_positive = 0
false_negative = 0

for result in results:
    progress_counter = progress_counter + 1

    treated_comment_text      = result[0]
    manual_classification     = result[1]
    
    # if manual_classification == 'DESIGN' or manual_classification == 'DEFECT' or manual_classification == 'DOCUMENTATION' or manual_classification == 'IMPLEMENTATION' or manual_classification == 'TEST':
    #     manual_classification = 'TECHNICAL_DEBT'
    
    cursor.execute("select distinct(td_classification) from processed_comments where treated_comment_text = %s and repository_id = 2", (treated_comment_text, ))
    automatic_classification_result = cursor.fetchone()

    if automatic_classification_result is None:
        print ("error")
    else:

        automatic_classification = automatic_classification_result[0]

        if automatic_classification == manual_classification:

            if manual_classification == 'WITHOUT_CLASSIFICATION':
                true_negative = true_negative + 1
                # print("true_negative " , manual_classification, " ", automatic_classification)
            else:
                true_positive = true_positive + 1
                # print("true_positive " , manual_classification, " ", automatic_classification)
        
        else:
            if manual_classification == 'WITHOUT_CLASSIFICATION':
                false_positive = false_positive + 1
                # print("false_positive " , manual_classification, " ", automatic_classification)
            else:
                false_negative = false_negative + 1
                # print("false_negative " , manual_classification, " ", automatic_classification)

    print (progress_counter, "out of:", total_files_to_process )

print('true_positive', true_positive)
print('true_negative', true_negative)
print('false_positive', false_positive)
print('false_negative', false_negative)


recall    = float(true_positive) / float((true_positive + false_negative))
precision = float(true_positive) / float((true_positive + false_positive))
f1measure = ((precision * recall) / (precision + recall)) * 2

print ("Precision:", precision, " Recall:", recall , "F1 measure: ", f1measure)

