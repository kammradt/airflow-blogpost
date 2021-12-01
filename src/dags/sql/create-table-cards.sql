create table if not exists cards(
    id serial constraint cards_pk primary key,
    name text not null,
    url text not null,
    price float not null,
    created_at date not null default current_date
);