from django.contrib.auth.models import User
from users.models import UserExt
from django.db import models

class PlayCookie(models.Model):
    username = models.CharField(max_length=200)
    used = models.BooleanField(default=False)
    
    def use(self):
        if self.used:
            return None
            
        try:
            user = User.objects.get(pk=self.username)
            userext = UserExt.objects.get(user=user.id)
        
        except (User.DoesNotExist, UserExt.DoesNotExist):
            return None
            
        # TO DO
        #if userext.is_banned():
        #    return None
            
        self.used = True
        self.save()
        return self.username
        