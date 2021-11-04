insert into cards (name, url, price) 
values (
    '{{ params.name }}',
    '{{ params.url }}',
    {{ params.price }}
);