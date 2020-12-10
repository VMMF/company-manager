Autor: Victor Mendez

Instructions for project development on Windows 10 PC

# Used software

Visual Studio Code 1.51.1
	Reference: https://code.visualstudio.com/
Python 3.9.1
	Reference: https://www.python.org/downloads/

#Project

- Create a folder called company-manager
- From Visual Studio Code, open a console in company-manager folder and type:
	Command: pip install pipenv
	Note: pipenv makes it very easy to manage the project dependencies
	Reference: https://realpython.com/pipenv-guide/
	
- Create a virtual environment for the project to install all dependencies that it will require
	Commnad: pipenv shell
	Note: A Pipfile will be created in company-manager folder and virtual environment files and installations are stored in C:\Users\Username\.virtualenvs
	
	Alternative: To be able to later debug in VS Code, it is better to create the virtual environment inside VS Code and let VS Code Manage it directly
	Command: python -m venv .venv  
	Reference: https://stackoverflow.com/questions/54106071/how-to-setup-virtual-environment-for-python-in-vs-code

#Backend

- Install django in your virtual environment
	Command: pipenv install django
	pipenv install psycopg2
	Note: A Pipfile.lock  will be created in company-manager folder
	
- Install libraries to provide additional data storing and processing functionalities
	pipenv install django-phone-field
	pipenv install pandas
	pipenv install xlrd
	
- Start a django project named backend where we will develop our backend
	Command: django-admin startproject backend
	Note: a backend folder will be created with a few .py template files inside
	Reference: https://docs.djangoproject.com/en/3.1/intro/tutorial01/
	
- Enter the newly created backend folder
	Command: cd backend

- Create a django App called companymanager inside the django project named backend
	Command: python manage.py startapp companymanager
	
- 

#Database

- Install PostgreSQL database (in my case I'm using version 12)
	Reference: https://www.postgresql.org/download/windows/
	
- Open pgAdmin4 database managament software which is installed allong with PostgreSQL
	Note: By default it is installed on C:\Program Files\PostgreSQL\12\pgAdmin 4\bin
	
- On pgAdmin4, create a PostgreSQL database called company_manager_db
	Note: It can also be created via commands see https://www.postgresql.org/docs/current/tutorial-createdb.html
	Command:
	set PGPASSWORD=1234&& psql -U postgres
	CREATE DATABASE company_manager_db;
	\q
	
- Add C:\Program Files\PostgreSQL\12\bin to the Windows PATH to be able to work with PostgreSQL from the console
	
#Backend

- Modify project settings.py DATABASES = {}, to connect to the PostgreSQL database using the adequate authentication settings
	Reference: https://stackoverflow.com/questions/63755924/after-migrate-command-django-automatically-creates-sqlite3-but-doesnt-automati?noredirect=1
	
- Send the default information (INSTALLED_APPS) from the newly created project backend to the PostgreSQL database
	Command: python manage.py migrate (If you happen to be outside the virtual environment type "pipenv shell" first)
	Note: Migrations are very powerful and let you change your models over time, as you develop your project, without the need to delete your database or tables and make new ones - it specializes in upgrading your database live, without losing data
	Reference: https://realpython.com/django-migrations-a-primer/
	
- Verify the database tables were updated via pgAdmin4 (doesn't refesh changes fast) or using 
	Command: psql -U postgres
	Note: I have assumed the default user named "postgres" will login so put this user's password. You will enter into PostgreSQL. Inside PostgreSQL type:
	Command: \c company_manager_db \dt
	Note: You need to be able to see tables
	Command: exit
	
- Run the development server to make sure it works
	Command: python manage.py runserver
	Note: You should see it working on http://127.0.0.1:8000/
	
- On django backend project on settings.py add on INSTALLED_APPS the django companymanager App

- On django App companymanager on models.py add the classes which will become the database tables
	Reference: https://docs.djangoproject.com/en/3.1/intro/tutorial02/
	
- On django App companymanager create the database tables structure (create migrations from models.py)
	Command: python manage.py makemigrations companymanager
	Result: On django App companymanager a migrations folder should be created with a 0001_initial.py
	
- On django App companymanager propagate the migrations to the database
	Command: python manage.py migrate companymanager
	Result: Verify the database tables were updated via pgAdmin4 or using commands
	Note: For curiosity, to see what SQL code should have to be written in order to create the database described in the migrations, type: python manage.py sqlmigrate companymanager 0001
	Verify that DateField are not migrated as DateTimeField
	Reference: https://docs.djangoproject.com/en/3.1/intro/tutorial02/
	
	
- Create an admin user for the site (separation between “content publishers” and the “public” site)
	Command: python manage.py createsuperuser
	Note: Input a name, email and password


- Alternative:(Optional) Load a default set of user with roles
	Command: python manage.py create_groups
	
- On django App companymanager admin.py, register the models previously defined in models.py

- (Optional) Load any previously saved database objects 
	Command: python manage.py loaddata companyData.json
	
	
- Start the backend project on a development server (not suitable for final use, only for development)
	Command: python manage.py runserver
	

	
#Frontend
