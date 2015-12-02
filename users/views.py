from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from django.contrib.auth import views as auth_views, models as auth_models
from django.contrib.auth import authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.mail import get_connection

from ttsite import settings, util

from forms import UserForm, BugForm
from models import UserExt, BugReport
from models import BUG_NEW, BUG_ACK, BUG_INVALID, BUG_CONFIRMED, BUG_CLOSED

import events

import os

FORGOTPASS = '''Hello, <b>%(username)s!</b>

<p>You have request a password change in Toontown Next! Please, <a href="http://%(baseurl)s/resetpass/%(token)s">click here</a>
to change your password.</p>
<p>If you didn't request the change, you can safely ignore this email.</p>
<p>Yours,</p>
<p>Club Nexus</p>'''

def __get_email(to, subject, message):
    connection = get_connection(use_tls=settings.EMAIL_USE_TLS, host=settings.EMAIL_HOST, port=settings.EMAIL_PORT,
                                username=settings.EMAIL_HOST_USER, password=settings.EMAIL_HOST_PASSWORD)
    e = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [to], connection=connection)
    e.content_subtype = 'html'
    return e

def TT_login(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
        
    r = auth_views.login(request, *args, **kwargs)
    if isinstance(r, HttpResponseRedirect):
        # Login was successful
        
        try:
            userext = UserExt.objects.get(user=request.user.id)
            
        except UserExt.DoesNotExist:
            pass
            
        else:
            if userext.is_banned():
                auth_logout(request)
                form = AuthenticationForm(request)
                return render(request, 'registration/login.html', {'form': form, 'banned': 1, 'bantext': userext.get_last_ban()})
        
        events.add_event(event_type='SUCCESSFUL_LOGIN', event_account=request.user.id,
                         request=request)
                         
    elif 'username' in request.POST:
        try:
            user = User.objects.get(username=request.POST['username']).id
            
        except:
            user = ''
            
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
                
                # N.B. Do not use HTTPS here, let the server redirect if desired
                baseurl = request.get_host()
                token = os.urandom(16).encode('hex')
                
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
    
    bh = ''
    try:
        userext = UserExt.objects.get(user=request.user.id)
        bh = userext.get_ban_history()
            
    except UserExt.DoesNotExist:
        pass
    
    return render(request, 'account/events.html', {'events': ev, 'bh': bh})
    
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
            
                __get_email(user.email, 'Password Reset', FORGOTPASS % locals()).send()

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
    
@events.TT_login_required
def TT_account_bug(request):
    error = ''
    error_captcha = ''
    
    if request.method == 'POST':
        if not util.verify_captcha(request):
            error_captcha = 'Please confirm that you are not a bot.'
            
        else:
            form = BugForm(data=request.POST)
            if form.is_valid():
                data = form.cleaned_data
            
                bug = form.save(commit=False)
                bug.user = request.user.id
                bug.date = events.timezone.now()
                bug.save()
                # N.B. using priv desc because it's not escaped (XSS)
                events.add_event('BUG_REPORTED', event_account=request.user.id, request=request,
                                  event_desc_priv='Title: %s' % data['title'])
                return HttpResponseRedirect('/')
                
            else:
                names = {'data': 'Description'}
                key, errors = form.errors.items()[0]
                error = '%s: %s' % (names.get(key, key).title(), errors[0])

    return render(request, 'account/bug.html', {'error': error, 'error_captcha': error_captcha})
    
@events.TT_login_required
def TT_buglist(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/')
        
    if request.method == 'POST':
        bug_id = request.POST.get('bug_id', 'notset')
        action = request.POST.get('action', '-1')
        
        try:
            bug = BugReport.objects.get(pk=bug_id)
            action = int(action)
            if action not in (BUG_NEW, BUG_ACK, BUG_INVALID, BUG_CONFIRMED, BUG_CLOSED):
                raise ValueError
                
            actionName = ('NEW', 'ACK', 'INVALID', 'CONFIRMED', 'CLOSED')[action]
            
        except (BugReport.DoesNotExist, ValueError):
            pass
            
        else:
            bug.status = action
            bug.save()

            events.add_event('BUG_MARK_AS_%s' % actionName.upper(), event_account=request.user.id, request=request,
                             event_desc_pub='bug=%s' % bug.id)
            
    bugs = BugReport.objects.order_by('-date')
    bugs = filter(lambda bug: bug.status in (BUG_NEW, BUG_ACK, BUG_CONFIRMED), bugs)
    return render(request, 'bugs.html', {'bugs': bugs})
