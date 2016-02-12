create table cloned_repositories (
    id serial,
    name text,
    clone_url text,
    cloned_date timestamp default now()
)