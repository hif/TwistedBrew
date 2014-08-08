from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
# imports from within the Django web app must be scoped below the web package
from twistedbrew.models import Brew, Worker
from web.twistedbrew.views import CommanderForm

def home(request):
    context = RequestContext(request)
    worker_list = Worker.objects.order_by('-type')
    brew_list = Brew.objects.order_by('-name')
    context_dict = {
        'workers': worker_list,
        'brews': brew_list,
    }

    def add_category(request):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('rango/add_category.html', {'form': form}, context)

    return render_to_response('twistedbrew/home.html', context_dict, context)