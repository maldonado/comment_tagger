
-- show all comments that the TD was removed
select project_name, file_name , version_introduced_author, version_removed_author from technical_debt_summary where version_removed_name != 'not_removed' order by 1,2;

RQ1 - How much of self-admitted technical debt gets removed ? [repeat]
(consistency of code and comment co-change) 

select count(*) from processed_comments 
13953

-- total of TD comments
select count(*) from processed_comments where td_classification != 'WITHOUT_CLASSIFICATION';
1147

-- wrong way of counting ... 
select count(distinct(treated_comment_text)) from processed_comments where td_classification != 'WITHOUT_CLASSIFICATION';
188

-- how much of them has been removed
select count(*) from processed_comments where is_introduced_version = true and has_removed_version = true;
169

-- how much of them still in the project
select count(*) from processed_comments where is_introduced_version = true and has_removed_version = false;
19

-- how much of the removal was done by the same author who introduced
select removed_version_author , introduced_version_author from processed_comments where has_removed_version = true and removed_version_author = introduced_version_author;
160

-- how much of the removal was done by a different author who introduced
select removed_version_author , introduced_version_author from processed_comments where has_removed_version = true and removed_version_author != introduced_version_author;
9 


RQ2 - How long does it take to remove technical debt in case of self-removal?
-- general
select avg(age(removed_version_date, introduced_version_date)) from processed_comments where has_removed_version = true;
              avg
--------------------------------
 2 mons 21 days 21:15:03.426699
 

-- self-removal
select avg(age(removed_version_date, introduced_version_date)) from processed_comments where has_removed_version = true and introduced_version_author = removed_version_author;
             avg
-----------------------------
 1 mon 40 days 06:49:39.3625

median(data1$epoch_time_to_remove/86400)
[1] 60.03586


-- non-self-removal
select avg(age(removed_version_date, introduced_version_date)) from processed_comments where has_removed_version = true and introduced_version_author != removed_version_author;
              avg
--------------------------------
 9 mons 17 days 26:59:58.362133
 median(data1$epoch_time_to_remove/86400)
[1] 62.29199


-- median design removal
> median(data1$epoch_time_to_remove/86400)
[1] 82.34905

-[ RECORD 1 ]-----+------------
td_classification | DESIGN
count             | 38


-[ RECORD 2 ]-----+------------
td_classification | REQUIREMENT
count             | 131

-- medeian requirement removal
 median(data1$epoch_time_to_remove/86400)
[1] 60.03586

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

-- unique TD breakdown:
select td_classification, count(distinct(treated_comment_text, file_id)) from processed_comments where repository_id = 2 and td_classification != 'WITHOUT_CLASSIFICATION' group by 1;
