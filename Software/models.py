from django.db import models
from django.contrib.auth.models import User
import random


class Voter(models.Model):
    NIC_Number = models.BigIntegerField(primary_key=True)
    First_Name = models.CharField(max_length=20)
    Last_Name = models.CharField(max_length=20)
    Middle_Name = models.CharField(max_length=20)
    Phone_Number = models.IntegerField(unique=True)
    Address = models.CharField(max_length=50)
    Email = models.EmailField(max_length=150,unique=True)
    User_Name = models.CharField(max_length=20, unique=True)
    Password = models.CharField(max_length=16, unique=True)
    OTP_Count = models.IntegerField(default=1)


    class Meta:
        db_table = 'details_of_voters'
    # def __str__(self):
    #     return self.user_name

class Admin(models.Model):
    Admin_ID = models.AutoField(primary_key=True)  
    Admin_name = models.CharField(max_length=50, unique=True, null=False)  
    Admin_password = models.CharField(max_length=60) 

    class Meta:
        db_table = 'admin_table'

    def __str__(self):
        return self.Admin_name
    
class Party(models.Model):
    Party_ID = models.AutoField(primary_key=True)
    Party_Name = models.CharField(unique=True,max_length=80)
    Party_Logo = models.ImageField(upload_to='media')
    Party_Color = models.CharField(max_length=7)

    class Meta:
        db_table = 'political_party'

    # def __str__(self):
    #     return self.Party_Name

class Elec_Name(models.Model):
    Election_ID = models.AutoField(primary_key=True)
    Election_Name = models.CharField(unique=True,max_length=80)
    Election_Year = models.IntegerField(unique=True)
    Election_Month = models.CharField(max_length=12)

    class Meta:
        db_table = 'Election_Name'
    def __str__(self):
        return f"{self.Election_Name} ({self.Election_Year})"

class Elec_Results(models.Model):
    Vote_ID = models.AutoField(primary_key=True)
    Political_Party = models.CharField(null=True,max_length=80)
    First_Vote = models.IntegerField(null=True)
    Second_Vote = models.IntegerField(null=True)
    Third_Vote = models.IntegerField(null=True)

    class Meta:
        db_table = 'election_results'