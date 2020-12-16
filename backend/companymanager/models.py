from django.db import models

#to be able to work with time
from django.utils.timezone import now, localtime
from django.utils import timezone
import datetime

#to be able to have a phoe field
from phone_field import PhoneField

# to validate numeric fields
from django.core.validators import MaxValueValidator, MinValueValidator

# to create Django users (assign permissions to rows in Staff table) and groups programmatically
from django.core.management import BaseCommand
from django.contrib.auth.models import User, Group , Permission


# References : 
# https://www.geeksforgeeks.org/uniquetrue-django-built-in-field-validation/
# https://docs.djangoproject.com/en/3.1/ref/models/fields/






class Project(models.Model):
    project_number = models.IntegerField(unique=True,primary_key=True)
    client = models.ForeignKey("Client", on_delete=models.CASCADE,verbose_name = "Customer of the project") # one project only belongs to 1 client, but 1 client may have many projects

    project_name = models.CharField(max_length=400)
    project_creation_date = models.DateField("Date project is created")
    # project_model_number = models.CharField(max_length=200,blank=True,default="") # useful if a specific piece of equipment is involved in a project
    project_planner = models.ForeignKey("Staff", on_delete=models.CASCADE) # select from a list of available employees

    PROJECT_STATUS_CHOICES = [
        ("OP", "Opened"),
        ("IP", "In Progress"),
        ("HO", "Hold"),
        ("CP", "Completed"),
        ("CA", "Cancelled"),
    ]
    
    project_status = models.CharField(
        max_length=2,
        choices=PROJECT_STATUS_CHOICES,
        default="OP"
    )

    project_internal_notes = models.TextField(blank=True,default="")



    def __str__(self):
        return str(self.project_number) + (" : ") + str(self.project_name) 

    # def get_client(self):
    #     return self.Project.client




def get_target_completion_date():
    target_completion_date = localtime(now())
    if target_completion_date.month == 11:
        target_completion_date = datetime.datetime(localtime(now()).year + 1,1,localtime(now()).day)
    elif target_completion_date.month == 12:
        target_completion_date = datetime.datetime(localtime(now()).year + 1,2,localtime(now()).day)
    else:
        target_completion_date = datetime.datetime(localtime(now()).year,localtime(now()).month + 2,localtime(now()).day) # assumed the default time to complete a PO is 2 months

    return target_completion_date



# class RestrictUserOrderManager(models.Manager):

#     def by_user(self,user):
#         queryset = super(RestrictUserOrderManager,self).get_queryset()

#         if user.is_restricted:
#             queryset = queryset.annotate(field_to_show=None) # field_to_show is a queryset field (not in any model)
#         else:
#             queryset = queryset.annotate(field_to_show= ["order_budget_total","order_budget_labor","order_budget_material"])

#         return queryset


# https://www.revsys.com/tidbits/tips-using-djangos-manytomanyfield/ (and related_name)
class Order(models.Model): 

    order_project = models.ForeignKey("Project", on_delete=models.CASCADE,verbose_name = "Project to which this order is associated",related_name= "orders_for_project")
 
    order_number = models.IntegerField(default=1,validators=[MinValueValidator(1)])

    # restricted_order_info = RestrictUserOrderManager()

    order_name = models.CharField(max_length=200) 
    class Meta:
        #TODO capture error and present it in human readable form https://stackoverflow.com/questions/55714632/is-it-possible-to-override-the-error-message-that-django-shows-for-uniqueconstra
        constraints = [ models.UniqueConstraint(fields= ["order_project","order_number"], name = "unique_order_id"),
                            #models.CheckConstraint(check=models.Q(order_number__gte=0),name="order_number__gte_0")  
                    ]

    # hidden field to be able to search using "order_project-order_number"
    order_and_project_number = models.CharField(max_length = 200,editable=False, default = "")
    
    def save(self, *args, **kwargs):
        self.order_and_project_number = str(self.order_project.project_number) + "-" + str(self.order_number)

        # if someone marks the order as completed assume that moment as order completion date
        if self.order_completion_date == None and self.order_status == "CO":
            self.order_completion_date = localtime(now())

        #if someone provides an order_completion_date assume that order as completed
        if self.order_completion_date != None:
            self.order_status = "CO"

        super(Order, self).save(*args, **kwargs)


    order_description = models.TextField(blank=True,null=True,default="")
    order_creation_date = models.DateField("Date purchase order received", default = datetime.date.today) 
    expected_order_completion_date = models.DateField("Order target completion date", default = get_target_completion_date)


    order_completion_date = models.DateField("Order completion date",blank=True,null=True,default="")
    

    order_planner = models.ForeignKey("Staff",on_delete=models.CASCADE,related_name = "planer_of_orders",verbose_name = "Staff member responsible for order execution") # select from a list of available employees

    order_facility = models.ManyToManyField("ClientFacility") #An order may involve more than 1 facility and a facility can be involved in more than 1 order as time passes
    
    order_service_type = models.ForeignKey("Service", on_delete=models.CASCADE,verbose_name = "Type of service provided in this order")
    order_budget_total = models.DecimalField(max_digits=19,decimal_places=2,validators=[MinValueValidator(0)])
    order_budget_labor = models.DecimalField(max_digits=19,decimal_places=2,validators=[MinValueValidator(0)])
    order_budget_material = models.DecimalField(max_digits=19,decimal_places=2,validators=[MinValueValidator(0)])
    order_times_reviewed = models.IntegerField(default=0)

    order_model_number = models.CharField(max_length=200,blank=True,default="") # useful if a specific piece of equipment is involved in an order
    order_serial_number = models.CharField(max_length=200,blank=True,default="") # useful if a specific piece of equipment is involved in an order

    order_customer_PO = models.CharField(max_length=200,blank=True,default="")
    order_invoice_number = models.CharField(max_length=200,blank=True,default="")
    order_internal_notes = models.TextField(blank=True,default="")
    order_client_notes = models.TextField(blank=True,default="")

    
    # Ordered status are fixed to the amount on the list below
    ORDER_STATUS_CHOICES = [
        ("OP", "Opened"),
        ("QU", "Quoted"),
        ("PO", "PO Received"),
        ("DA", "Design Approved"),
        ("HO", "Hold"),
        ("AC", "Assembly Complete"),
        ("PI", "Proceed with Invoices"),
        ("PS", "Product Shipped"),
        ("RS", "Report Sent"),
        ("FI", "Final Invoice Sent"),
        ("CO", "Completed"),
        ("CA", "Cancelled"),
    ]
    
    order_status = models.CharField(
        max_length=2,
        choices=ORDER_STATUS_CHOICES,
        default="OP"
    )

    BILLING_CHOICES = [
        ("FI", "Fixed"),
        ("HO", "Hourly"),
    ]

    order_billing = models.CharField(
        max_length=2,
        choices=BILLING_CHOICES,
        default="FI"
    )

    

    def __str__(self):
        # the_client_name = self.order_project.client.client_name
        # the_client_id = self.order_project.client.pk
        # the_facilities = list(ClientFacility.objects.all().filter(client__exact = the_client_id).values_list("facility_name",flat=True))
        # facilities_dict[the_client_name] = the_facilities

        return str(self.order_project.project_number) + ("-") + str(self.order_number) + (" : ") + str(self.order_name) 


# # Options to add/remove should be made available
# # ServiceCodes don"t seem to be used on any other class (one to one with order?)
# class ServiceCodes (models.Model):

#     service_code_id = models.IntegerField(unique=True,primary_key=True)

#     SERVICE_CATEGORY_MT_SERVICE_CODES_CHOICES = [
#         ("FS", "Field Technical Services"),
#         ("OH", "Overhead and Administration"),
#         ("SH", "Shop Work"),
#     ]

#     service_category_MT_service_codes = models.CharField(
#         max_length=2,
#         choices=SERVICE_CATEGORY_MT_SERVICE_CODES_CHOICES,
#         default="SH"
#     )

#     SERVICE_CATEGORY_EC_SERVICE_CODES_CHOICES = [
#         ("AS", "Automation services"),
#         ("AD", "AutoCAD Drafting"),
#         ("CR", "Contract Rate"),
#         ("ED", "Engineering Design"),
#         ("EA", "Engineering Analysis"),
#         ("FS", "Field Technical Services"),
#         ("OH", "Overhead and Administration"),
#         ("SH", "Shop Work"),
#         ("PS", "Product Sales, Purchase and Resell"),
#         ("PA", "Customer Project Administration and Management"),
#         ("EC", "Engineer, Procure, Construct"),
#     ]

#     service_category_EC_service_codes = models.CharField(
#         max_length=2,
#         choices=SERVICE_CATEGORY_EC_SERVICE_CODES_CHOICES,
#         default="ED"
#     )



# Options to add/remove should be made available
class ServiceCategory(models.Model):
    #service_category_id = models.IntegerField(unique=True,primary_key=True)
    service_category_name = models.CharField(max_length=200,unique=True)

    def __str__(self):
        return self.service_category_name

    class Meta:
        verbose_name_plural = "Service categories"

    

    # SERVICE_CATEGORY_CHOICES = [
    #     ("MT", "Maintenance and Testing"),
    #     ("EC", "Engineering, Design-Build, Fabrication, Installation"),
    # ]

    # service_category = models.CharField(
    #     max_length=2,
    #     choices=SERVICE_CATEGORY_CHOICES,
    #     default="EC"
    # )



# Options to add/remove should be made available
class Service (models.Model):

    #services_id = models.IntegerField(unique=True,primary_key=True)
    service_name = models.CharField(max_length=200,unique=True)
    service_category = models.ForeignKey("ServiceCategory", on_delete=models.CASCADE,verbose_name = "Category of the Service") #a Service can only have 1 ServiceCategory

    def __str__(self):
        return str(self.service_name)

    # SERVICEs_MT_SERVICE_CODES_CHOICES = [
    #     ("MT", "Maintenance and Testing"),
    #     ("GT", "Ground System Testing"),
    #     ("IA", "Infrared Analysis/Thermal Imaging"),
    #     ("TO", "Transformer Oil and Gas Analysis"),
    #     ("PQ", "Power Quality and Energy Recording"),
    # ]

    # service_category_MT_service_codes = models.CharField(
    #     max_length=2,
    #     choices=SERVICEs_MT_SERVICE_CODES_CHOICES,
    #     default="MT"
    # )

    # SERVICES_EC_SERVICE_CODES_CHOICES = [
    #     ("IC", "Install and Commission New Equipment"),
    #     ("EI", "Equipment Improvement and Life Extension"),
    #     ("PD", "Product Design and Manufacturing"),
    #     ("PS", "Product Sales"),
    #     ("PF", "Panel Fabrication"),
    #     ("ED", "Electrical System Engineering and Design"),
    #     ("AF", "Electrical Studies and Arc Flash Improvements"),
    #     ("QI", "Electrical Power Quality Engineering"),
    #     ("DR", "Electrical Drawings"),
    #     ("CD", "Control Design, Automation and Integration"),
    #     ("SC", "Planning and Site Coordination"),
    # ]

    # service_category_EC_service_codes = models.CharField(
    #     max_length=2,
    #     choices=SERVICES_EC_SERVICE_CODES_CHOICES,
    #     default="DR"
    # )



# # TODO Needs to be populated on the database. Not hardcoded. \
# # Options to add/remove should be made available
# class Products(models.Model):
#     pass

# # TODO Needs to be populated on the database. Not hardcoded. \
# # Options to add/remove should be made available
# class ProductCategories(models.Model):
#     pass


class Staff(models.Model):

    #link the staff table to django authorization for User
    # authentication_and_authorisation_user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    
    staff_name = models.CharField(max_length=200,unique=True)
    staff_position_in_company = models.CharField(max_length=200)
    staff_start_date_in_company = models.DateField("Date started working at office")
    staff_category = models.ForeignKey("StaffCategory", on_delete=models.CASCADE) # staff can only be of 1 type (their main role even though they get involved in multiple roles)
    staff_hourly_salary = models.DecimalField(max_digits=5,decimal_places=2)

    def __str__(self):
        return str(self.staff_name)

    class Meta:
        verbose_name_plural = "Staff"


# Options to add/remove should be made available
class StaffCategory(models.Model):
    #staff_category_id = models.IntegerField(unique=True,primary_key=True)
    staff_category_name = models.CharField(max_length=200,unique=True)

    #e.g Administration, Electrical ,Planning and Design, Mechanical, Technical

    def __str__(self):
        return str(self.staff_category_name)

    class Meta:
        verbose_name_plural = "Staff categories"


def get_default_task_start_time ():

    default_task_start_time = localtime(now())
    
    if default_task_start_time.hour >= 8 and default_task_start_time.hour <= 12:
        default_task_start_time = datetime.datetime(localtime(now()).year,localtime(now()).month,localtime(now()).day,8,0,0)
    elif default_task_start_time.hour > 12:
        default_task_start_time = datetime.datetime(localtime(now()).year,localtime(now()).month,localtime(now()).day,12,0,0)

    return default_task_start_time


def get_default_task_end_time ():  
    default_task_end_time = localtime(now()) 

    if default_task_end_time.hour > 12 and default_task_end_time.hour <= 4:
        default_task_end_time = datetime.datetime(localtime(now()).year,localtime(now()).month,localtime(now()).day,12,0,0)
    elif default_task_end_time.hour > 4:
        default_task_end_time = datetime.datetime(localtime(now()).year,localtime(now()).month,localtime(now()).day,16,30,0)

    return default_task_end_time

    


class StaffTimeSheet(models.Model):

    time_sheet_owner = models.ForeignKey("Staff", on_delete=models.CASCADE,help_text= "Employee name")    

    task_belongs_to_order = models.ForeignKey("Order",on_delete=models.CASCADE, related_name = "order_present_in_timesheet_of") 

    task_start_time = models.DateTimeField(default  = get_default_task_start_time) 
    task_end_time = models.DateTimeField(default = get_default_task_end_time) 

    #Don"t allow 2 taks to be introduced on the database with the same start and end time on the same day
    class Meta:
        constraints = [ models.UniqueConstraint(fields= ["time_sheet_owner","task_start_time","task_end_time"], name = "unique_StaffTimeSheet_tasks"),
                    ]
 
    def worked_hours(self):
        time_difference = self.task_end_time - self.task_start_time
        hours = time_difference.days*24 + time_difference.seconds//3600
        minutes = (time_difference.seconds//60)%60
        if hours >= 0 and minutes >= 0:
            return str(hours) + ":" + str(minutes )
        else:
            return "Negative time! Correct."

    def worked_hours_math(self):
        time_difference = self.task_end_time - self.task_start_time
        hours = time_difference.days*24 + time_difference.seconds/3600
        if hours >= 0:
            return hours
        else:
            return 0

    task_time_code = models.ForeignKey("TimeCode", on_delete=models.CASCADE,verbose_name = "Time code" ,related_name = "in_timesheets_of") 
    task_description = models.TextField() #blank=True,default=""

    # https://docs.djangoproject.com/en/3.1/topics/db/models/#model-methods
    def save(self, *args, **kwargs):
        #Make sure for the same day and the same person 2 tasks are not overlapped in time
        super(StaffTimeSheet, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.time_sheet_owner) + " / " + str(localtime(self.task_start_time) )



class TimeCode (models.Model):
    time_code_name = models.CharField(max_length=300,unique=True)   
    time_code_description = models.TextField(blank=True,default="")

    def __str__(self):
        return self.time_code_name
    

# Options to add/remove should be made available
class Client(models.Model):
    #client_id = models.IntegerField(unique=True,primary_key=True) 
    client_name = models.CharField(max_length=300,unique=True) # one to many with a facility
    client_industry = models.ForeignKey("ClientIndustry", on_delete=models.CASCADE) # a client only has one industry type, however the same industry type can have many client members



    def __str__(self):
        return self.client_name


class ClientFacility(models.Model):
    
    client_name = models.ForeignKey("Client", on_delete=models.CASCADE,verbose_name = "Owner of the facility")  #a ClientFacility only belongs to 1 Client
    facility_name = models.CharField(max_length=300) # one to many with a facility

    # More than 1 client may have a facility with the same name. However the combination client-facility name must be unique
    class Meta:
        constraints = [ models.UniqueConstraint(fields= ["client_name","facility_name"], name = "unique_client_facility_id"),
                    ]
        verbose_name_plural = "Client facilities"

    def __str__(self):
        return self.facility_name + " : " + str(self.client_name.client_name)       

class ClientDepartment(models.Model):

    client_name = models.ForeignKey("Client", on_delete=models.CASCADE) # a client department can only belong to 1 client
    client_department_name = models.CharField(max_length=400)

    class Meta:
        constraints = [ models.UniqueConstraint(fields= ["client_name","client_department_name"], name = "unique_client_department_id"),
                    ]

    def __str__(self):
        return self.client_department_name

class ClientAccount (models.Model):

    client_name = models.ForeignKey("Client", on_delete=models.CASCADE) # a client account can only belong to 1 client
    account_user_name = models.CharField(max_length=400) # name of the representative of the customer

    #TODO add unique=True, null=True, blank=True
    account_email = models.EmailField(blank=True) # email of the representative of the customer
    
    #TODO add unique=True, null=True, blank=True
    account_phone = PhoneField(blank=True, help_text="Contact phone number")


    class Meta:
        #TODO Add account_phone and account_email to the constraints list
        #TODO Eliminate account_user_name from the constraints list
        constraints = [ models.UniqueConstraint(fields= ["client_name","account_user_name"], name = "unique_client_account_id"),
                    ]


    def __str__(self):
        return self.account_user_name

# Options to add/remove should be made available
class ClientIndustry (models.Model):

    client_industry_name = models.CharField(max_length=400,unique=True)

    def __str__(self):
        return self.client_industry_name

    class Meta:
        verbose_name_plural = "Client industry"

    # CLIENT_INDUSTRY_CHOICE = [
    #     ("MP", "Marine and Port"),
    #     ("GO", "Government Hospitals/Schools/Offices"),
    #     ("WT", "Water Treatment and Handling"),
    #     ("MA", "Manufacturing"),
    #     ("FB", "Food and Beverage"),
    #     ("TR", "Transportation"),
    #     ("TL", "Telecommunication"),
    #     ("AD", "Aerospace and Defence"),
    #     ("FA", "Forestry and Agriculture"),
    #     ("PP", "Pulp and Paper"),
    #     ("OG", "Oil and Gas"),
    #     ("MM", "Mining and Metals"),
    #     ("WE", "Wind Energy"),
    #     ("HG", "Hydro Generation"),
    #     ("EU", "Electric Utility"),
    #     ("SE", "Stock Equipment"),
    # ]

    # client_industry = models.CharField(
    #     max_length=2,
    #     choices=CLIENT_INDUSTRY_CHOICE,
    #     default="EU"
    # )



