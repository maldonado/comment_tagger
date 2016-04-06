create table repositories (
    id serial,
    name text,
    master_branch text,
    clone_url text,
    cloned_date timestamp default now(),
    UNIQUE (clone_url)
);

create table tags (
    id serial,
    repository_id numeric,
    extracted_date timestamp default now(),
    name text,
    version_order numeric,
    UNIQUE (repository_id,name)
);

create table files (
    id serial, 
    repository_id numeric,
    extracted_date timestamp default now(),
    name text,
    file_path text,
    deletion_commit_hash text default null,
    UNIQUE(repository_id,name,file_path)
);

create table file_versions (
    id serial,
    repository_id numeric,
    file_id numeric,
    commit_hash text,
    author_name text,
    author_email text,
    author_date timestamp,
    version_path text, 
    older_version_path text,
    has_local_file boolean default false,
    has_parsed_file boolean default false,
    UNIQUE(file_id, commit_hash)
);

create table raw_comments (
    id serial,
    repository_id numeric, 
    file_id numeric,
    file_versions_id numeric,
    commit_hash text,
    comment_text text,
    comment_type text,
    comment_format text,
    start_line numeric,
    end_line numeric,
    has_class_declaration boolean,
    has_interface_declaration boolean,
    has_enum_declaration boolean,
    has_annotation_declaration boolean,
    class_declaration_lines text
);

with temp as (select id, repository_id from files )
update file_versions set repository_id = t.repository_id from temp t where t.id = file_versions.file_id 

create table processed_comments (
    id numeric,
    repository_id numeric, 
    file_id numeric,
    file_versions_id numeric,
    commit_hash text,
    comment_text text,
    treated_comment_text text,
    td_classification text,
    comment_type text,
    comment_format text,
    start_line numeric,
    end_line numeric,
    has_class_declaration boolean,
    has_interface_declaration boolean,
    has_enum_declaration boolean,
    has_annotation_declaration boolean,
    class_declaration_lines text
);


create table manually_classified_comments (
    id serial,
    project_origin text,
    comment_text text, 
    treated_comment_text text, 
    classification text
);

insert into manually_classified_comments (project_origin, comment_text, treated_comment_text, classification) 
    select a.projectname, b.commenttext, b.treated_commenttext, b.classification from comment_class a, processed_comment b where a.id = b.commentclassid 

update manually_classified_comments set classification = 'WITHOUT_CLASSIFICATION' where classification = 'BUG_FIX_COMMENT';
update manually_classified_comments set classification = 'REQUIREMENT' where classification = 'IMPLEMENTATION';
delete from manually_classified_comments where treated_comment_text = ''

alter table processed_comments add column introduced_version_commit_hash text;
alter table processed_comments add column is_introduced_version boolean;
alter table processed_comments add column introduced_version_author text;
alter table processed_comments add column introduced_version_date timestamp;
alter table processed_comments add column removed_version_commit_hash text;
alter table processed_comments add column has_removed_version boolean;
alter table processed_comments add column removed_version_author text;
alter table processed_comments add column removed_version_date timestamp;

-- move to class
alter table processed_comments add column interval_time_to_remove text;
with temp as (select id, age(removed_version_date, introduced_version_date) as interval_time from processed_comments where has_removed_version = true)
update processed_comments set interval_time_to_remove = t.interval_time from temp t where t.id = processed_comments.id 

alter table processed_comments add column epoch_time_to_remove numeric;




