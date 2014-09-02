from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template.context import RequestContext
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required
from namingservice.orders.forms import AddOrderForm, DeleteOrderForm, PayOrderForm, AddSuggestionForm, DeleteSuggestionForm, WinSuggestionForm
from django.contrib import messages
from namingservice.accounts.models import Account
from django.db.models import F
from django.db.transaction import commit_on_success
from namingservice.orders.models import Order, Suggestion
from decimal import Decimal
from django.utils.html import escape
from django.utils.text import truncate_words

def orders(request, subset, template_name='orders/orders_%s.djhtml'):
    if (subset in ['all']):
        order_list = Order.objects.select_related().filter(status__in=['a', 'c']).order_by('status', 'currency', '-cost')
    else:
        if request.user.is_authenticated():
            if (subset == 'my'):
                # all except deleted orders
                order_list = request.user.order_set.exclude(status='d').order_by('-crdate')
            elif (subset == 'suggestions'):
                # all except deleted suggestions
                order_list = Order.objects.select_related().filter(suggestion__user=request.user, suggestion__status__in=['n', 'l', 'd', 'w', 's']).distinct().order_by('-crdate')
        else:
            return redirect_to_login(request.path)
        
    orders = _do_paginator(request, order_list)

    return render_to_response(template_name % (subset), {'orders': orders}, context_instance=RequestContext(request))

def order_details(request, order_id, template_name='orders/order_details_%s.djhtml'):
    order = get_object_or_404(Order.objects.select_related('user'), pk=order_id)
    need_pagination = True
    win_suggestion = []
    form = []
    form_del = []
    suggestion_to_del = []
    
    # anonymous user
    if (not request.user.is_authenticated()):
        # active order
        if (order.status == 'a'):
            suggestion_list = []
            template_name_posfix = 'anonymous_active'
        # complete order
        elif (order.status == 'c'):
            suggestion_list = get_object_or_404(order.suggestion_set, status='w')
            need_pagination = False
            template_name_posfix = 'anonymous_complete'
        else:
            raise Http404
        
    # registered user 
    else:
        # user's order
        if (order.user == request.user):
            # active order
            if (order.status == 'a'):
                # trying catch suggestion for win
                if request.GET:
                    try:
                        action = request.GET.__getitem__('action')
                        suggestion_id = int(request.GET.__getitem__('suggestion_id'))
                        if (action == 'win'):
                            win_suggestion = Suggestion.objects.get(pk=suggestion_id, order = order)
                            form = WinSuggestionForm({'suggestion_id': win_suggestion.id})
                    except: 
                        win_suggestion = []
                        form = []
                # update status all new suggestions to 'seen'
                if order.suggestion_set.filter(status = 'n').exists():
                    order.suggestion_set.filter(status = 'n').update(status = 's')
                # get all suggestions except 'delete' status
                suggestion_list = order.suggestion_set.select_related('user').exclude(status = 'x')
                template_name_posfix = 'my_order_active'
            # complete order
            elif (order.status == 'c'):
                suggestion_list = get_object_or_404(order.suggestion_set, status='w')
                need_pagination = False
                template_name_posfix = 'my_order_complete'
            # not paid order
            elif (order.status == 'n'):
                action = request.GET.get('action', '')
                if (action):
                    if (action == 'delete'):
                        form = DeleteOrderForm({'order_id': order.id})
                    if (action == 'pay'):
                        form = PayOrderForm({'order_id': order.id, 'cost': order.cost})
                suggestion_list = []
                template_name_posfix = 'my_order_not_paid'
            else:
                raise Http404
            
        # not user's order
        else:
            # active order
            if (order.status == 'a'):
                # trying catch suggestion for deletion
                if request.GET:
                    try:
                        action = request.GET.__getitem__('action')
                        suggestion_id = int(request.GET.__getitem__('suggestion_id'))
                        if (action == 'delete'):
                            suggestion_to_del = Suggestion.objects.get(pk=suggestion_id, user = request.user)
                            form_del = DeleteSuggestionForm({'suggestion_id': suggestion_to_del.id})
                    except: 
                        suggestion_to_del = []
                        form_del = []
                        
                suggestion_list = Suggestion.objects.select_related('user').filter(user=request.user, order=order).exclude(status = 'x')
                form = AddSuggestionForm({'order_id': order.id})
                template_name_posfix = 'other_order_active'
            # complete order
            elif (order.status == 'c'):
                suggestion_list = order.suggestion_set.select_related('user').filter(user = request.user).exclude(status = 'x')
                win_suggestion = get_object_or_404(order.suggestion_set.select_related('user'), status='w')
                template_name_posfix = 'other_order_complete'
            else:
                raise Http404
        
    # pagination if need
    if (need_pagination):
        suggestions = _do_paginator(request, suggestion_list)
    else:
        suggestions = suggestion_list
    
    context_info = {
        'order': order,
        'suggestions': suggestions,
        'win_suggestion': win_suggestion,
        'form': form,
        'form_del': form_del,
        'suggestion_to_del': suggestion_to_del,
    }
      
    return render_to_response(template_name % (template_name_posfix), context_info, context_instance=RequestContext(request))     

@login_required
def add_order(request, template_name='orders/add_order.djhtml'):
    if request.method == 'POST':
        order = Order(user = request.user)
        form = AddOrderForm(request.POST, instance=order) 
        if form.is_valid():
            form.save()
            messages.success(request, 'the new order was successfully added, to start receiving suggestions you need <a href="%s">to pay</a>' % (order.get_absolute_url() + "?action=pay"))
            return redirect('/orders/my')
    else:
        form = AddOrderForm()
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))

def add_suggestion(request):
    if request.user.is_authenticated() and request.method == 'POST':
        # get order id
        order_id = int(request.POST.get('order_id'))
        # add suggestion possible if order status is active ... [1] 
        order = get_object_or_404(Order, pk=order_id)
        if order.status == 'a':
            # get suggestion with trim trailing spaces
            desc = request.POST.get('desc').strip()
            form = AddSuggestionForm(request.POST)
            if form.is_valid():
                # [1] ... and order not own to current user
                if order.user != request.user:
                    # suggestion must be unique
                    if not order.suggestion_set.filter(desc=desc).exclude(status='x').exists():
                        # create suggestion from current user for order
                        order.suggestion_set.create(user=request.user, desc=desc)
                        # create suggestion message
                        # messages.success(request, 'add new suggestion success')
                    else:
                        # create not unique message
                        messages.warning(request, 'sorry, but "%s" has already been suggested' % escape(desc))
                else:
                    # warning message
                    messages.warning(request, "you can't add suggestion to your own order")
        
            else:
                for key in form.errors: 
                    for error in form.errors[key]: 
                        messages.info(request, error)
        else:
            messages.success(request, "order status is already '%s', you can't add suggestion in this case" % order.get_status_display())
            
    else:
        raise Http404
    
    return redirect(order.get_absolute_url())

@commit_on_success
def delete_order(request):
    if request.user.is_authenticated() and request.method == 'POST':
        form = DeleteOrderForm(request.POST)
        if form.is_valid():
            # get order id
            order_id = form.cleaned_data['order_id']
            # delete order possible if order own current user and order status is not paid 
            order = get_object_or_404(Order, pk=order_id, user=request.user, status='n')
            # mark order as deleted
            order.status = 'd'
            # update order
            order.save()
            # success message
            html_message = 'order <b>"%s"</b> was deleted' % escape(truncate_words(order.desc, 7))
            messages.warning(request, html_message)
        else:
            messages.error(request, 'delete order error')
    else:
        raise Http404
    
    return redirect('/orders/my')

@commit_on_success
def delete_suggestion(request):
    if request.user.is_authenticated() and request.method == 'POST':
        form = DeleteSuggestionForm(request.POST)
        if form.is_valid():
            # get suggestion id
            suggestion_id = form.cleaned_data['suggestion_id']
            # delete suggestion possible if suggestion own current user
            suggestion = get_object_or_404(Suggestion, pk=suggestion_id, user=request.user)
            # and suggestion status is new
            if suggestion.status == 'n':
                # mark suggestion as deleted
                suggestion.status = 'x'
                # update suggestion
                suggestion.save()
                # success message
                messages.warning(request, 'suggestion "%s" was deleted' % escape(suggestion.desc))
            else:
                messages.warning(request, "the status of suggestion \"%s\" is already \"%s\", so you can't delete it" % (escape(suggestion.desc), suggestion.get_status_display()))
        else:
            raise Http404
    else:
        raise Http404
    
    return redirect(suggestion.get_absolute_url())

@commit_on_success
def pay_order(request):
    if request.user.is_authenticated() and request.method == 'POST':
        form = PayOrderForm(request.POST)
        if form.is_valid():
            # get order id
            order_id = form.cleaned_data['order_id']
            # get order cost
            cost = form.cleaned_data['cost']
            
            order = get_object_or_404(Order, pk=order_id, user=request.user, status='n', cost=cost)
            account = get_object_or_404(Account, user=request.user, currency=order.currency)
            
            # pay order possible if order own current user and order's status is not paid and cost equal
            # and if account amount with according currency more or equal order's cost
            if account.amount < order.cost:
                curr = account.get_currency_display()
                account_amount = account.amount
                order_cost = order.cost 
                message_html = 'you have %(curr)s%(account_amount).2f on account, but order cost is %(curr)s%(order_cost).2f, you need <a href="/accounts/my?action=add_funds">update</a> your account to pay for this order' % vars()
                #message_html = 'you have $%.2f on account, but order cost is $%.2f, you need <a href="/accounts/my?action=add_funds">update</a> your account to pay for this order' % (account.amount, order.cost)
                messages.warning(request, message_html)
                return redirect(order.get_absolute_url())
            
            # TODO: May be it'll be better to make this with signals (like triggers in DBs). For working only with transactions. Or with overriding model save method.
            # account amount minus order cost
            account.amount = F('amount') - order.cost
            account.save()
            account = Account.objects.get(pk = account.pk)
            
            # add history entry
            account.transaction_set.create(type='p', amount=order.cost, status='o', note='Pay order')
              
            # mark order as active
            order.status = 'a'
            # update order
            order.save()
            
            # success message
            messages.success(request, "the order was successfully paid, you will start receiving suggestions soon")
        else:
            messages.error(request, 'pay order error')
    else:
        raise Http404
    
    return redirect(order.get_absolute_url())

@commit_on_success
def vote_suggestion(request):
    if request.user.is_authenticated() and request.method == 'POST':
        # get suggestion id
        suggestion_id = int(request.POST.get('suggestion_id'))
        # get vote value
        suggestion_vote = request.POST.get('suggestion_vote')
        # get suggestion
        suggestion = get_object_or_404(Suggestion, pk=suggestion_id)
        # set suggestion status if it not deleted and not win
        if suggestion.status not in ['x', 'w']:
            suggestion.status = suggestion_vote
            # update suggestion
            suggestion.save()
    else: 
        raise Http404
    
    return redirect(suggestion.get_absolute_url())

@commit_on_success
def win_suggestion(request):
    if request.user.is_authenticated() and request.method == 'POST':
        form = WinSuggestionForm(request.POST)
        if form.is_valid():
            # TODO: Need to more optimal, too much queries
            # get suggestion id
            suggestion_id = form.cleaned_data['suggestion_id']
            # get win suggestion
            suggestion = get_object_or_404(Suggestion, pk=suggestion_id)
            # get current order
            order = suggestion.order
            # get win user account with accord order's currency
            win_account = get_object_or_404(Account, user=suggestion.user, currency=order.currency)
            # win suggestion possible if order own current user
            if order.user == request.user:
                # win user account amount plus contribution from order cost (80%)
                tax = Decimal('0.80')
                
                # unique offer
                if Order.objects.filter(status='c').count() < 20:
                    tax = Decimal('1.00')
                    
                contribution = order.cost * tax
                win_account.amount = F('amount') + contribution
                win_account.save()
                win_account = Account.objects.get(pk = win_account.pk)
                
                # add history entry
                win_account.transaction_set.create(type='w', amount=contribution, status='o', note='Your suggestion win! Congratulations!')
                
                # mark win suggestion
                suggestion.status = 'w'
                # update suggestion
                suggestion.save()
                
                # congratulation message to win suggestion user
                html_message = "Congratulation! Your suggestion <a href='%s'>'%s'</a> has won! Good job! Your contribution amounts %s%.2f. We are looking forward to working with you in the future. Thank you for choosing our service!" % (suggestion.get_absolute_url(), escape(suggestion.desc), win_account.get_currency_display(), contribution)
                suggestion.user.message_set.create(message=html_message)
                
                # mark current order as complete
                order.status = 'c'
                # update order
                order.save()
                
                # success message
                html_message = 'Congratulations! Your order is complete! Thank you for choosing our service! We are looking forward for you to come back!'
                messages.success(request, html_message)
            
        else:
            raise Http404
    else:
        raise Http404
    
    return redirect(suggestion.get_absolute_url())

def _do_paginator(request, object_list, num_items=30):
    """
    Pages pagination
    """
    paginator = Paginator(object_list, num_items) # TODO: Make a Ajax pagination later
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
        
    # If page request (9999) is out of range, deliver last page of results.
    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)
        
    return objects
    
