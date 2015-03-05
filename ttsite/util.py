import urllib2, json

import settings

def verify_captcha(request):
    if settings.CAPTCHA_ALWAYS_CORRECT:
        return 1
        
    resp = request.POST.get('g-recaptcha-response', '')
    data = 'secret=6LfaqgETAAAAABfxKtZx7gKQtNAhK7Ud1QxNc5f3&response=' + resp
    
    req = urllib2.Request('https://www.google.com/recaptcha/api/siteverify', data, {})
    res = json.loads(urllib2.urlopen(req).read())
    return res.get('success', False)
    