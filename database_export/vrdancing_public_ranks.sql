create table ranks
(
    id          serial not null,
    discordid   text,
    username    text,
    bootyxp     integer,
    rank        text,
    datejoined  text,
    description text,
    birthday    text,
    country     text,
    swsxp       boolean
);