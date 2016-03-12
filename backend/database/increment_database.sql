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






