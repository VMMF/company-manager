from django.contrib import admin
from django import forms
from .models import Project,Order,Client,ServiceCategory,Service,Staff,StaffCategory,StaffTimeSheet,TimeCode,Client,ClientFacility,ClientDepartment,ClientAccount,ClientIndustry

#to be able to customize text display area
from django.forms import TextInput, Textarea
from django.db import models

#to be able to work with time
from datetime import datetime, timezone
import pytz # to localize naive datetime
from django.utils.timezone import now, localtime

# to use decimal numbers in currency fields
from decimal import Decimal

# to capture errors while importing into the database
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

# to be able to find elements in a long list of foreign or many to many relations
from django.contrib.admin.widgets import AutocompleteSelect, AutocompleteSelectMultiple


from django.contrib.auth.models import User, Group




#to load files from Excel
import os
from django.conf import settings
import pandas, numpy
import math


# Auxiliary functions

def day_hour_format_converter(date_time_UTC):
    local_time = localtime(date_time_UTC)
    return str(local_time.year) +"-"+ str(local_time.month) +"-"+ str(local_time.day) + "  " + str(local_time.hour) +":"+ str(local_time.minute) 

def day_format_converter(date):
    return str(date.year) +"-"+ str(date.month) +"-"+ str(date.day)


def ExcelProjectsLoader():

    """
    ExcelProjectsLoader loads an existing Excel project list spreadsheet into the database.
    The format of this spreadsheet is specific for this example and should be modified to be
    used for any other Excel file format.

    The path to the Excel file is hardcoded and some assumptions about default values for some fields have been made.
    This function should only be called once, while initially populating the database 
    """

    spreadsheet_file = pandas.read_excel (r"C:\@Victor\Programming\Portfolio\PPI Projects.xlsx")

    #filling client table
    client_info = pandas.DataFrame(spreadsheet_file, columns = ["Project Client Name"]) # assume cliend industry is always "To be defined"
    client_info = client_info.to_numpy().tolist()
    client_info_no_duplicates = []
    [client_info_no_duplicates.append(x) for x in client_info if x not in client_info_no_duplicates] 

    default_industry = None
    try:
        default_industry = ClientIndustry.objects.get(id=1)
    except ObjectDoesNotExist:
        default_industry = ClientIndustry(client_industry_name = "To be defined")
        default_industry.save()


    for client in client_info_no_duplicates:
        a_client = Client(client_name = client[0], client_industry = default_industry) #assuming clientindustry "To be defined" by default

        # if a_client.client_name not in ClientIndustry.objects.all():
        try:
            a_client.save()
        except IntegrityError as e:
            # print(e.__cause__)
            pass


    #filling client facility table
    client_facility_info = pandas.DataFrame(spreadsheet_file, columns = ["Project Client Name","Project Facility"])
    # client_facility_info.replace(numpy.nan,"Undefined", regex = True) # replaced cells with empty data by "Undefined string
    client_facility_info = client_facility_info.to_numpy().tolist()

    for client_facility in client_facility_info:
        
        a_client = Client.objects.all().filter(client_name = client_facility[0]) [0]

        a_client_facility = None
        # if math.isnan(client_facility[1]):
        if str(client_facility[1]) == "nan":
            a_client_facility = ClientFacility(facility_name = "Undefined", client_name = a_client)
        else:
            a_client_facility = ClientFacility(facility_name = client_facility[1], client_name = a_client)
            
        try:
            a_client_facility.save()
        except IntegrityError as e:
            pass


    #filling client department table
    client_department_info = pandas.DataFrame(spreadsheet_file, columns = ["Project Client Name","Project Department"])
    client_department_info = client_department_info.to_numpy().tolist()
    for client_department in client_department_info:
        
        a_client = Client.objects.all().filter(client_name = client_department[0]) [0]

        a_client_department = None
        if str(client_department[1]) == "nan":
            a_client_department = ClientDepartment(client_department_name = "Undefined", client_name = a_client)
        else:
            a_client_department = ClientDepartment(client_department_name = client_department[1], client_name = a_client)
            
        try:
            a_client_department.save()
        except IntegrityError as e:
            pass


    #filling client account table
    client_account_info = pandas.DataFrame(spreadsheet_file, columns = ["Project Client Name","Project Customer Contact"]) # asume generic email and fill missing Project Customer Contact with N/A
    client_account_info = client_account_info.to_numpy().tolist()
    for client_account in client_account_info:
        
        a_client = Client.objects.all().filter(client_name = client_account[0]) [0]

        a_client_account = None
        if str(client_account[1]) == "nan":
            a_client_account = ClientAccount(account_user_name = "Undefined", client_name = a_client)
        else:
            a_client_account = ClientAccount(account_user_name = client_account[1], client_name = a_client)
            
        try:
            a_client_account.save()
        except IntegrityError as e:
            pass




    #filling project table
    project_info = pandas.DataFrame(spreadsheet_file, columns = ["Project #","Project Client Name","Project Name","Project Date Created","Project Planner","Project Current Status","Project Internal Notes"]) 
    project_info = project_info.to_numpy().tolist()

    # if Project Planner is not defined assume John Doe
    try:
        default_project_planner = Staff.objects.get(staff_name = "John Doe")
    except ObjectDoesNotExist:
        default_project_planner = Staff(staff_name = "John Doe",staff_position_in_company = "Electrical Engineer",staff_start_date_in_company="2005-01-01",staff_category = "Technical",staff_hourly_salary = 25.0)
        default_project_planner.save()

    for project in project_info:

        a_client = Client.objects.all().filter(client_name = project[1]) [0]

        # solving missing project_planner
        if str(project[4]) == "nan":
            project[4] = default_project_planner
        else:
            project[4] = Staff.objects.all().filter(staff_name = project[4]) [0]

        # solving project_status
        if project[5] == "No Status":
            project[5] = "CA" # if Project Current Status == No Status, asume canceled
        elif project[5] == "Opened":
            project[5] = "OP"
        elif project[5] == "In Progress":
            project[5] = "IP"
        elif project[5] == "Hold":
            project[5] = "HO"
        elif project[5] == "Complete":
            project[5] = "CP"
        elif project[5] == "Cancelled":
            project[5] = "CA"

        if str(project[6]) == "nan":
            project[6] = ""



        a_project = Project(project_number = project[0], client = a_client,project_name = project[2],project_creation_date = project[3],project_planner = project[4],project_status = project[5], project_internal_notes = project[6])

        try:
            a_project.save()
        except IntegrityError as e:
            pass
    



    
    # filling service table
    service_info = pandas.DataFrame(spreadsheet_file, columns = ["Order Service"])
    service_info = service_info.to_numpy().tolist()
    # assume Unspecified service_category

    for service in service_info:

        default_service_category = ServiceCategory.objects.all().filter(service_category_name = "Unspecified") [0]

        if str(service[0]) == "nan":
            service[0] = "Unspecified"
        elif service[0] == "AD - AutoCAD Drafting":
            service[0] = "AutoCAD Drafting"
            default_service_category = ServiceCategory.objects.all().filter(service_category_name = "Engineering, Design-Build, Fabrication, Installation") [0]
        elif service[0] == "AS - Automation Services":
            service[0] = "Automation Services"
            default_service_category = ServiceCategory.objects.all().filter(service_category_name = "Engineering, Design-Build, Fabrication, Installation") [0]
        elif service[0] == "EA - Engineering Analysis":
            service[0] = "Engineering Analysis"  
            default_service_category = ServiceCategory.objects.all().filter(service_category_name = "Engineering, Design-Build, Fabrication, Installation") [0]
        elif service[0] == "EC - Engineer, Procure, Construct":
            service[0] = "Engineer, Procure, Construct" 
            default_service_category = ServiceCategory.objects.all().filter(service_category_name = "Engineering, Design-Build, Fabrication, Installation") [0]  
        elif service[0] == "ED - Engineering Design":
            service[0] = "Engineering Design" 
            default_service_category = ServiceCategory.objects.all().filter(service_category_name = "Engineering, Design-Build, Fabrication, Installation") [0]  
        elif service[0] == "FS - Field Technical Services":
            service[0] = "Field Technical Services" 
            default_service_category = ServiceCategory.objects.all().filter(service_category_name = "Maintenance and Testing") [0]     
        elif service[0] == "OH - Overhead and Adminstration":
            service[0] = "Overhead and Adminstration"                                
        elif service[0] == "PA - Customer Project Administration and Management":
            service[0] = "Customer Project Administration and Management" 
        elif service[0] == "R - Product Sales - purchase and resell":
            service[0] = "Product Sales - purchase and resell"
        elif service[0] == "S - Shop Work":
            service[0] = "Shop Work"            
            default_service_category = ServiceCategory.objects.all().filter(service_category_name = "Maintenance and Testing") [0]  

        a_service = Service(service_name = service[0],service_category = default_service_category)

        try:
            a_service.save()
        except IntegrityError as e:
            pass


    
    #filling order table
    order_info = pandas.DataFrame(spreadsheet_file, columns = ["Project #",
    "Order #","Order Name","Order Details","Order Created Date",
    "Order Target Completion Date","Order Completed Date","Order Planner",
    "Project Facility","Order Service","Order Model #","Order Serial #",
    "Order Customer PO#","Order Invoice #","Order Internal Notes",
    "Order Comments for Client","Order Current Status","Order Fee",
    "Order Name","Order Budget Labour Hours","Order Budget Material Expenses"])

    order_info = order_info.to_numpy().tolist()


    # if Order Planner is not defined assume Grant Erb
    try:
        default_order_planner = Staff.objects.get(staff_name = "Grant Erb")
    except ObjectDoesNotExist:
        default_order_planner = Staff(staff_name = "Grant Erb",staff_position_in_company = "Electrical Engineer",staff_start_date_in_company="2005-01-01",staff_category = "Technical",staff_hourly_salary = 25.0)
        default_order_planner.save()

    for order in order_info:

        the_order_project = Project.objects.all().filter(project_number = order[0]) [0]

        # separator = "-"
        # order[1] = order[1].split(separator,1)[1]

        # solving missing order_description
        if str(order[3]) == "nan":
            order[3] = ""

        # solving missing expected_order_completion_date
        if str(order[5]) == "NaT":
            order[5] = order[4] #asuming order creation date

        # solving missing order_planner
        if str(order[7]) == "nan":
            order[7] = default_order_planner
        else:
            order[7] = Staff.objects.all().filter(staff_name = order[7]) [0]

        # solving missing order facility
        if str(order[8]) == "nan":
            order[8] = None
        else:
            order[8] = ClientFacility.objects.all().filter(facility_name = order[8]).filter(client_name = Project.objects.all().filter(project_number = order[0])[0].client ) [0]
        
        # solving missing order service type
        if str(order[9]) == "nan":
            order[9] = None
        else:
            separator = "- "
            order[9] = order[9].split(separator,1)[1]
            order[9] = Service.objects.all().filter(service_name = order[9]) [0]

        a_order_times_reviewed = 0

        # solve missing order_model_number
        if str(order[10]) == "nan":
            order[10] = ""

        # solve missing order_serial_number
        if str(order[11]) == "nan":
            order[11] = ""

        # solve missing order_customer_PO
        if str(order[12]) == "nan":
            order[12] = ""       

        # solve missing order_invoice_number
        if str(order[13]) == "nan":
            order[13] = ""   

        # solve missing order_internal_notes
        if str(order[14]) == "nan":
            order[14] = ""

        # solve missing order_client_notes
        if str(order[15]) == "nan":
            order[15] = ""  

        # solve order_status
        if order[16] == "Opened":
            order[16] = "OP"
        elif order[16] == "Quoted":
            order[16] = "QU"
        elif order[16] == "PO Received":
            order[16] = "PO" 
        elif order[16] == "Design Approved":
            order[16] = "DA"
        elif order[16] == "Hold":
            order[16] = "HO"
        elif order[16] == "Assembly Complete":
            order[16] = "AC"
        elif order[16] == "Proceed with Invoices":
            order[16] = "PI"
        elif order[16] == "Product Shipped":
            order[16] = "PS"
        elif order[16] == "Report Sent":
            order[16] = "RS"
        elif order[16] == "Final Invoice Sent":
            order[16] = "FI"
        elif order[16] == "Complete":
            order[16] = "CP"
        elif order[16] == "Cancelled":
            order[16] = "CA"
        elif order[16] == "No Status":
            order[16] = "CA" # if Order Current Status == No Status, asume canceled


        # solving missing order_completion_date
        if str(order[6]) == "nan" and order[16] != "OP":
            order[6] = order[4] #assume closed the same date as opened
        else :
            order[6] = None


        # solve missing order_billing
        if str(order[17]) == "nan":
            order[17] = "FI" 
        elif order[17] == "Hourly":
            order[17] = "HO" 
        elif order[17] == "Fixed":
            order[17] = "FI"    

        # assuming default labor hour is charged @130 to the customer
        a_order_budget_total = Decimal(order[19]*130 + order[20])  
        a_order_budget_labor = Decimal(order[19]*130)

        a_order = Order(order_project = the_order_project,order_number = order[1],order_and_project_number = order[2],
        order_description = order[3],order_creation_date = order[4], expected_order_completion_date = order[5],
        order_completion_date = order[6],order_planner = order[7],order_service_type = order[9], 
        order_budget_total = a_order_budget_total,order_times_reviewed = a_order_times_reviewed,
        order_model_number = order[10],order_serial_number = order[11],order_customer_PO = order[12],
        order_invoice_number = order[13],order_internal_notes = order[14], order_client_notes = order[15],
        order_status = order[16],order_billing = order[17], order_name = order[18],order_budget_labor = a_order_budget_labor,
        order_budget_material = order[20])

        try:
            a_order.save()
            a_order.order_facility.set([order[8]]) 
        except IntegrityError as e:
            # print(e.__cause__)
            pass





def ExcelTimeSheetLoader():

    """
    ExcelTimeSheetLoader loads an existing Excel employee hours spreadsheet into the database.
    The format of this spreadsheet is specific for this example and should be modified to be
    used for any other Excel file format

    The path to the Excel file is hardcoded and some assumptions about default values for some fields have been made.
    This function should only be called once, while initially populating the database. 
    """


    spreadsheet_file = pandas.read_excel (r"C:\@Victor\Programming\Portfolio\2018.xlsx")

    #filling hours table

    hours_info = pandas.DataFrame(spreadsheet_file, columns = ["Date","Start Time","End Time","Time Codes","Project #","Order #","Description"])
    hours_info = hours_info.to_numpy().tolist()

    
    # time_sheet_owner is Victor
    try:
        default_time_sheet_owner = Staff.objects.get(staff_name = "Victor Mendez")
    except ObjectDoesNotExist:
        default_time_sheet_owner = Staff(staff_name = "Victor Mendez",staff_position_in_company = "Project Engineer - Electrical",staff_start_date_in_company="2018-09-15",staff_category = "Technical",staff_hourly_salary = 29.0)
        default_time_sheet_owner.save()


    for hours in hours_info:

        hours[5] = Order.objects.all().filter(order_project__project_number = hours[4]).filter(order_number = hours[5])[0]
        # hours[5] = Order.objects.all().filter(order_and_project_number = str(hours[4]) + "-" + str(hours[5]))[0]

        # solve missing task_time_code
        if str(hours[3]) == "nan":
            hours[3] = TimeCode.objects.all().filter(time_code_name = "Unclassified") [0] 
        else:
            hours[3] = TimeCode.objects.all().filter(time_code_name = hours[3]) [0]          

        # tz = timezone("America/Moncton")
        # start_day_time = pytz.utc.localize(datetime.combine(hours[0],hours[1]))
        # stop_day_time = pytz.utc.localize(datetime.combine(hours[0],hours[2]))
        start_day_time = datetime.combine(hours[0],hours[1])
        stop_day_time = datetime.combine(hours[0],hours[2])


        a_hour = StaffTimeSheet(time_sheet_owner = default_time_sheet_owner,task_belongs_to_order = hours[5],task_start_time = start_day_time,task_end_time = stop_day_time,task_time_code = hours[3], task_description = hours[6] )


        try:
            a_hour.save()
        except IntegrityError as e:
            # print(e.__cause__)
            pass





#TODO create feature: time delta between PO received time and 10% of work order budget is spent in labor (means the order has begun to be actively worked on)

def order_worked_stats(order_obj):

    """
    order_worked_stats calculates some basic stats about different employee contribution on a same work order
    """

    dict_order_hours_by_employee = {} 
    dict_order_hours_by_time_code = {} #TODO Use this dict for useful stats 
    for staff_time_sheet in order_obj.order_present_in_timesheet_of.all():
        dict_order_hours_by_employee[staff_time_sheet.time_sheet_owner.staff_name] = dict_order_hours_by_employee.get(staff_time_sheet.time_sheet_owner.staff_name,0) + staff_time_sheet.worked_hours_math()
        dict_order_hours_by_time_code[staff_time_sheet.task_time_code.time_code_name] = dict_order_hours_by_time_code.get(staff_time_sheet.task_time_code.time_code_name,0) + staff_time_sheet.worked_hours_math()

    dict_order_labor_cost_by_employee = {} 
    weighted_salary_x_hour = 25
    dict_order_hours_by_employee_at_weighted_salary_x_hour = {} # to store the equivalent hours worked by each employee if they were paid 25 x hour (if your salary is actually 50 x hour, each declared hour will count double)
    for employee in dict_order_hours_by_employee.keys():

        dict_order_labor_cost_by_employee[employee] =  Decimal(dict_order_hours_by_employee.get(employee,0)) * staff_time_sheet.time_sheet_owner.staff_hourly_salary.real 

        dict_order_hours_by_employee_at_weighted_salary_x_hour[employee] = Decimal(dict_order_hours_by_employee.get(employee,0)) * staff_time_sheet.time_sheet_owner.staff_hourly_salary.real/weighted_salary_x_hour


    to_return = ( round( sum(dict_order_hours_by_employee.values()) , 2 ), dict_order_hours_by_employee,
                round ( float( sum(dict_order_labor_cost_by_employee.values()) ) , 2 ), dict_order_labor_cost_by_employee,
                round( sum(dict_order_hours_by_employee_at_weighted_salary_x_hour.values()) , 2 ) , dict_order_hours_by_employee_at_weighted_salary_x_hour,
                dict_order_hours_by_time_code)    
    
    return to_return









#models created in models.py
my_models = [ClientIndustry] 
admin.site.register(my_models)



#to be able to modify the size of text elements in models displayed in the admin page Reference: https://docs.djangoproject.com/en/3.1/intro/tutorial07/
class ProjectModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size":"70"})},
        models.TextField: {"widget": Textarea(attrs={"rows":4, "cols":150})},
    }


    def date_project_created(self, project_obj):
        if project_obj.project_creation_date:
            return day_format_converter(project_obj.project_creation_date)

    list_display = ("project_number","client","project_name","date_project_created","project_planner","project_status")
    search_fields = ["project_number","client__client_name","project_name","project_creation_date"] 
    list_filter = ("project_planner__staff_name","project_status")
    ordering = ["project_number"]
    autocomplete_fields = ["client"]


    # ExcelProjectsLoader()
    # ExcelTimeSheetLoader()

admin.site.register(Project, ProjectModelAdmin)


class OrderMemberModelForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ["order_budget_total","order_budget_labor","order_budget_material","order_customer_PO","order_invoice_number"]
        widgets = {
            "order_project" : AutocompleteSelect(Order.order_project.field.remote_field,
            admin.site,attrs={'style': 'width: 500px'} ), 
            "order_name" : forms.Textarea(attrs={'rows':1, 'cols':80}),
            "order_description" : forms.Textarea(attrs={'rows':4, 'cols':150}),
            "order_facility" : AutocompleteSelectMultiple(Order.order_facility.field.remote_field,
            admin.site,attrs={'style': 'width: 500px'} ),
            "order_model_number" : forms.Textarea(attrs={'rows':1, 'cols':80}),
            "order_serial_number" : forms.Textarea(attrs={'rows':1, 'cols':80}),
            "order_customer_PO" : forms.Textarea(attrs={'rows':1, 'cols':80}),
            "order_invoice_number" : forms.Textarea(attrs={'rows':1, 'cols':80}),
            "order_internal_notes" : forms.Textarea(attrs={'rows':4, 'cols':150}),
            "order_client_notes" : forms.Textarea(attrs={'rows':4, 'cols':150}),
        }


class OrderAdminModelForm(forms.ModelForm):
    # order_facility = forms.ModelChoiceField(
    #              queryset= ClientFacility.objects.all(),
    #              widget=AutocompleteSelect(Order._meta.get_field("order_facility").remote_field, admin.site,attrs={'style': 'width: 500px'} ),
    #            )

    class Meta:
        model = Order
        fields = "__all__"
        widgets = {
            "order_project" : AutocompleteSelect(Order.order_project.field.remote_field,
            admin.site,attrs={'style': 'width: 500px'} ), 
            "order_name" : forms.Textarea(attrs={'rows':1, 'cols':80}),
            "order_description" : forms.Textarea(attrs={'rows':4, 'cols':150}),
            "order_facility" : AutocompleteSelectMultiple(Order.order_facility.field.remote_field,
            admin.site,attrs={'style': 'width: 500px'} ),
            "order_model_number" : forms.Textarea(attrs={'rows':1, 'cols':80}),
            "order_serial_number" : forms.Textarea(attrs={'rows':1, 'cols':80}),
            "order_customer_PO" : forms.Textarea(attrs={'rows':1, 'cols':80}),
            "order_invoice_number" : forms.Textarea(attrs={'rows':1, 'cols':80}),
            "order_internal_notes" : forms.Textarea(attrs={'rows':4, 'cols':150}),
            "order_client_notes" : forms.Textarea(attrs={'rows':4, 'cols':150}),
        }

    # TODO add possibility to filter on new Orders being created and not just on existing ones    

    def __init__(self, *args, **kwargs):
        super(OrderAdminModelForm, self).__init__(*args, **kwargs)


        if self.instance:
            try:
                self.fields["order_facility"].queryset = ClientFacility.objects.all().filter(client__exact = self.instance.order_project.client.id)
            except : #TODO find a way to filter new orders and update the displayed list based on changing the project (customer) in real time
                pass

          


class OrderModelAdmin(admin.ModelAdmin):
    # form = OrderModelForm

    # formfield_overrides = {
    #     models.CharField: {"widget": TextInput(attrs={"size":"75"})},
    #     models.TextField: {"widget": Textarea(attrs={"rows":4, "cols":150})},
    # }

    def project (self,order_obj):
        return "\n".join([str(order_obj.order_project.project_number)])

    def date_PO_received(self, order_obj):
        if order_obj.order_creation_date:
            return day_format_converter(order_obj.order_creation_date)

    def target_completion_date(self, order_obj):
        if order_obj.expected_order_completion_date:
            return day_format_converter(order_obj.expected_order_completion_date)

    def date_completed(self, order_obj):
        if order_obj.order_completion_date:
            return day_format_converter(order_obj.order_completion_date)

    def order_stats(self, order_obj):
        (order_consumed_hours,dict_order_hours_by_employee,
        order_labor_cost,dict_order_budget_by_employee,
        order_consumed_weighted_hours,dict_order_hours_by_employee_at_weighted_salary_x_hour,
        dict_order_hours_by_time_code) = order_worked_stats(order_obj)

        percentage_of_total_budget = 0
        if order_obj.order_budget_total != 0:
            percentage_of_total_budget = round ( order_labor_cost*100 / float(order_obj.order_budget_total) , 2) 

        percentage_of_labor_budget = 0
        if order_obj.order_budget_labor != 0:
            percentage_of_labor_budget = round ( order_labor_cost*100 / float(order_obj.order_budget_labor) , 2) 
        
        to_return = (
                    "Time (h) = " + str(order_consumed_hours) 
                    + ". Weigted time at 25 x hour (h) = " + str(order_consumed_weighted_hours) 
                    + ". Labor cost (CAD) = " + str(order_labor_cost) 
                    + ". Percentage of total budget (%) = " + str(percentage_of_total_budget) 
                    + ". Percentage of labor budget (%) = " + str(percentage_of_labor_budget)
                    )
        # + ". Hours by time code = " + str(dict_order_hours_by_time_code)


        return to_return


    # do not show certain fields for normal users
    def get_form(self, request, *args, **kwargs):
        # form = super(OrderModelAdmin, self).get_form(request, *args, **kwargs)
        #TODO Create these groups with Code and not through Django
        if request.user.groups.filter(name="Administration").exists():

            return OrderAdminModelForm        

        elif request.user.groups.filter(name="Member").exists():

            return OrderMemberModelForm

        # if no user role has been defined assume Admin
        elif not request.user.groups.all().exists():

            return OrderAdminModelForm
        
    #TODO find a way to produce the same result on OrderAdminModelForm
    # fields = ["order_project",("order_number","order_name"),"order_description",
    #         ("order_creation_date","expected_order_completion_date","order_completion_date"),
    #         ("order_planner","order_status","order_billing"),"order_facility",
    #         ("order_budget_total","order_budget_labor","order_budget_material"),
    #         ("order_service_type","order_times_reviewed"),
    #         ("order_model_number","order_serial_number"),
    #         ("order_customer_PO","order_invoice_number"),
    #         "order_internal_notes","order_client_notes"]


    list_display = ("project","order_number","order_name","date_PO_received",
                    "target_completion_date","order_status","date_completed","order_stats")

    search_fields = ["order_and_project_number","order_project__project_number","order_name",
                    "order_creation_date","order_planner__staff_name","order_facility__facility_name"] 
    
    list_filter = ("order_status",)
    ordering = ["order_project"]
    # filter_horizontal = ("order_facility",) #filter_vertical
    # autocomplete_fields = ["order_project","order_facility"]



admin.site.register(Order, OrderModelAdmin)



class ClientAccountModelAdmin(admin.ModelAdmin):

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size":"70"})},
    }

    list_display = ("client_name","account_user_name","account_email","account_phone")
    autocomplete_fields = ["client_name"]

    #https://stackoverflow.com/questions/11754877/troubleshooting-related-field-has-invalid-lookup-icontains
    search_fields = ["client_name__client_name","account_user_name","account_email","account_phone"]

admin.site.register(ClientAccount, ClientAccountModelAdmin)   




class ClientDepartmentModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size":"70"})},
    }

    list_display = ("client_name","client_department_name")
    autocomplete_fields = ["client_name"]

admin.site.register(ClientDepartment, ClientDepartmentModelAdmin)


class ClientFacilityModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size":"70"})},
    }

    list_display = ("client_name","facility_name")
    search_fields = ["client_name__client_name","facility_name"]
    ordering = ["facility_name"]
    autocomplete_fields = ["client_name"]

admin.site.register(ClientFacility, ClientFacilityModelAdmin)



class ClientModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size":"50"})},
    }

    search_fields = ["client_name"]
    list_display = ("client_name","client_industry")
    list_filter = ("client_industry",)
    ordering = ["client_name"]

admin.site.register(Client, ClientModelAdmin)


class ServiceModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size":"50"})},
    }

    list_display = ("service_name","service_category")


admin.site.register(Service, ServiceModelAdmin)



class ServiceCategoryModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size":"50"})},
    }

    ordering = ["service_category_name"]


admin.site.register(ServiceCategory, ServiceCategoryModelAdmin)


# class StaffTimeSheetInline(admin.TabularInline):
#     model = StaffTimeSheet
#     # extra = 2


class StaffTimeSheetModelForm(forms.ModelForm):
    
    task_description = forms.CharField(required=False, widget=forms.Textarea(attrs={"class":"form-control","rows":4,"cols":150,"placeholder":"task description"}))

    class Meta:
        model = StaffTimeSheet
        fields = "__all__"
        widgets = {
            "task_belongs_to_order": AutocompleteSelect(StaffTimeSheet.task_belongs_to_order.field.remote_field,
            admin.site,attrs={'style': 'width: 500px'} ),             
        }


    def __init__(self, *args,**kwargs):
        super (StaffTimeSheetModelForm,self).__init__(*args,**kwargs)
        #retrieve current_user from ModelAdmin
        self.fields['time_sheet_owner'].queryset = Staff.objects.all().filter(staff_name__contains = self.current_user)

    # title = forms.CharField(max_length=50)
    # spreadsheet_file = forms.FileField(label="Select an excel spreadsheet",help_text="It must have the format of PPI timesheet")




class StaffTimeSheetModelAdmin(admin.ModelAdmin):
    form = StaffTimeSheetModelForm

    def get_form(self, request, *args, **kwargs):
        form = super(StaffTimeSheetModelAdmin, self).get_form(request, *args, **kwargs)
        form.current_user = request.user #get current user only accessible in ModelAdmin and pass it to ModelForm
        return form

    def get_queryset(self, request):
        qs = super(StaffTimeSheetModelAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            if qs.exists() :
                return qs.filter(time_sheet_owner= Staff.objects.all().filter(staff_name__contains = request.user)[0] )
            else:
                return qs
        else:
            return qs


    # #determines size of input text box (not working if form is declared independently)
    # formfield_overrides = {
    #     models.CharField: {"widget": TextInput(attrs={"size":"50"})},
    #     models.TextField: {"widget": Textarea(attrs={"rows":4, "cols":100})},
    # }

    # fields = ["time_sheet_owner","task_date","task_belongs_to_order","task_start_time","task_end_time","service_category","task_description"]

    def project_order (self,staff_time_sheet_obj):
        #in case task_belongs_to_order was of a many to many filed type
        #return "\n".join([str(order.order_project.project_number) + "-" + str(order.order_number) for order in staff_time_sheet_obj.task_belongs_to_order.all()])

        return "\n".join([str(staff_time_sheet_obj.task_belongs_to_order.order_project.project_number) + "-" + str(staff_time_sheet_obj.task_belongs_to_order.order_number) ])

    def start_time(self, staff_time_sheet_obj):
      if staff_time_sheet_obj.task_start_time:
        return day_hour_format_converter(staff_time_sheet_obj.task_start_time)

    def end_time(self, staff_time_sheet_obj):
      if staff_time_sheet_obj.task_end_time:
        return day_hour_format_converter(staff_time_sheet_obj.task_end_time)


    list_display = ("time_sheet_owner","project_order","start_time",
                    "end_time","worked_hours","task_time_code","task_description")
    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.search_fields
    # https://docs.djangoproject.com/en/3.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_search_results

    #removed task_start_time to avoid cluttering search results
    search_fields = ["task_belongs_to_order__order_and_project_number",
                    "task_description","task_belongs_to_order__order_number",
                    "task_belongs_to_order__order_project__project_number"] 
    
    list_filter = ("time_sheet_owner","task_start_time")
    ordering = ["-task_start_time"]
    # autocomplete_fields = ["task_belongs_to_order"]


    

admin.site.register(StaffTimeSheet, StaffTimeSheetModelAdmin)


class StaffModelAdmin(admin.ModelAdmin):

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size":"70"})},
        models.TextField: {"widget": Textarea(attrs={"rows":4, "cols":100})},
    }

    list_display = ("staff_name","staff_category","staff_position_in_company","staff_hourly_salary")
    search_fields = ["staff_name","staff_category"]
    list_filter = ("staff_category",)
    ordering = ["staff_name"]

admin.site.register(Staff, StaffModelAdmin) 



class StaffCategoryModelAdmin(admin.ModelAdmin):

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size":"70"})},
    }

    list_display = ("staff_category_name",)
    ordering = ["staff_category_name"]

admin.site.register(StaffCategory, StaffCategoryModelAdmin) 





class TimeCodeModelAdmin(admin.ModelAdmin):

    #determines size of input text box
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size":"50"})},
        models.TextField: {"widget": Textarea(attrs={"rows":4, "cols":150})},
    }
 
    list_display = ("time_code_name","time_code_description")
    ordering = ["time_code_name"]

admin.site.register(TimeCode, TimeCodeModelAdmin)