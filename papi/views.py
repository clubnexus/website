from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.utils import timezone

from models import PlayCookie, NameState, Gameserver

from users.models import UserExt
from users import events

from ttsite import settings

import random, json
import hashlib, os

def get_file_hash(filename):
    hash = hashlib.sha256()
    with open(filename, 'rb') as f:
        while True:
            d = f.read(1024 ** 2 * 10) # 10 MB
            if not d:
                break
                
            hash.update(d)
            
    return hash.hexdigest()

def JSONResponse(data):
    return HttpResponse(json.dumps(data), content_type='application/json')
    
class LoginSuccess:
    UnknownError = 0
    IncorrectUserOrPassword = 1
    ServerError = 2
    TwoStepRequired = 3
    AccountDisabled = 4
    ServerClosed = 5
    IPBlacklisted = 6
    Success = 7
    Reserved = 8
    
# Common errors
loginError = lambda: JSONResponse({'status': LoginSuccess.IncorrectUserOrPassword, 'message': 'The username or password is incorrect.'})
genericError = lambda: JSONResponse({'status': LoginSuccess.ServerError, 'message': 'Something went wrong. Please try again.'})
bannedError = lambda: JSONResponse({'status': LoginSuccess.AccountDisabled, 'message': 'Your account is banned. Please try to login from website for more info.'})
serverClosedError = lambda: JSONResponse({'status': LoginSuccess.ServerClosed, 'message': 'The server is currently closed.'})

invalidCookie = lambda: JSONResponse({'success': False, 'error': 'invalid cookie'})

@csrf_exempt
def PAPI_login(request):
    try:
        data = json.loads(request.POST['data'])
        
    except:
        return HttpResponseBadRequest()
        
    username = data.get('username', '')
    password = data.get('password', '')
    if not username or not password:
        return loginError()
        
    user = authenticate(username=username, password=password)
    if user is None:
        try:
            user = User.objects.get(username=username).id
            
        except:
            user = ''
            
        events.add_event(event_type='FAILED_LOGIN', event_account=user,
                         request=request)
        return loginError()
        
    try:
        userext = UserExt.objects.get(user=user.id)
    
    except UserExt.DoesNotExist:
        return genericError()

    if userext.is_banned():
        return bannedError()
    
    gameservers = Gameserver.objects.order_by('-name')
    if not gameservers:
        return serverClosedError
        
    gameserver = random.choice(gameservers)
    cookie = PlayCookie()
    cookie.username = username
    cookie.value = os.urandom(16).encode('hex')
    cookie.save()

    return JSONResponse({'status': LoginSuccess.Success, 'message': 'OK',
                         'token': cookie.value, 'gameserver': gameserver})
    
@csrf_exempt
def PAPI_ban(request):
    try:
        databytes = request.POST['data']
        data = json.loads(databytes)
        hmac = request.POST['hmac']
        
    except:
        return HttpResponseBadRequest()
    
    expected = hashlib.sha512(databytes + settings.API_KEY).hexdigest()
    value = 0
    
    if len(hmac) != len(expected):
        return HttpResponseForbidden()
        
    for x, y in zip(expected, hmac):
        value |= (x != y)
        
    if value:
        return HttpResponseForbidden()
        
    username = data['username']
    try:
        user = User.objects.get(username=username)
        userext = UserExt.objects.get(user=user.id)
        
    except (User.DoesNotExist, UserExt.DoesNotExist):
        return JSONResponse({'error': 'no userext', 'success': False})
        
    userext.add_ban(data['banner'].encode('utf-8'), data['duration'], data['reason'].encode('utf-8'))
    return JSONResponse({'success': True})
    
@csrf_exempt
def PAPI_names(request):
    try:
        databytes = request.POST['data']
        data = json.loads(databytes)
        hmac = request.POST['hmac']
        
    except:
        return HttpResponseBadRequest()
    
    expected = hashlib.sha512(databytes + settings.API_KEY).hexdigest()
    value = 0
    
    if len(hmac) != len(expected):
        return HttpResponseForbidden()
        
    for x, y in zip(expected, hmac):
        value |= (x != y)
        
    if value:
        return HttpResponseForbidden()
        
    action = data['action']
    username = data['username']
    
    res = {'success': True, 'error': None}
    if action == 'get':
        states = NameState.objects.filter(username=username).order_by('date')
        for state in states:
            res[state.avId] = state.status
        
    elif action == 'set':
        state = NameState()
        state.username = username
        state.wantedName = data['wantedName']
        state.avId = data['avId']
        state.date = timezone.now()
        state.save()
        
    else:
        res['success'] = False
        res['error'] = 'invalid operation'
        
    return JSONResponse(res)
    
@csrf_exempt
def PAPI_cookie(request):
    try:
        databytes = request.POST['data']
        data = json.loads(databytes)
        hmac = request.POST['hmac']
        
    except:
        return HttpResponseBadRequest()
    
    expected = hashlib.sha512(databytes + settings.API_KEY).hexdigest()
    value = 0
    
    if len(hmac) != len(expected):
        return HttpResponseForbidden()
        
    for x, y in zip(expected, hmac):
        value |= (x != y)
        
    if value:
        return HttpResponseForbidden()
        
    cookie = str(data['cookie'])
    if len(cookie) <= 8:
        return invalidCookie()

    try:
        obj = PlayCookie.objects.get(value=cookie, used=False)
    
    except PlayCookie.DoesNotExist:
        return invalidCookie()
        
    username = obj.use()
    if username is None:
        return invalidCookie()
        
    return JSONResponse({'success': True, 'username': username})
    
def PAPI_gentoken(request, username):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    
    try:
        user = User.objects.get(username=username)
        if user is None:
            raise ValueError('not found')
            
        userext = UserExt.objects.get(user=user.id)

    except Exception as e:
        return JSONResponse({'status': LoginSuccess.ServerError, 'message': repr(e)})
        
    cookie = PlayCookie()
    cookie.username = username
    cookie.value = os.urandom(16).encode('hex')
    cookie.save()

    return JSONResponse({'status': LoginSuccess.Success, 'token': cookie.value})
    
@events.TT_login_required
def PAPI_servers(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/')
        
    if request.method == 'POST':
        server_id = request.POST.get('server_id', 'notset')
        action = request.POST.get('action', '')
        arg = ''
        
        try:
            action, arg = action.split('_', 1)
            if action == 'change':
                gameserver = Gameserver.objects.get(pk=server_id)
                gameserver.open = bool(int(arg))
                gameserver.save()
                
            elif action == 'add':
                arg = request.POST.get('name', '')
                if not '.' in arg:
                    raise ValueError
                    
                gameserver = Gameserver(name=arg)
                gameserver.save()
                
            elif action == 'del':
                gameserver = Gameserver.objects.get(pk=server_id)
                gameserver.delete()
                
            else:
                raise ValueError(action)
            
        except (Gameserver.DoesNotExist, ValueError):
            pass
            
        else:
            events.add_event('GAMESERVER_%s' % action.upper(), event_account=request.user.id, request=request,
                             event_desc_pub='arg=%s' % arg)
            
    servers = Gameserver.objects.order_by('-name')
    return render(request, 'api/servers.html', {'servers': servers})
    