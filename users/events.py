from django.http import HttpResponseRedirect
from django.utils.decorators import available_attrs
from django.utils import timezone
from django.conf import settings

from models import TTEvent

from functools import wraps

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
        
    else:
        ip = request.META.get('REMOTE_ADDR')
        
    return ip

def add_event(event_type, event_date=None, event_account=0, event_desc_pub='',
              event_desc_priv='', event_ip_pub=None, event_ip_priv=None,
              request=None):
    if event_date is None:
        event_date = timezone.now()
        
    if event_ip_pub is None:
        if request:
            event_ip_pub = get_client_ip(request)
            
        else:
            event_ip_pub = ''
            
    if event_ip_priv is None:
        event_ip_priv = ''
    
    ev = TTEvent(event_type=event_type, event_date=event_date,
                 event_account=event_account, event_desc_pub=event_desc_pub,
                 event_desc_priv=event_desc_priv, event_ip_pub=event_ip_pub,
                 event_ip_priv=event_ip_priv)
    return ev.save()

def get_events(event_account):
    try:
        r = TTEvent.objects.filter(event_account=event_account)
    
    except TTEvent.DoesNotExist:
        r = []
        
    return r
    
##### TT specific decorator
    
def TT_user_passes_test(test_func):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
                
            return HttpResponseRedirect('/login/')
                
        return _wrapped_view
        
    return decorator

def TT_login_required(function):
    return TT_user_passes_test(lambda u: u.is_authenticated() and u.is_active)(function)
