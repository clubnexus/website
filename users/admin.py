from django.contrib import admin

from models import UserExt
from models import TTEvent

admin.site.register(UserExt)
admin.site.register(TTEvent)
