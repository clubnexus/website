from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from django.contrib.auth import views as auth_views, models as auth_models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.mail import get_connection

from ttsite import settings, util

from forms import UserForm
from models import UserExt

import events

import os

FORGOTPASS = '''Hello, <b>%(username)s!</b>
<p>You have request a password change in Toontown Next! Please, <a href="%(url)s">click here</a>
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
                user.is_active = 1
                
                token = os.urandom(16).encode('hex')
                
                user.save()
                userext = UserExt(user=user.id, email_token=token)
                userext.save()

                events.add_event('REGISTERED', event_account=user.id, request=request)              

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
    context = request.session.pop('registersuccessctx', 'Congratulations! Your account has been registered. You can now proceed to login.')
    extra = request.session.pop('registersuccessextra', '')
    wantLogin = request.session.pop('registersuccesswantlogin', 1)
    return render(request, 'registration/success.html', {'context': context, 'extra': extra, 'want_login': wantLogin})

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
                if userext.is_token_valid():
                    raise ValueError
            
            except (auth_models.User.DoesNotExist, UserExt.DoesNotExist, ValueError):
                error = 'Either this email was not found or the account is not activated or a password change has already been request lately. It may take up to 24 hours to reset link reach your email.'
            
            else:
                username = user.username
                userext.gen_reset_token()
                
                request.session['registersuccessctx'] = 'Password reset email sent.'
                request.session['registersuccessextra'] = '<p><i>It may take up to 24 hours to reset link reach your email. If you don\'t get it until then, check your spam and if it\'s still not there request a new password change email using the previous form.</i></p>'
                request.session['registersuccesswantlogin'] = 0
                return HttpResponseRedirect('/register/success')

    return render(request, 'registration/forgotpass.html', {'error': error})
    
def TT_resetpass(request, token):
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
    
@events.TT_login_required
def TT_pending(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/')
        
    if request.method == 'POST':
        token = request.POST.get('token', 'notset')
        try:
            userext = UserExt.objects.get(email_reset_token=token)
            userext.email_reset_token = token[:32] + '1'
            userext.save()
            
        except Exception as e:
            print token, e
            raise
            
    pending = UserExt.objects.order_by('-email_reset_token')
    pd = set()
    for p in pending:
        if p.email_reset_token and p.email_reset_token[-1] == '0':
            user = p.get_user()
            if not user:
                continue
             
            username = user.username
            url = 'http://%s/resetpass/%s' % (request.get_host(), p.email_reset_token[:32])
            msg = FORGOTPASS % locals()
            
            res =  '<td><a href="mailto:%s' % user.email
            res += '?subject=Password%20reset">'
            res += '%s</a></td>' % username
            res += '<td>%s</td>' % user.email
            res += '<td style="text-align: left;">%s</td>' % msg
            res += '<td><a href="javascript:doreview(\'%s\');">DONE</a></td>' % p.email_reset_token
            pd.add(res)
            
    return render(request, 'pending.html', {'pd': pd})
    
def errorpage(request):
    return render(request, 'error.html', {})
    