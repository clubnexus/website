from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from models import TopToonsEntry

from users import events
from ttsite import settings

import hashlib
import json

def getCurrentMonth():
    dt = datetime.date.today()
    month = dt.month
    year = dt.year
    return year * 100 + month
    
def getPrevMonth():
    current = getCurrentMonth()
    year, month = divmod(current, 100)
    month -= 1
    if not month:
        month = 12
        year -= 1
        
    return year * 100 + month
   
def getNextMonth():
    current = getCurrentMonth()
    year, month = divmod(current, 100)
    month += 1
    if month > 12:
        month = 1
        year += 1
        
    return year * 100 + month
    
# GLOBALS (keep sync with TopToonsGlobals.py)
CAT_COGS = 1
CAT_BLDG = 2
CAT_CATALOG = 4
CAT_GIFTS = 8
CAT_TASKS = 16
CAT_TROLLEY = 32
CAT_RACE_WON = 64
CAT_FISH = 128
CAT_JELLYBEAN = 256
CAT_HOLE_IN_ONE = 512
CAT_COURSE_UNDER_PAR = 1024
CAT_VP = 2048
CAT_CFO = 4096
CAT_CJ = 8192
CAT_CEO = 16384

DESCRIPTIONS = {CAT_COGS: 'Cogs defeated',
                CAT_BLDG: 'Toon buildings recovered',
                CAT_CATALOG: 'Items purchased from cattlelog',
                CAT_GIFTS: 'Gifts given',
                CAT_TASKS: 'Toontasks completed',
                CAT_TROLLEY: 'Trolley games played',
                CAT_RACE_WON: 'Races won',
                CAT_FISH: 'Fish caught',
                CAT_JELLYBEAN: 'Jellybeans earned',
                CAT_HOLE_IN_ONE: 'Holes in one',
                CAT_COURSE_UNDER_PAR: 'Mini-golf courses under par',
                CAT_VP: 'Vice President battles won',
                CAT_CFO: 'Chief Financial Officer battles won',
                CAT_CJ: 'Chief Justice battles won',
                CAT_CEO: 'Chief Executive Officer battles won'
               }

_CAT_BEGIN = CAT_COGS
_CAT_END = CAT_CEO
_CAT_ALL = (_CAT_END << 1) - 1

def JSONResponse(data):
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def post(request):
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
        
    month = data.pop('month')
    
    try:
        TopToonsEntry.objects.get(month=month)
        
    except TopToonsEntry.DoesNotExist:
        pass
        
    else:
        return JSONResponse({'success': False, 'error': 'month already uploaded!'})
    
    entry = TopToonsEntry(month=month, data=json.dumps(data))
    entry.save()

    return JSONResponse({'success': True})
    
class _TOON:
    pass
    
class _MONTH:
    pass
    
class _CATEGORY:
    def __init__(self, name, toons):
        self.name = name
        self.toons = []
        for dt in toons:
            t = _TOON()
            (t.name, t.hp), t.score = dt
            self.toons.append(t)
            
def _convertMonthToText(month):
    year, month = divmod(current, 100)
    return '%s/%s' % (str(month).zfill(2), year) # TO DO: str (jan, feb, etc)

def home(request):
    objects = TopToonsEntry.objects.order_by('-month')          
    monthList = []
    
    for obj in objects:
        data = json.loads(obj.data)
        categories = [] 
        
        i = _CAT_BEGIN
        while i <= _CAT_END:
            name = DESCRIPTIONS[i]
            categories.append(_CATEGORY(name, data[str(i)]))
            i *= 2
            
        m = _MONTH()
        m.categories = categories
        m.text = _convertMonthToText(obj.month)
        monthList.append(m)
            
    return render(request, 'toptoons/toptoons.html', {'error': error, 'categories': categories, 'monthList': monthList})
    