
-- show all comments that the TD was removed
select project_name, file_name , version_introduced_author, version_removed_author from technical_debt_summary where version_removed_name != 'not_removed' order by 1,2;

RQ1 - How much of self-admitted technical debt gets removed ? [repeat]
(consistency of code and comment co-change) 

select count(*) from processed_comments 
3942803

-- total of TD comments
select repository_id , count(*) from processed_comments where td_classification != 'WITHOUT_CLASSIFICATION' group by 1 order by 1;
 2 | 10729
 3 | 21356
 5 | 20141
 6 | 18927
 7 | 26725
 8 |  1893
 9 |  4810


select repository_id, count(*) from processed_comments where td_classification != 'WITHOUT_CLASSIFICATION' and is_introduced_version is true group by 1 order by 1;
2 |   854
3 |  1260
5 |  4331
6 |  1164
7 |  1317
8 |   135
9 |   271

-- how much of them has been removed
select repository_id, count(*) from processed_comments where is_introduced_version = true and has_removed_version = true group by 1 order by 1;
2 |   728
3 |   981
5 |  3926
6 |   472
7 |  1009
8 |   118
9 |   208

-- how much of them still in the project
select repository_id, count(*) from processed_comments where is_introduced_version = true and has_removed_version = false group by 1 order by 1;
2 |   126
3 |   279
5 |   405
6 |   692
7 |   308
8 |    17
9 |    63

-- how much of the removal was done by the same author who introduced
-- select removed_version_author , introduced_version_author from processed_comments where has_removed_version = true and removed_version_author = introduced_version_author;
select repository_id, count(*) from processed_comments where has_removed_version = true and removed_version_author = introduced_version_author group by 1 order by 1;
2 |   372
3 |   663
5 |  2652
6 |   116
7 |   578
8 |    72
9 |   149

-- how much of the removal was done by a different author who introduced
-- select removed_version_author , introduced_version_author from processed_comments where has_removed_version = true and removed_version_author != introduced_version_author;
select repository_id, count(*) from processed_comments where has_removed_version = true and removed_version_author != introduced_version_author group by 1 order by 1;
2 |   356
3 |   318
5 |  1274
6 |   356
7 |   431
8 |    46
9 |    59


RQ2 - How long does it take to remove technical debt in case of self-removal?
-- general
select repository_id, avg(age(removed_version_date, introduced_version_date)) from processed_comments where has_removed_version = true group by 1 order by 1;
---------------+---------------------------------------
2 | 1 year 1 mon 31 days 31:23:00.099022
3 | 1 year 3 mons 42 days 16:00:56.758214
5 | 2 mons 21 days 10:37:40.879433
6 | 10 mons 23 days 15:17:08.213173
7 | 1 year 7 mons 35 days 22:04:13.751373
8 | 1 year 4 mons 29 days 28:03:26.58758
9 | 5 mons 24 days 31:31:39.660069 

-- self-removal
select repository_id , avg(age(removed_version_date, introduced_version_date)) from processed_comments where has_removed_version = true and introduced_version_author = removed_version_author group by 1 order by 1;
---------------+-------------------------------------------
 2 | 4 mons 18 days 13:37:20.372864       | 54.95469                             
 3 | 11 mons 41 days 30:08:06.652812      | 148.8064                             
 5 | 1 mon 16 days 12:56:34.245269        | 18.16019                      
 6 | 3 mons 12 days 31:15:36.975089       | 52.9247                       
 7 | 4 mons 22 days 18:42:26.783992       | 8.750382                             
 8 | 6 mons 16 days 24:55:41.098244       | 68.07265                            
 9 | 1 mon 27 days 17:51:06.191399        | 10.7359                      

median(data1$epoch_time_to_remove/86400)
[1] 18.16019


-- non-self-removal
select repository_id, avg(age(removed_version_date, introduced_version_date)) from processed_comments where has_removed_version = true and introduced_version_author != removed_version_author group by 1 order by 1 ;
--+----------------------------------------
2 | 1 year 11 mons 28 days 19:12:03.85102   |  179.0223                                    
3 | 2 years 23 days 17:08:38.835205         |  385.9666                              
5 | 4 mons 33 days 26:22:50.931217          |  28.08756                             
6 | 1 year 34 days 34:21:00.213896          |  376.7547                             
7 | 3 years 4 mons 26 days 24:31:12.810212  |  1301.488                                     
8 | 2 years 8 mons 39 days 30:52:06.600382  |  830.7921                                     
9 | 1 year 3 mons 21 days 29:27:18.282278   |  190.1779                                    
 
 median(data1$epoch_time_to_remove/86400)
[1] 126.9162


tool performance evaluation 

Automated approach
--total extracted comments: 
select count(*) from raw_comments where repository_id = 2;

--total analyzed comments: 
select count(*) from processed_comments where repository_id = 2;

--total technical debt:
select count(*) from processed_comments where repository_id = 2 and td_classification != 'WITHOUT_CLASSIFICATION';

--TD breakdown:   
select td_classification, count(*) from processed_comments where repository_id = 2 and td_classification != 'WITHOUT_CLASSIFICATION' group by 1;           

-- total unique extracted comments: 
select count(distinct(comment_text)) from raw_comments where repository_id = 2;

--total unique analyzed comments:
select count(distinct(treated_comment_text, file_id)) from processed_comments where repository_id = 2;

-- total unique technical debt: 
select count(distinct(treated_comment_text, file_id)) from processed_comments where repository_id = 2 and td_classification != 'WITHOUT_CLASSIFICATION';
select count(*) from processed_comments where is_introduced_version is true and repository_id = 2

-- unique TD breakdown:
select td_classification, count(distinct(treated_comment_text, file_id)) from processed_comments where repository_id = 2 and td_classification != 'WITHOUT_CLASSIFICATION' group by 1;
