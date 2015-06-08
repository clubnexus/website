from django.http import HttpResponseRedirect
from django.shortcuts import render

from ttsite.settings import API_RELAY, WANT_INVASION_DEBUG
from users.events import TT_login_required, add_event
from papi.models import NameState, STATUS_PEN, STATUS_REJ, STATUS_APR

import urllib2
import json
import os

suitHeadTypes = ['f',
 'p',
 'ym',
 'mm',
 'ds',
 'hh',
 'cr',
 'tbc',
 'bf',
 'b',
 'dt',
 'ac',
 'bs',
 'sd',
 'le',
 'bw',
 'sc',
 'pp',
 'tw',
 'bc',
 'nc',
 'mb',
 'ls',
 'rb',
 'cc',
 'tm',
 'nd',
 'gh',
 'ms',
 'tf',
 'm',
 'mh']

def __convertTime(value):
    if not value:
        return '-'
        
    r = []
    u = [('s', 60), ('min', 60), ('h', 24), ('d', 0)]
    while u and value:
        unit, mod = u.pop(0)
        if not mod:
            x = value
            
        else:
            value, x = divmod(value, mod)
            
        if x != 0:
            r.append('%d%s' % (x, unit))
        
    return ' '.join(r[::-1])
    
def __get_debug_invasion():
    r = {'error': None}
    for i in xrange(32):
        r[str(i)]= {
        'cogFullName': [os.urandom(4).encode('hex'), '', ''],
        'cogName': suitHeadTypes[i],
        'districtName': os.urandom(7).encode('hex'),
        'duration': 1,
        'numCogs': int(ord(os.urandom(1)) * 99),
        'remaining': int(-ord(os.urandom(1)) ** 2.5),
        'skel': False,
        }
    return r

class _District:
    pass
    
class _Invasion:
    pass

def __doRequest(url, args={}):
    ag = '&'.join('%s=%s' % (x, y) for x, y in args.items())
    url = "http://%s%s?%s" % (API_RELAY, url, ag)
    try:
        req = urllib2.Request(url)
        return json.loads(urllib2.urlopen(req, timeout=8).read())
        
    except:
        return {'error': 'Unable to reach server.'}

def TT_api_invasions(request):
    if WANT_INVASION_DEBUG:
        data = __get_debug_invasion()
        
    else:
        data = __doRequest('/invasions')
        
    error = data.pop('error')
    
    districts = []
    if not error:
        for d in data.values():
            if d['duration'] == 0:
                continue
                
            inv = _Invasion()
            if d['skel'] == True:
                inv.cogName = 'Skelecog'
                inv.pic = 'skel'
            else:
                inv.cogName = d['cogFullName'][0]
                inv.pic = d['cogName']
            inv.numCogs = d['numCogs']
            inv.duration = __convertTime(d['duration'])
            inv.isMega = inv.duration == '1s'
            inv.remaining = __convertTime(abs(d['remaining']))
            inv.cogWidth = 150
            if inv.pic in ('ms', 'sd', 'tm', 'ac'):
                inv.cogWidth = 100
            
            district = _District()
            district.name = d['districtName']
            district.invasion = inv
            districts.append(district)
            
    if not districts:
        error = 'No invasion found!'
        
    return render(request, 'api/invasion.html', {'error': error, 'districts': districts})

@TT_login_required
def TT_api_names(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/')
        
    if request.method == 'POST':
        try:
            avId = int(request.POST['avId'])
            
        except:
            avId = 0
            
        action = request.POST.get('action', 'notset')
        
        try:
            namestate = NameState.objects.get(avId=avId, status=STATUS_PEN)
            
        except NewsComment.DoesNotExist:
            pass
            
        else:
            changed = 0
            
            if action == 'rej':
                changed = 1
                namestate.status = STATUS_REJ
                
            elif action == 'apr':
                changed = 1
                namestate.status = STATUS_APR
               
            if changed:
                add_event('NAME_%s' % action.upper(), event_account=request.user.id, request=request,
                           event_desc_pub='%s' % (namestate.wantedName))
                namestate.mod = request.user.username
                namestate.save()
    
    names = NameState.objects.filter(status=STATUS_PEN).order_by('date')
    return render(request, 'api/names.html', {'names': names})
    