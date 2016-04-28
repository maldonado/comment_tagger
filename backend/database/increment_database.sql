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
    comment_location text, 
    func_specifier text, 
    func_return_type text, 
    func_name text, 
    func_parameter_list text,
    has_class_declaration boolean,
    has_interface_declaration boolean,
    has_enum_declaration boolean,
    has_annotation_declaration boolean,
    class_declaration_lines text
);

alter table raw_comments add column comment_location text;
alter table raw_comments add column func_specifier text;
alter table raw_comments add column func_return_type text;
alter table raw_comments add column func_name text;
alter table raw_comments add column func_parameter_list text;
alter table raw_comments add column func_line numeric;

create unique index  id_raw_comenst_index on raw_comments (id);
create index repository_id_raw_comment_index on raw_comments (repository_id);

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

alter table processed_comments add column 
alter table processed_comments add column 
alter table processed_comments add column 
alter table processed_comments add column 
alter table processed_comments add column 
alter table processed_comments add column 


alter table processed_comments add column introduced_version_commit_hash text;
alter table processed_comments add column is_introduced_version boolean;
alter table processed_comments add column introduced_version_author text;
alter table processed_comments add column introduced_version_date timestamp;
alter table processed_comments add column removed_version_commit_hash text;
alter table processed_comments add column has_removed_version boolean;
alter table processed_comments add column removed_version_author text;
alter table processed_comments add column removed_version_date timestamp;
alter table processed_comments add column comment_location text;
alter table processed_comments add column func_specifier text;
alter table processed_comments add column func_return_type text;
alter table processed_comments add column func_name text;
alter table processed_comments add column func_parameter_list text;
alter table processed_comments add column func_line numeric;
alter table processed_comments add column interval_time_to_remove text;
alter table processed_comments add column epoch_time_to_remove numeric;
alter table processed_comments add column interval_time_in_the_system text;
alter table processed_comments add column epoch_time_in_the_system numeric;

create unique index id_processed_comments_index on processed_comments (id);
create index file_versions_id_processed_comments_index on processed_comments (file_versions_id);
create index repository_id_processed_comments_index on processed_comments (repository_id);
create index treated_comment_text_processed_comments_index on processed_comments (treated_comment_text);


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

with temp as (select id, repository_id from files)
update file_versions set repository_id = t.repository_id from temp t where t.id = file_versions.file_id 


create table aux_last_found_version_before_removal (
    processed_comment_id numeric,
    last_found_commit_hash text,
    last_found_comment_location text,
    last_found_func_specifier text,
    last_found_func_return_type text,
    last_found_func_name text,
    last_found_func_parameter_list text,
    last_found_func_line numeric
)

alter table aux_last_found_version_before_removal add column last_found_author text;
alter table aux_last_found_version_before_removal add column last_found_date timestamp;

with temp as (select a.id, b.id as processed_comment_id, author_date, author_name from file_versions a, processed_comments b, aux_last_found_version_before_removal c where b.id = c.processed_comment_id and b.file_versions_id = a.id and b.commit_hash = a.commit_hash)
update aux_last_found_version_before_removal set last_found_date = t.author_date, last_found_author = t.author_name from temp t where t.processed_comment_id = aux_last_found_version_before_removal.processed_comment_id 


