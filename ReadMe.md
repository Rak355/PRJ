#At command line type these instructions

1. pip install Flask
2. pip install --upgrade firebase-admin
3. export FLASK_APP=backend
4. flask run

#On browser go to local address

1. 127.0.0.1:5000/  is the index page
2. 127.0.0.1:5000/signup is the signup page
3. 127.0.0.1:5000/login is the login page
4. 127.0.0.1:5000/main is the page after successful login

#Assumptions

1. All company names must be unique.
2. User must logout to login with anoter credentials
3. User must edit or delete only one row (company) at a time, otherwise the behaviour webapp is undefined and may lead to inconsistencies in the database.
