from django.contrib.auth.models import User
from django.core.signing import dumps, loads
from django.db import models
import string, os

ALLOWED_CHARS = string.ascii_lowercase + string.ascii_uppercase + ''.join([`x` for x in xrange(10)]) + '.-_'

class UserExt(models.Model):
    user = models.CharField(max_length=128)
    
    email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=64)
    
    banned = models.BooleanField(default=False)
    ban_history = models.CharField(max_length=20 * 1024)
    
    email_reset_token = models.CharField(max_length=32)
    
    def get_user(self):
        try:
            user = User.objects.get(pk=self.user)
        
        except User.DoesNotExist:
            user = None
            
        return user
    
    @staticmethod
    def validate_username(username):
        if len(username) < 6:
            return 'Username too short (min. 6 characters)'
            
        if len(username) > 20:
            return 'Username too long (max. 20 characters)'
        
        for c in username:
            if c not in ALLOWED_CHARS:
                return 'Invalid caracther %s. Your username may contain only these: %s' % (c, ALLOWED_CHARS)
            
        return ''
        
    @staticmethod
    def validate_password(password):
        if len(password) < 6:
            return 'Password too short (min. 6 characters)'
            
        if len(password) > 32:
            return 'Password too long (max. 32 characters)'
        
        elif password == 'correcthorsebatterystaple':
            return 'u w0t m8'
        
        return ''
       
    def gen_reset_token(self):
        user = self.get_user()
        if not user:
            return ''
            
        self.email_reset_token = os.urandom(16).encode('hex') 
        self.save()
        
        return dumps({'token': self.email_reset_token,
                      'username': self.get_user().username}, compress=True).encode('hex') 
    
    @classmethod
    def check_reset_token(cls, token):
        try:
            # Token is valid for only 36 hours
            token = loads(token.decode('hex'), max_age=60 * 60 * 24 * 1.5)
            
        except:
            return (None, None)
            
        try:
            userext = cls.objects.get(email_reset_token=token['token'])
            if userext.get_user().username != token['username']:
                return (None, None)
            
        except:
            return (None, None)
        
        return (userext.get_user(), userext)
        
    def __unicode__(self):
        user = self.get_user()
        if not user:
            return 'Unknown user'
            
        return user.username
        
class TTEvent(models.Model):
    event_type = models.CharField(max_length=60)
    event_date = models.DateTimeField()
    event_account = models.CharField(max_length=128)
    
    # N.B. For desc and ip, we have public and private fields
    # Public fields are visible in the UCP to the user
    # Private fields are visible only to the devs (via direct db access)
    # This is useful, for example, when storing banners
    event_desc_pub = models.TextField(max_length=500)
    event_desc_priv = models.TextField(max_length=500)
    event_ip_pub = models.CharField(max_length=40)
    event_ip_priv = models.CharField(max_length=40)
    
    def __unicode__(self):
        try:
            user = User.objects.get(pk=self.event_account)
        
        except User.DoesNotExist:
            user = 'Unknown user'
        
        return '%s (%s/%d, %s, %s, %s)' % (self.event_type, user, self.event_account, self.event_date,
                                           self.event_ip_pub, self.event_desc_pub)
        