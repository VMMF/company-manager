To clean windows cmd console
Command : cls 

To save database content to JSON
Command : python manage.py  dumpdata companymanager --indent 4 > companymanager/fixtures/dataPPI.json
Reference: https://docs.djangoproject.com/en/3.1/topics/serialization/#natural-keys


To load fixtures (database data) and avoid populating the database by hand
Command: python manage.py loaddata dataPPI.json
Reference:https://docs.djangoproject.com/en/3.1/topics/serialization/#natural-keys


To reset database:

set PGPASSWORD=1234&& psql -U postgres
DROP DATABASE IF EXISTS company_manager_db;
CREATE DATABASE company_manager_db;
\q

python manage.py migrate
python manage.py makemigrations companymanager
python manage.py migrate companymanager

python manage.py createsuperuser --username JohnDoe --email admin@mydomain.com

python manage.py loaddata dataExampleCompany.json
python manage.py create_groups

python manage.py runserver



To "debug" in VS Code
https://stackoverflow.com/questions/40849115/how-to-run-debug-django-app-in-visual-studio-code

To debug in Console

python manage.py shell

from  companymanager.models import Project,Order,Client,HoursByOrderByStaff,ServiceCategory,Service,Staff,StaffCategory,Client,ClientFacility,ClientDepartment,ClientAccount,ClientIndustry

