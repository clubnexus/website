from django.contrib import admin

from models import NewsPost
from models import NewsComment

admin.site.register(NewsPost)
admin.site.register(NewsComment)
