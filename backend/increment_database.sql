create table cloned_repositories (
    id serial,
    name text,
    clone_url text,
    cloned_date timestamp default now()
)

create table extracted_tags (
    id serial,
    cloned_repository_id numeric,
    extracted_date timestamp default now(),
    name text,
    version_date timestamp,
    version_order numeric
)