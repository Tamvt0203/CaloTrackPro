from django.contrib import admin

from .models import User, Food, CaloHistory, FoodUser, WeightHistory
# Register your models here.
admin.site.register(User)
admin.site.register(Food)
admin.site.register(CaloHistory)
admin.site.register(FoodUser)
admin.site.register(WeightHistory)