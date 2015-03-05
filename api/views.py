from django.shortcuts import render

from ttsite.settings import API_RELAY

import urllib
import json

def __convertTime(value):
    if not value:
        return '-'
        
    r = []
    u = [('s', 60), ('min', 60), ('h', 24), ('day', 0)]
    while u and value:
        unit, mod = u.pop(0)
        if not mod:
            x = value
            
        else:
            value, x = divmod(value, mod)
            
        if x != 0:
            r.append('%d%s' % (x, unit))
        
    return ' '.join(r[::-1])

class _District:
    pass
    
class _Invasion:
    pass

def __doRequest(url, args):
    ag = '&'.join('%s=%s' % (x, y) for x, y in args.items())
    url = "http://%s%s?%s" % (API_RELAY, url, ag)
    try:
        return json.loads(urllib.urlopen(url).read())
        
    except:
        return {'error': 'Unable to reach server.'}

def TT_api_invasions(request):
    data = __doRequest('/invasions', {'lang': 'l3'})
    error = data.pop('error')
    
    districts = []
    if not error:
        for d in data.values():
            if d['duration'] == 0:
                continue
                
            inv = _Invasion()
            inv.cogName = d['cogFullName'][0]
            inv.pic = d['cogName']
            inv.numCogs = d['numCogs']
            inv.duration = __convertTime(d['duration'])
            inv.isMega = inv.duration == '1s'
            inv.remaining = __convertTime(abs(d['remaining']))
            
            district = _District()
            district.name = d['districtName']
            district.invasion = inv
            districts.append(district)
            
    if not districts:
        error = 'No invasion found!'
        
    return render(request, 'api/invasion.html', {'error': error, 'districts': districts})
