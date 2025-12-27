from django.db import models

# İkinci Model: Iris çiçeklerinin bulunduğu bölgeyi/bahçeyi temsil eder.
class Garden(models.Model):
    name = models.CharField(max_length=100) # 1. Alan
    location = models.CharField(max_length=200) # 2. Alan
    established_date = models.DateField() # 3. Alan
    capacity = models.IntegerField() # 4. Alan
    contact_email = models.EmailField() # 5. Alan

    def __str__(self):
        return self.name

# Ana Model: Iris veri setindeki fiziksel ölçümleri tutar.
class IrisObservation(models.Model):
    # İlişki: Her gözlem bir bahçeye aittir (Many-to-One)
    garden = models.ForeignKey(Garden, on_delete=models.CASCADE) # İlişki şartı 
    
    sepal_length = models.FloatField() # 1. Alan 
    sepal_width = models.FloatField()  # 2. Alan 
    petal_length = models.FloatField() # 3. Alan 
    petal_width = models.FloatField()  # 4. Alan 
    species = models.CharField(max_length=50) # 5. Alan 

    def __str__(self):
        return f"{self.species} - {self.id}"
