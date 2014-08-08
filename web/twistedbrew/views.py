from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
# imports from within the Django web app must be scoped below the web package
from twistedbrew.models import Brew, Worker

def home(request):
    context = RequestContext(request)
    worker_list = Worker.objects.order_by('-type')
    brew_list = Brew.objects.order_by('-name')
    context_dict = {
        'workers': worker_list,
        'brews': brew_list,
    }

    return render_to_response('twistedbrew/home.html', context_dict, context)