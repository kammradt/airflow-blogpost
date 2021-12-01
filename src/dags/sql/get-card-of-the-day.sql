select name, price, url
from cards where created_at = current_date
order by price desc limit 1;