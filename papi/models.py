from django.contrib.auth.models import User
from users.models import UserExt
from django.db import models

STATUS_PEN = 0
STATUS_REJ = 1
STATUS_APR = 2

class PlayCookie(models.Model):
    username = models.CharField(max_length=200)
    used = models.BooleanField(default=False)
    value = models.CharField(max_length=32)
    
    def use(self):
        if self.used:
            return None
            
        try:
            user = User.objects.get(username=self.username)
            userext = UserExt.objects.get(user=user.id)
        
        except (User.DoesNotExist, UserExt.DoesNotExist):
            return None

        if userext.is_banned():
            return None
            
        self.used = True
        self.save()
        return self.username
        
class NameState(models.Model):
    username = models.CharField(max_length=200)
    wantedName = models.CharField(max_length=200)
    avId = models.IntegerField()
    status = models.IntegerField(default=STATUS_PEN)
    mod = models.CharField(max_length=200)
    date = models.DateTimeField()
    
class Gameserver(models.Model):
    name = models.CharField(max_length=200)
    open = models.BooleanField(default=False)
    