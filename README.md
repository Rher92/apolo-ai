# apolo

[![Build Status](https://travis-ci.org/rher92/apolo.svg?branch=master)](https://travis-ci.org/rher92/apolo)
[![Built with](https://img.shields.io/badge/Built_with-Cookiecutter_Django_Rest-F7B633.svg)](https://github.com/agconti/cookiecutter-django-rest)

Its all about a Weissman score > 5.0. Check out the project's [documentation](http://rher92.github.io/apolo/).

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)  
- Docker compose 

# Local Development

Start the dev server for local development:
```bash
docker-compose up

or 

docker compose up
```

Run any django command:
```bash
docker-compose run web python manage.py <command>

or 

docker compose run web python manage.py <command>

e.g.

docker compose run web python manage.py shell_plus
```

Happy path flow:

1. Create product

```bash
curl --location 'http://127.0.0.1:8000/api/v1/products/' \
--form 'name="test1"' \
--form 'price_per_unit="12"' \
--form 'quantity="100"'
```

2. List products

```bash
curl --location 'http://127.0.0.1:8000/api/v1/products/'
```

3. Create order

```bash
curl --location 'http://127.0.0.1:8000/api/v1/orders/' \
--header 'Content-Type: application/json' \
--data '{
    "products": [
        {"id": 3, "quantity": 4}
    ]
}'
```

4. List orders

```bash
curl --location 'http://127.0.0.1:8000/api/v1/orders/'
```
