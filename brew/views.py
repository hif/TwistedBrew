from django.core.context_processors import csrf
import os
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from brew.models import Brew, BrewSection, BrewStep
from brew.importing import brew_importer
import core.utils.logging as log
from rest_framework import viewsets
from brew.serializers import BrewSerializer, BrewSectionSerializer, BrewStepSerializer


class BrewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows brews to be viewed or edited.
    """
    queryset = Brew.objects.all().order_by('name')
    serializer_class = BrewSerializer


class BrewSectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows brew sections to be viewed or edited.
    """
    queryset = BrewSection.objects.all().order_by('index')
    serializer_class = BrewSectionSerializer


class BrewStepViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows brew steps to be viewed or edited.
    """
    queryset = BrewStep.objects.all().order_by('index')
    serializer_class = BrewStepSerializer


def brews(request):
    context = RequestContext(request)
    importers = brew_importer.BrewImporter.get_importers()
    context_dict = {
        'brews_active': True,
        'importers': importers,
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
    else:
        brew = None
    return render_to_response('brew_data.html', {'data': brew})


def brew_delete(request, pk):
    Brew.objects.get(pk=pk).delete()
    return HttpResponseRedirect('/brew/brews/')


def brews_delete_all(request):
    Brew.objects.all().delete()
    return HttpResponseRedirect('/brew/brews/')


def brews_import(request):
    uri = None
    try:
        if request.POST:
            index = int(request.POST['index'])
            file = request.FILES['file']
            filename = request.FILES['file'].name
            uri = os.path.dirname(os.path.realpath(__file__))
            uri += '/importing/uploaded_files/'
            uri += filename
            fd = open(uri, 'wb')
            for chunk in file.chunks():
                fd.write(chunk)
            fd.close()
            brew_importer.BrewImporter.import_brews(index, uri)
    except Exception as e:
        try:
            if uri is not None:
                log.error('Failed to upload file {0} : {1}'.format(uri, e.args[0]))
            else:
                log.error('Failed to upload file : {0}'.format(e.args[0]))
        except Exception:
            if uri is not None:
                log.error('Failed to upload file {0}'.format(uri))
            else:
                log.error('Failed to upload file')
    return HttpResponseRedirect('/brew/brews/')