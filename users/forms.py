from django.contrib.auth.models import User
from django import forms

from models import BugReport

class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=40)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

class BugForm(forms.ModelForm):
    title = forms.CharField(widget=forms.PasswordInput())
    data = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = BugReport
        fields = ('title', 'data')
