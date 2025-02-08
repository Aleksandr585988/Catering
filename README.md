# CATERING API

# TECH STACK

- Python - programming language
- Django -web framework
- DRF (Django REST Framework) - data validation
- PostgreSQL - Database (RDBMS)
  - tables
- Redis/MongoDB - Key-value Storage
  - json {"any-key": value}
- Manage dependencies...

# SETUP
- activate virtual environment
  - pipenv shell --python python3.11


- generate `Pipfile.lock` file after adding dependencies 
  - pipenv lock
  

- install dependencies form `Pipfile.lock` file
  - pipenv sync

# Download test data
- python manage.py loaddata delivery/fixtures/delivery_data.json
- python manage.py loaddata food/fixtures/dishes.json
- python manage.py loaddata food/fixtures/dishesOrder.json
- python manage.py loaddata food/fixtures/dishOrderItem.json
- python manage.py loaddata food/fixtures/restaurants.json

# Why json?
1. Supporting complex structures: JSON allows you to store more complex data, in particular the relationships between models (for example, connections between tables by external keys). In CSV, this is more difficult because it does not support the structure of objects or connections between data.
2. Data Flexibility: JSON allows you to store different types of data, such as dates, boople values, or arrays that are useful for Django models. In CSV all data is stored as a text
3. Readiness and clarity: JSON looks more structured and more convenient for understanding, especially when the data is complex or containing several levels of investment.
4. Scale: If you want to add more data in the future, JSON is easier to scale as you can simply add new records without much restriction.