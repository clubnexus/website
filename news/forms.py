from ckeditor.widgets import CKEditorWidget
from django import forms
from models import NewsPost

import datetime

class PostForm(forms.ModelForm):
    date = forms.DateTimeField(initial=datetime.datetime.now)#(widget=SelectDateWidget)
    
    class Meta:
        model = NewsPost
        fields = ('title', 'post', 'pic', 'date')
        widgets = {'post': CKEditorWidget()}
