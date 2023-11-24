from django.contrib import admin
from .models import Category, Note, Comments

# Register your models here.

admin.site.register(Category)
admin.site.register(Note)
admin.site.register(Comments)
