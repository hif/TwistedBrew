from django.shortcuts import render
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import Brew, BrewSection, BrewStep


def brews(request):
    context = RequestContext(request)
    context_dict = {
        'brews_active': True,
    }
    context_dict.update(csrf(request))
    return render_to_response('brews.html', context_dict, context)


def brew_selection(request):
    if request.method == 'POST':
        brew_list = Brew.objects.order_by('name')
    else:
        brew_list = []
    return render_to_response('brew_selection.html', {'selection': brew_list})


def brew_data(request):
    if request.method == 'POST':
        brew = Brew.objects.get(pk=(request.POST['pk']))
        brew.load_brew_sections()
        for section in brew.brew_sections:
            section.load_brew_steps()
    else:
        brew = None
    return render_to_response('brew_data.html', {'data': brew})
