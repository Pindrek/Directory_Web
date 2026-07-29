from cProfile import Profile

from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Directory)
admin.site.register(File)