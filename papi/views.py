from django.contrib.auth import authenticate

from users.models import UserExt
from users import events

def TT_login(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    # TO DO
    