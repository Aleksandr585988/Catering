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

### DEPLOYMENT
Set CI/CD
code quality tools
tests
Select Cloud Provider
Digital Ocean
Rent instance (machine)
Clone Project
Infra:
Native (bare metal)
Machine with application
Machine with worker (or same?)
Database
...
Docker Infra
Machine with Docker
Select HTTP-serverssh Hillyl Catering Gubanov Alex
security
SSL Certificates
Access to staticfiles
Reverse Proxy


<!-- ### Loading Test Data (Fixtures)

To load mock data for the models: 
`DishOrderItem` 
`DishesOrder` 
`User` 
`DeliveryDishesOrder` 


1. Ensure the fixture file is located at `products/fixtures/.....`.
2. Run the following command to load the data:

   ```bash
   python manage.py loaddata fixtures/logistic_fixture.json
   python manage.py loaddata fixtures/dish_order_fixture.json
   python manage.py loaddata fixtures/user_fixtures.json
   python manage.py loaddata fixtures/dish_order_item_fixture.json
   ```

3. After the data is loaded, the model will be populated with test data.

**Note:** Ensure that restaurants `Melange` and `Bueno` are present and have been populated, 
along with the dishes `Пицца`, `Суши` and `Салат`.

You can use JSON fixtures like this in your project to easily update and manage test data. -->