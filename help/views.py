from django.templatetags.static import static
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

def TT_help_index(request):
    return HttpResponseRedirect('/help/faq')

def TT_help_faq(request):
    return render(request, 'help/faq.html', {})
    
def TT_help_salute(request):
    return render(request, 'help/salute.html', {})
    
def TT_help_about(request):
    return render(request, 'help/about.html', {})
    
def TT_help_screenshots(request):
    rd = {}
    gamelist = ''
    for game, obj in (('Toon Puzzle', 'game'), ('Toon Puzzle 2', 'game2'),
                      ('Toon Shoot', 'toonshoot'), ('Cog Crusher', 'cogCrush'),
                      ('TuneTown', 'tunetown'), ('Card Cog', 'cardcog'),
                      ('Memory Game', 'memory'), ('Laff Lanes', 'laff'),
                      ('Cog Invasion (Squirt)', 'coginv1'), ('Cog Invasion (Throw)', 'coginv2')):
        obj = static('shockwave/%s.swf' % obj)
        gamelist += '''<tr><td colspan="3" align="center"><br><font face="arial,helvetica" size="2">
                       <a href="%(obj)s">%(game)s</a></font></td></tr>''' % locals()
   
    rd['gamelist'] = gamelist
    return render(request, 'help/screenshots.html', rd)
    