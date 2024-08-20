from django.contrib import admin

# Register your models here.
from .models import Choice, Person, Question

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Person)
