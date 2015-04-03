from django.contrib.auth.models import User
from django.core.signing import dumps, loads
from django.db import models
import string, os, struct, time, datetime

ALLOWED_CHARS = string.ascii_lowercase + string.ascii_uppercase + ''.join([`x` for x in xrange(10)]) + '.-_'

class BanRecord:
    class BanEntry:
        start = 0
        duration = 0
        banner = ''
        reason = ''
        
        def still_in_effect(self):
            if self.duration == 1:
                return True
                
            end = self.start + self.duration * 3600
            return end > time.time()
            
        def as_html(self):
            sdt = datetime.datetime.fromtimestamp(self.start).strftime('%B %d, %Y, %I:%M %p')
            dur = '%d hours' % self.duration if self.duration > 1 else '<b><i>account terminated</i></b>'
            return '<p>Start date: %s</p><p>Duration: %s</p></p>Reason: %s</p>' % (sdt, dur, self.reason)
            
        def as_td(self):
            sdt = datetime.datetime.fromtimestamp(self.start).strftime('%B %d, %Y, %I:%M %p')
            dur = '%d hours' % self.duration if self.duration > 1 else '<b><i>account terminated</i></b>'
            return '<td>%s</td><td>%s</td><td>%s</td>' % (sdt, dur, self.reason)
            
        def __str__(self):
            sdt = datetime.datetime.fromtimestamp(self.start).strftime('%B %d, %Y, %I:%M %p')
            dur = self.duration if self.duration > 1 else 'ACCOUNT TERMINATED'
            return 'start: %s; duration (in hours): %s; reason: %s' % (sdt, dur, self.reason)
        
    def __init__(self, data):
        self.make_from_net_string(data)
        
    def make_from_net_string(self, data):
        self.entries = []
        
        if not data:
            return
            
        data = data.decode('hex')
            
        numEntries = ord(data[0])
        data = data[1:]
        
        for i in xrange(numEntries):
            start, duration = struct.unpack('<II', data[:8])
            data = data[8:]
            
            bs, = struct.unpack('<H', data[:2])
            banner = data[2:2+bs]
            data = data[2+bs:]
            
            rs, = struct.unpack('<H', data[:2])
            reason = data[2:2+rs]
            data = data[2+rs:]
            
            entry = BanRecord.BanEntry()
            entry.start = start
            entry.duration = duration
            entry.banner = banner
            entry.reason = reason
            self.entries.append(entry)
            
    def make_net_string(self):
        data = ''
        data += chr(len(self.entries))
        for entry in self.entries:
            data += struct.pack('<II', entry.start, entry.duration)
            data += struct.pack('<H', len(entry.banner)) + entry.banner
            data += struct.pack('<H', len(entry.reason)) + entry.reason
            
        return data.encode('hex')

    def is_banned(self):
        if not self.entries:
            return False
            
        return self.entries[-1].still_in_effect()
        
class UserExt(models.Model):
    user = models.CharField(max_length=128)
    
    email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=64)

    ban_history = models.CharField(max_length=20 * 1024)
    
    email_reset_token = models.CharField(max_length=33)
    
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
            
        data = struct.pack('<I', int(time.time()))
        data += os.urandom(12)
        self.email_reset_token = data.encode('hex') + '0'
        self.save()
        
        return self.email_reset_token[:32]
                      
    def is_token_valid(self):
        if len(self.email_reset_token) < 4:
            if self.email_reset_token:
                self.email_reset_token = ''
                self.save()
            return 0
            
        max_age = 60 * 60 * 24 * 2 # 48 hours
        
        valid = time.time() < struct.unpack('<I', self.email_reset_token[:4])[0] + max_age
        if not valid:
            self.email_reset_token = ''
            self.save()
        
        return valid

    @classmethod
    def check_reset_token(cls, token):
        try:
            userext = cls.objects.get(email_reset_token=token + '1')
            if not userext.is_token_valid():
                return (None, None)
            
        except:
            return (None, None)
        
        return (userext.get_user(), userext)
        
    def is_banned(self):
        return BanRecord(self.ban_history).is_banned()
        
    def add_ban(self, banner, duration, reason):
        record = BanRecord(self.ban_history)
        
        entry = BanRecord.BanEntry()
        entry.banner = banner
        entry.duration = duration
        entry.reason = reason
        entry.start = int(time.time())
        
        record.entries.append(entry)
        self.ban_history = record.make_net_string()
        self.save()
        
    def get_last_ban(self):
        record = BanRecord(self.ban_history)
        if not record.entries:
            return 'No ban entry found!'
            
        return record.entries[-1].as_html()
        
    def get_ban_history(self):
        record = BanRecord(self.ban_history)
        d = '<tr><td>Start date</td><td>Duration</td><td>Reason</td></tr>'
        for entry in record.entries[::-1]:
            d += '<tr>%s</tr>' % entry.as_td()
            
        return d
        
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
        