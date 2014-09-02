from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from namingservice.profiles.forms import ProfileChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect

def register(request, template_name='profiles/register.djhtml'):
    if request.user.is_authenticated():
        return redirect('settings_page')
    if request.method == 'POST':
        form = UserCreationForm(request.POST) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration was successful! Now you can login with your username and password.')
            new_user = get_object_or_404(User, username = form.cleaned_data['username'])
            html_message = """
                Welcome to the namingservice.org, here you can find yourself a name. And even more!
                Let's find out introduction information about the service. <b>It's fun!</b>
                In the list below you can see the all active orders from our clients and you can add you suggestions to it immediately, and became a contributor. <b>Start making money right now.</b>
                If you want to become our client just click <a href="/orders/my">my orders</a> and add your order for our contributors, set the price you think is fair and make a payment! After that you will start receiving suggestions immediately! <b>It's fair and it's easy.</b>
                You can become both a client adding orders and a contributor adding suggestions at the same time. You do not need separate accounts. <b>It's great!</b>
                If you want to know more about the service click <a href="/about/">about</a>
            """
            new_user.message_set.create(message=html_message)
            
            return redirect('login_page')
    else:
        form = UserCreationForm()
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))

@login_required
def settings(request, template_name='profiles/settings.djhtml'):
    if request.method == 'POST':
        form = ProfileChangeForm(request.POST, instance=request.user) 
        if form.is_valid():
            form.save()
            messages.success(request, 'user settings were successfully changed')
            return redirect('settings_page')
    else:
        form = ProfileChangeForm(instance=request.user)
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))


"""
Native django's password_change view with message add 
"""
@csrf_protect
@login_required
def password_change(request, template_name='profiles/password_change.djhtml',
                    post_change_redirect='settings_page', password_change_form=PasswordChangeForm):
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'password was successfully changed, by the next login it will be activated')
            return redirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))
