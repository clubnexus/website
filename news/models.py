from django.templatetags.static import static
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

COMMENT_STATE_NOT_FOUND = -1
COMMENT_STATE_PEN = 0
COMMENT_STATE_REJ = 1
COMMENT_STATE_APR = 2

IMAGE_NONE = 0
IMAGE_COG = 1
IMAGE_TOON = 2

COG_ICONS = {
    # TO DO: COMPLETE
    
    # Bossbots
    # 0: '', # flunky
    # 1: '', # pencil
    # 2: '', # yesman
    # 3: '', # micromanager
    # 4: '', # downsizer
    # 5: '', # hunter
    # 6: '', # raider
    # 7: '', # cheese
    
    # Lawbots
    # 8: '', # bottom feeder
    # 9: '', # bloodsucker
    # 10: '', # double talker
    # 11: '', # chaser
    12: 'backstabber', # back stabber
    # 13: '', # spin doctor
    14: 'legal-eagle', # legal eagle
    # 15: '', # big wig
    
    # Cashbots
    # 16: '', # short change
    # 17: '', # pincher
    # 18: '', # tightwad
    # 19: '', # counter
    # 20: '', # cruncher
    # 21: '', # money bags
    # 22: '', # shark
    # 23: '', # baron

    # Sellbots
    # 24: '', # cold caller
    # 25: '', # telemarketer
    # 26: '', # dropper
    27: 'glad-hander', # hander
    # 28: '', # mover shaker
    # 29: '', # two face
    # 30: '', # mingler
    31: 'hollywood', # hollywood
}

def encode_image(high, low):
    return high << 6 | low
    
def decode_image_raw(code):
    return code >> 6, code & 64

def decode_image(code):
    high, low = decode_image_raw(code)
    if high == IMAGE_NONE:
        return ''
        
    if high == IMAGE_TOON:
        return 'flippy'
        
    # Cog icon
    return COG_ICONS.get(low, 'legal-eagle')
 
def get_icons():
    res = {
        'none': encode_image(IMAGE_NONE, 0),
        'flippy': encode_image(IMAGE_TOON, 0)
    }
    
    for value, name in COG_ICONS.items():
        res[name] = encode_image(IMAGE_COG, value)
        
    return res

class NewsPost(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    post = models.TextField()
    pic = models.FileField(upload_to=settings.POST_PIC_UPLOAD_DIR)
    date = models.DateTimeField()
    
    def __init__(self, *args, **kw):
        models.Model.__init__(self, *args, **kw)
        
        if self.id:
            self.comments = NewsComment.objects.filter(post=self.id, approved=COMMENT_STATE_APR).order_by('-date')
            self.commentinfo = '%s comment%s'
            if len(self.comments) >= 1:
                self.commentinfo %= (len(self.comments), 's' if len(self.comments) > 1 else '')
                self.comments[len(self.comments) - 1].last = 1
                
            else:
                self.commentinfo %= ('No', 's')
                
            for comment in self.comments:
                comment.style = 'user'
                if comment.is_staff():
                    comment.style += 'staff'
                    
                comment.tp = 1
                    
                high, low = decode_image_raw(comment.image)
                if high != IMAGE_NONE:
                    comment.img = static('img/posts/icons/%s-icon.jpg' % decode_image(comment.image))
                    
                else:
                    comment.img = ''
                    
                if high == IMAGE_COG:
                    comment.authorname = 'The COGs'
                    comment.style += '_cog'
                    comment.tp = 0
                    
                elif high == IMAGE_TOON:
                    comment.authorname = 'Toon Council'
       
    def user_comment_status(self, user):
        comments = NewsComment.objects.filter(post=self, author=user.id).order_by('-date')
        if not comments:
            return COMMENT_STATE_NOT_FOUND
            
        # If we have more than 1 comment we are staff anyway
        # Therefore check only first comment
        return comments[0].approved
        
    def can_user_comment(self, user):
        if user.is_staff:
            return 1
           
        states = (x.approved for x in NewsComment.objects.filter(post=self, author=user.id))         
        return all(state not in (COMMENT_STATE_APR, COMMENT_STATE_PEN) for state in states)
    
    def __unicode__(self):
        return self.title
    
class NewsComment(models.Model):
    post = models.ForeignKey(NewsPost)
    author = models.CharField(max_length=128)
    approved = models.IntegerField(default=COMMENT_STATE_PEN)
    comment = models.TextField(max_length=250)
    date = models.DateTimeField()
    image = models.IntegerField(default=IMAGE_NONE)
    
    def __init__(self, *args, **kw):
        models.Model.__init__(self, *args, **kw)
        
        self.authorname = self.get_author_name()
    
    def get_author_name(self):  
        if not self.author:
            return 'Unknown user'
            
        try:
            user = User.objects.get(pk=self.author)
        
        except User.DoesNotExist:
            return 'Unknown user'
            
        return user.username
        
    def is_staff(self):
        try:
            user = User.objects.get(pk=self.author)
        
        except User.DoesNotExist:
            return 0
            
        return user.is_staff
    
    def __unicode__(self):
        s = self.authorname + "'s "
        if not self.approved:
            s += 'un'
            
        s += 'approved comment: %s...' % self.comment[:10]
        return s
        