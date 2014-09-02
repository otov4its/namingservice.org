from django.shortcuts import render_to_response
from django.template import RequestContext

def home_page(request):
    return render_to_response('base_2col.djhtml', context_instance=RequestContext(request))

    





