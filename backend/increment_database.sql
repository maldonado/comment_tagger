create table repositories (
    id serial,
    name text,
    clone_url text,
    cloned_date timestamp default now()
)

create table tags (
    id serial,
    repository_id numeric,
    extracted_date timestamp default now(),
    name text,
    version_order numeric
)

