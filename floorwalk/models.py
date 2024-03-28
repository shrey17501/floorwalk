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
    phone = models.CharField(max_length=15, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    lat = models.CharField(max_length=30)
    lon = models.CharField(max_length=30)
    pincode = models.CharField(max_length=30)
    operating_time = models.CharField(max_length=300, null=True)

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
    

class Top_five_populated_cities_of_each_state(models.Model):
    state_name = models.CharField(max_length=100, null=True)
    state = models.BigIntegerField()
    level = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=100, null=True)
    tru = models.CharField(max_length=100, null=True)
    total_population = models.BigIntegerField()
    total_males = models.BigIntegerField()
    total_female = models.BigIntegerField()

    def __str__(self):
        return self.state

class State_census(models.Model):
    state = models.BigIntegerField()
    state_name = models.CharField(max_length=100, null=True)
    level = models.CharField(max_length=100, null=True)
    tru = models.CharField(max_length=100, null=True)
    total_population = models.BigIntegerField()
    total_males = models.BigIntegerField()
    total_female = models.BigIntegerField()

    def __str__(self):
        return self.state

class Apparel(models.Model):
    brand_name = models.CharField(max_length=100, null=True)
    store_name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=500, null=True)
    phone = models.CharField(max_length=30, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    lat = models.CharField(max_length=30, null=True)
    lon = models.CharField(max_length=30, null=True)
    pincode = models.CharField(max_length=10, null=True)
    star_count = models.CharField(max_length=10, null=True)
    rating_count = models.CharField(max_length=10, null=True)
    email = models.CharField(max_length=150, null=True)
    url = models.CharField(max_length=200, null=True)
    primary_category_name = models.CharField(max_length=50, null=True)
    category_name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.brand_name

class Census(models.Model):
    id = models.BigAutoField(primary_key=True)
    state = models.BigIntegerField()
    District = models.BigIntegerField()
    Subdistt = models.BigIntegerField()
    Town_Village = models.BigIntegerField()
    Ward = models.BigIntegerField()
    EB = models.BigIntegerField()
    Level = models.CharField(max_length=100, null=True)
    Name = models.CharField(max_length=100, null=True)
    TRU = models.CharField(max_length=100, null=True)
    Total_Family = models.BigIntegerField()
    Total_Population = models.BigIntegerField()
    Total_Males = models.BigIntegerField()
    Total_Female = models.BigIntegerField()
    Children_0to6_years = models.BigIntegerField()
    male_children = models.BigIntegerField()
    female_children = models.BigIntegerField()
    Scheduled_Caste = models.BigIntegerField()
    Scheduled_Caste_Male = models.BigIntegerField()
    Scheduled_Caste_Female = models.BigIntegerField()
    Schedule_Tribe = models.BigIntegerField()
    Schedule_Tribe_Male = models.BigIntegerField()
    Schedule_Tribe_Female = models.BigIntegerField()
    Total_literates = models.BigIntegerField()
    Male_literates = models.BigIntegerField()
    Female_literates = models.BigIntegerField()
    Illiterate = models.BigIntegerField()
    Male_Illiterate = models.BigIntegerField()
    Female_Illiterate = models.BigIntegerField()
    Total_Working_Population = models.BigIntegerField()
    Total_Working_Population_Male = models.BigIntegerField()
    Total_Working_Population_Female = models.BigIntegerField()
    Total_Main_Workers_Population = models.BigIntegerField()
    Male_Main_Workers_Population = models.BigIntegerField()
    Female_Main_Workers_Population = models.BigIntegerField()
    Cultivators = models.BigIntegerField()
    Male_Cultivators = models.BigIntegerField()
    Female_Cultivators = models.BigIntegerField()
    Agriculture_Labourer = models.BigIntegerField()
    Male_Agriculture_Labourer = models.BigIntegerField()
    Famale_Agriculture_Labourer = models.BigIntegerField()
    Household_Industries = models.BigIntegerField()
    Male_Household_Industries = models.BigIntegerField()
    Female_Household_Industries = models.BigIntegerField()
    Other_Workers = models.BigIntegerField()
    Male_Other_Workers = models.BigIntegerField()
    Female_Other_Workers = models.BigIntegerField()
    Marginal_Workers = models.BigIntegerField()
    Male_Marginal_Workers = models.BigIntegerField()
    Female_Marginal_Workers = models.BigIntegerField()
    Marginal_Cultivator_Population_Person = models.BigIntegerField()
    Marginal_Cultivator_Population_Male = models.BigIntegerField()
    Marginal_Cultivator_Population_Female = models.BigIntegerField()
    Marginal_Agriculture_Labourers_Population_Person = models.BigIntegerField()
    Marginal_Agriculture_Labourers_Population_Male = models.BigIntegerField()
    Marginal_Agriculture_Labourers_Population_Female = models.BigIntegerField()
    Marginal_Household_Industries_Population_Person = models.BigIntegerField()
    Marginal_Household_Industries_Population_Male = models.BigIntegerField()
    Marginal_Household_Industries_Population_Female = models.BigIntegerField()
    Marginal_Other_Workers_Population_Person = models.BigIntegerField()
    Marginal_Other_Workers_Population_Male = models.BigIntegerField()
    Marginal_Other_Workers_Population_Female = models.BigIntegerField()
    Marginal_Worker_Population_3to6_Person = models.BigIntegerField()
    Marginal_Worker_Population_3to6_Male = models.BigIntegerField()
    Marginal_Worker_Population_3to6_Female = models.BigIntegerField()
    Marginal_Cultivator_Population_3to6_Person = models.BigIntegerField()
    Marginal_Cultivator_Population_3to6_Male = models.BigIntegerField()
    Margina_Cultivator_Population_3to6_Female = models.BigIntegerField()
    Marginal_Agriculture_Labourers_Population_3to6_Person = models.BigIntegerField()
    Marginal_Agriculture_Labourers_Population_3to6_Male = models.BigIntegerField()
    Marginal_Agriculture_Labourers_Population_3to6_Female = models.BigIntegerField()
    Marginal_Household_Industries_Population_3to6_Person = models.BigIntegerField()
    Marginal_Household_Industries_Population_3to6_Male = models.BigIntegerField()
    Marginal_Household_Industries_Population_3to6_Female = models.BigIntegerField()
    Marginal_Other_Workers_Population_Person_3to6_Person = models.BigIntegerField()
    Marginal_Other_Workers_Population_Person_3to6_Male = models.BigIntegerField()
    Marginal_Other_Workers_Population_Person_3to6_Female = models.BigIntegerField()
    Marginal_Worker_Population_0to3_Person = models.BigIntegerField()
    Marginal_Worker_Population_0to3_Male = models.BigIntegerField()
    Marginal_Worker_Population_0to3_Female = models.BigIntegerField()
    Marginal_Cultivator_Population_0to3_Person = models.BigIntegerField()
    Marginal_Cultivator_Population_0to3_Male = models.BigIntegerField()
    Marginal_Cultivator_Population_0to3_Female = models.BigIntegerField()
    Marginal_Agriculture_Labourers_Population_0to3_Person = models.BigIntegerField()
    Marginal_Agriculture_Labourers_Population_0to3_Male = models.BigIntegerField()
    Marginal_Agriculture_Labourers_Population_0to3_Female = models.BigIntegerField()
    Marginal_Household_Industries_Population_0to3_Person = models.BigIntegerField()
    Marginal_Household_Industries_Population_0to3_Male = models.BigIntegerField()
    Marginal_Household_Industries_Population_0to3_Female = models.BigIntegerField()
    Marginal_Other_Workers_Population_0to3_Person = models.BigIntegerField()
    Marginal_Other_Workers_Population_0to3_Male = models.BigIntegerField()
    Marginal_Other_Workers_Population_0to3_Female = models.BigIntegerField()
    Non_Working_Population_Person = models.BigIntegerField()
    Non_Working_Population_Male = models.BigIntegerField()
    Non_Working_Population_Female = models.BigIntegerField()

    def __str__(self):
        return self.TRU
    


