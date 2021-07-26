create table if not exists jobs (
    job_id uuid primary key,
    name text unique,

    state bigint default 0,
    errors text default '',
    inserted_at timestamp without time zone default (now() at time zone 'utc'),
    scheduled_at timestamp without time zone default (now() at time zone 'utc'),
    taken_at timestamp without time zone default null,
    internal_state jsonb default '{}',

    args jsonb default '{}'
);