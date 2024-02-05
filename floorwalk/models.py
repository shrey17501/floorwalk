from django.db import models

# Create your models here.
class Automobile(models.Model):
    brand_name = models.CharField(max_length=100, null=True)
    store_name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=500, null=True)
    phone = models.CharField(max_length=30, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    lat = models.CharField(max_length=30, null=True)
    lon = models.CharField(max_length=30, null=True)
    pincode = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.brand_name
    
class Electronic(models.Model):
    brand_name = models.CharField(max_length=50, null=True)
    store_name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=600, null=True)
    phone = models.CharField(max_length=300, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    lat = models.CharField(max_length=30, null=True)
    lon = models.CharField(max_length=30, null=True)
    pincode = models.CharField(max_length=20, null=True)
    type = models.CharField(max_length=50, null=True)
    operating_time = models.CharField(max_length=400, null=True)
    brand_logo = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.brand
    
class Entertainment(models.Model):
    brand_name = models.CharField(max_length=50)
    store_name = models.CharField(max_length=200)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    lat = models.CharField(max_length=30)
    lon = models.CharField(max_length=30)
    pincode = models.CharField(max_length=15)

    def __str__(self):
        return self.brand_name
    
class Supermarket(models.Model):
    brand_name = models.CharField(max_length=30)
    store_name = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    lat = models.CharField(max_length=30)
    lon = models.CharField(max_length=30)
    pincode = models.CharField(max_length=30)

    def __str__(self):
        return self.store_name
    
class Telecom(models.Model):
    brand_name = models.CharField(max_length=100, null=True)
    store_name = models.CharField(max_length=300, null=True)
    address = models.CharField(max_length=400, null=True)
    phone = models.CharField(max_length=15, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    lat = models.CharField(max_length=30, null=True)
    lon = models.CharField(max_length=30, null=True)
    pincode = models.CharField(max_length=10, null=True)
    store_type = models.CharField(max_length=250, null=True)
    operating_time = models.CharField(max_length=300, null=True)

    def __str__(self):
        return self.brand_name