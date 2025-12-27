from django.contrib import admin
from .models import IrisObservation, Garden

@admin.register(IrisObservation)
class IrisObservationAdmin(admin.ModelAdmin):
    list_display = ('species', 'sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'garden')
    list_filter = ('species', 'garden')
    search_fields = ('species', 'garden__name')
    list_per_page = 20  # Sayfalama özelliği

@admin.register(Garden)
class GardenAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity')
    search_fields = ('name', 'location')
