from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from users.events import TT_login_required, add_event

from models import NewsPost, NewsComment
from models import COMMENT_STATE_PEN, COMMENT_STATE_APR, COMMENT_STATE_REJ
from models import COMMENT_STATE_NOT_FOUND
from models import get_icons, decode_image

from forms import PostForm

def home(request):
    posts = NewsPost.objects.order_by('-date')
    if posts:
        post = posts[0]
        user_commented = post.user_comment_status(request.user)
        return render(request, 'news/post.html', {'post': post, 'user_commented': user_commented,
                                                  'icons': get_icons()})
    
    else:
        return render(request, 'help/about.html', {})
        
def play(request):
    return render(request, 'play.html', {})
    
def news(request):
    news_list = NewsPost.objects.order_by('-date')[:5]
    return render(request, 'news/news.html', {'news_list': news_list})
    
def detail(request, post_id):
    post = get_object_or_404(NewsPost, pk=post_id)
    user_commented = post.user_comment_status(request.user)
    return render(request, 'news/post.html', {'post': post, 'user_commented': user_commented,
                                              'icons': get_icons()})
    
@TT_login_required
def comment(request, post_id):        
    post = get_object_or_404(NewsPost, pk=post_id)
    user_commented = post.user_comment_status(request.user)
    if not post.can_user_comment(request.user):
        # u w0t m8
        return HttpResponse('You have already commented in this post!')
        
    try:
        image = int(request.POST.get('image', '0').strip())
        if image:
            if not decode_image(image):
                # u w0t m8
                raise ValueError('bad value for image')
            
            if not request.user.is_staff:
                # u w0t m8
                return HttpResponseForbidden('non-staff attempted to submit image in comment')
        
    except:
        # u w0t m8
        print image, image >> 6, image & 64, decode_image(image)
        raise
        return HttpResponse('The image value specified has some problem, try another one!')
        
    comment = request.POST.get('comment', '').strip()
    if not comment:
        # u w0t m8
        return HttpResponse('Empty comment?')
        
    if len(comment) > 1000 and not request.user.is_staff:
        # u w0t m8
        return HttpResponse('Comment too long!')
        
    c = NewsComment()
    c.post = post
    c.author = request.user.id
    c.comment = comment
    c.date = timezone.now()
    c.image = image
    c.approved = COMMENT_STATE_APR if request.user.is_staff else COMMENT_STATE_PEN
    c.save()
    
    add_event('POST_COMMENT', event_account=request.user.id, request=request,
              event_desc_pub='Post: <a href="/news/post/%s/">%s</a>' % (post.id, post.title))
    
    return HttpResponseRedirect('/news/post/%s' % post_id)

@TT_login_required
def make(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')
    
    errors = []
    title = post = ''
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            
            title = data['title']
            author = 'Club Nexus' # data['author']
            post = data['post']
            pic = data['pic']
            date = data['date']
                        
            post = form.save()
            add_event('POST', event_account=request.user.id, request=request,
                              event_desc_pub='id=%s' % post.id) 

            return HttpResponseRedirect('/')
                
        else:
            for key, errors in form.errors.items():
                errors.extend('%s: %s' % (key, x) for x in errors)
      
    form = PostForm()
    return render(request, 'news/make.html', {'errors': set(errors), 'form': form})

@TT_login_required
def review(request):
    if not request.user.is_staff:
        return HttpResponseRedirect('/')
        
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id', 'notset')
        action = request.POST.get('action', 'notset')
        
        try:
            comment = NewsComment.objects.get(pk=comment_id, approved=COMMENT_STATE_PEN)
            
        except NewsComment.DoesNotExist:
            pass
            
        else:
            changed = 0
            
            if action == 'rej':
                changed = 1
                comment.approved = COMMENT_STATE_REJ
                
            elif action == 'apr':
                changed = 1
                comment.approved = COMMENT_STATE_APR
               
            if changed:
                post = comment.post
                add_event('COMMENT_%s' % action.upper(), event_account=request.user.id, request=request,
                           event_desc_pub='Post: <a href="/news/post/%s/">%s</a><br>commented by: %s' % (post.id, post.title, comment.authorname))     
                comment.save()
    
    pending = NewsComment.objects.filter(approved=COMMENT_STATE_PEN)
    return render(request, 'news/review.html', {'comments': pending})
    