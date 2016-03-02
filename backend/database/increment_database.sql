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
    has_local_copy boolean default false,
    has_parsed_file boolean default false,
    UNIQUE(file_id, commit_hash)
);


    
