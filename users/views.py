from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from django.contrib.auth import views as auth_views, models as auth_models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage

from ttsite import settings, util

from forms import UserForm
from models import UserExt

import events

import os

EMAILDATA = '''Hello, <b>%(username)s!</b>

<p>Thank you for registering in Toontown Next! Please, <a href="http://%(baseurl)s/verify/%(token)s">click here</a>
to confirm your account.</p>
<p>Yours,</p>
<p>Club Nexus</p>'''

FORGOTPASS = '''Hello, <b>%(username)s!</b>

<p>You have request a password change in Toontown Next! Please, <a href="http://%(baseurl)s/resetpass/%(token)s">click here</a>
to change your password.</p>
<p>If you didn't request the change, you can safely ignore this email.</p>
<p>Yours,</p>
<p>Club Nexus</p>'''

def TT_login(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
        
    r = auth_views.login(request, *args, **kwargs)
    if isinstance(r, HttpResponseRedirect):
        # Login was successful
        events.add_event(event_type='SUCCESSFUL_LOGIN', event_account=request.user.id,
                         request=request)
                         
    elif 'username' in request.POST:
        try:
            user = User.objects.get(username=request.POST['username']).id
            
        except:
            user = 0
            
        events.add_event(event_type='FAILED_LOGIN', event_account=user,
                         request=request)
        
    return r
    
def TT_logout(request, *args, **kwargs):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login')
        
    return auth_views.logout(request, '/')
  
def TT_register(request):
    # N.B. We use a form ONLY to validate input
    
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    
    error_username = []
    error_email = []
    error_password = []
    error_captcha = []
    email = username = ''
    
    if request.method == 'POST':
        form = UserForm(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            username = data['username']
            email = data['email']
            password = data['password']
            password2 = data.get('password2', '')
            
            email_taken = len(auth_models.User.objects.filter(email__iexact=email))
            username_problem = UserExt.validate_username(username)
            password_problem = UserExt.validate_password(password)
            captcha_ok = util.verify_captcha(request)
            
            if username_problem:
                error_username = [username_problem]
            
            elif email_taken:
               error_email = ['This email has already been used.']
               
            elif password_problem:
                error_password = [password_problem]
                
            elif password2 != password:
                error_password.append('The passwords do not match.')
                
            elif not captcha_ok:
                error_captcha = ['Please confirm that you are not a bot.']
            
            else:
                user = form.save(commit=False)
                user.set_password(user.password)
                user.is_active = 0
                
                # N.B. Do not use HTTPS here, let the server redirect if desired
                baseurl = request.get_host()
                token = os.urandom(32).encode('hex')
                
                try:
                    msg = EmailMessage('Registration', EMAILDATA % locals(), settings.DEFAULT_FROM_EMAIL, [email])
                    msg.content_subtype = 'html'
                    msg.send()

                except:
                    raise
                    error_email = ['Unable to reach this email.']

                else:
                    user.save()
                    userext = UserExt(user=user.id, email_token=token)
                    userext.save()

                    events.add_event('REGISTERED', event_account=user.id, request=request,
                                     event_desc_priv='emailtoken=%s' % token)              

                    return HttpResponseRedirect('/register/success')
                
        else:
            for key, errors in form.errors.items():
                if key == 'username':
                    error_username.extend(errors)
                    
                elif key == 'email':
                    error_email.extend(errors)
                
                elif key in ('password', 'password2'):
                    error_password.extend(errors)              
  
    error_username = set(error_username)
    error_password = set(error_password)
    error_email = set(error_email)
    error_captcha = set(error_captcha)
    
    form = UserForm()
    return render(request, 'registration/register.html', {'error_username': error_username,
                                                          'error_email': error_email,
                                                          'error_password': error_password,
                                                          'error_captcha': error_captcha,
                                                          'D_username': username,
                                                          'D_email': email})
    
def TT_verify(request, token):
    userext = get_object_or_404(UserExt, email_token=token, email_verified=False)
    user = get_object_or_404(User, pk=userext.user)
    
    user.is_active = 1
    user.save()
    
    userext.email_verified = 1
    userext.save()
    
    events.add_event('EMAIL_VERIFIED', event_account=user.id, request=request)
    
    return HttpResponseRedirect('/login')
    
@events.TT_login_required
def TT_account_main(request):
    return render(request, 'account/index.html')
  
@events.TT_login_required
def TT_account_events(request):
    ev = list(events.get_events(request.user.id).order_by('-event_date'))
    return render(request, 'account/events.html', {'events': ev})
    
@events.TT_login_required
def TT_account_changepassword(request):
    error = ''
    
    if request.method == 'POST':
        if not 'oldpassword' in request.POST:
            error = 'Old password field is required.'
            
        elif not 'password' in request.POST:
            error = 'New password field is required.'
            
        elif not 'password2' in request.POST:
            error = 'New password confirmation field is required.'
            
        else:
            password = request.POST['password']
            password2 = request.POST['password2']
            
            if password != password2:
                error = 'The passwords do not match.'
                
            else:
                error = UserExt.validate_password(password)
                if not error:
                    if not authenticate(username=request.user.username, password=request.POST['oldpassword']):
                        error = 'The old password is incorrect.'
                    
                    else:
                        # Phew, finally update it
                        user = request.user
                        user.set_password(password)
                        user.save()
                        events.add_event(event_type='CHANGE_PASSWORD', event_account=user.id,
                                         request=request)
                        
                        return HttpResponseRedirect('/login')

    return render(request, 'account/changepassword.html', {'error': error})
    
def TT_register_success(request):
    context = request.session.pop('registersuccessctx', 'Your account has been registered.')
    extra = request.session.pop('registersuccessextra', '')
    return render(request, 'registration/success.html', {'context': context, 'extra': extra})
    
def TT_register_resend(request):
    error = ''
    
    if request.method == 'POST':
        email = request.POST['email']
        if not email.strip() or not '@' in email:
            error = 'Invalid email'
            
        elif not util.verify_captcha(request):
            error = 'Please confirm that you are not a bot.'
            
        else:
            try:
                user = auth_models.User.objects.get(email__iexact=email)
                userext = UserExt.objects.get(user=user.id, email_verified=False)
            
            except (auth_models.User.DoesNotExist, UserExt.DoesNotExist):
                error = 'Email not found or associated user already confirmed'
            
            else:
                username = user.username
                token = userext.email_token
                baseurl = request.get_host()
            
                msg = EmailMessage('Registration', EMAILDATA % locals(), settings.DEFAULT_FROM_EMAIL, [user.email])
                msg.content_subtype = 'html'
                msg.send()
            
                request.session['registersuccessctx'] = 'Registration email resent.'
                return HttpResponseRedirect('/register/success')

    return render(request, 'registration/resend.html', {'error': error})
    
def TT_forgotpass(request):
    error = ''
    
    if request.method == 'POST':
        email = request.POST['email']
        if not email.strip() or not '@' in email:
            error = 'Invalid email'
            
        elif not util.verify_captcha(request):
            error = 'Please confirm that you are not a bot.'
            
        else:
            try:
                user = auth_models.User.objects.get(email__iexact=email, is_active=True)
                userext = UserExt.objects.get(user=user.id)
            
            except (auth_models.User.DoesNotExist, UserExt.DoesNotExist):
                error = 'Email not found or account not activated'
            
            else:
                username = user.username
                token = userext.gen_reset_token()
                baseurl = request.get_host()
            
                msg = EmailMessage('Password Reset', FORGOTPASS % locals(), settings.DEFAULT_FROM_EMAIL, [user.email])
                msg.content_subtype = 'html'
                msg.send()

                request.session['registersuccessctx'] = 'Password reset email sent.'
                request.session['registersuccessextra'] = '<p><i>Make sure to use link provided in your email soon, as it will be invalidated within the next 36 hours.</i></p>'
                return HttpResponseRedirect('/register/success')

    return render(request, 'registration/forgotpass.html', {'error': error}) 
    
def TT_resetpass(request, token):
    print token
    
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    
    error = ''
    
    user, userext = UserExt.check_reset_token(token)
    if not user:
        return HttpResponseRedirect('/404')
    
    if request.method == 'POST':
        password = request.POST['password']
        error = UserExt.validate_password(password)
        if error:
            pass
            
        elif not util.verify_captcha(request):
            error = 'Please confirm that you are not a bot.'
            
        else:
            user.set_password(password)
            user.save()
            
            userext.email_reset_token = ''
            userext.save()
            
            events.add_event(event_type='CHANGE_PASSWORD', event_account=user.id,
                             request=request)
            
            return HttpResponseRedirect('/login')

    return render(request, 'registration/resetpass.html', {'error': error, 'token': token})
    
def errorpage(request):
    return render(request, 'error.html', {})
    