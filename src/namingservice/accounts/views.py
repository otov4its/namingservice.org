from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from models import Account, Transaction
from django.db.models import F
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.transaction import commit_on_success
from forms import WithdrawForm
from django.contrib import messages

@login_required
def account(request, template_name='accounts/account_%s.djhtml'):
    # get user accounts
    accounts = Account.objects.filter(user = request.user)
    
    # get action
    action = request.GET.get('action', '')
    
    # get status
    status = request.GET.get('status', '')
    # send message if payment success
    if status == 'VALID':
        message_html = """
            <h3>the sum was successfully added</h3><p>the payment will be transferred within 24 hours</p><p>for more information check your e-mail</p>
            
            <!-- Google Code for Payment Conversion Page -->
            <script type="text/javascript">
            /* <![CDATA[ */
            var google_conversion_id = 966247864;
            var google_conversion_language = "en";
            var google_conversion_format = "2";
            var google_conversion_color = "ffffff";
            var google_conversion_label = "8xLACKDihgMQuIvfzAM";
            var google_conversion_value = 0;
            if (50) {
              google_conversion_value = 50;
            }
            /* ]]> */
            </script>
            <script type="text/javascript" src="http://www.googleadservices.com/pagead/conversion.js">
            </script>
            <noscript>
            <div style="display:inline;">
            <img height="1" width="1" style="border-style:none;" alt="" src="http://www.googleadservices.com/pagead/conversion/966247864/?value=50&amp;label=8xLACKDihgMQuIvfzAM&amp;guid=ON&amp;script=0"/>
            </div>
            </noscript>
            """    
        messages.success(request, message_html)
    
    if action == 'add_funds':
        transactions = []
        posfix = action
    else:
        # get history transactions
        posfix = 'history'
        transaction_list = Transaction.objects.select_related().filter(account__in=accounts)
        transactions = _do_paginator(request, transaction_list)
        
    context_info = {
        'accounts': accounts, 
        'transactions': transactions,
    }
    
    return render_to_response(template_name % posfix, context_info, context_instance=RequestContext(request))

# TODO: Make real add funds
@login_required
@commit_on_success
def add_funds(request):    
    """
    # temporary add funds for testing
    account = Account.objects.get(user = request.user)
    account.amount = F('amount') + 50
    account.save()
    account = Account.objects.get(pk = account.pk)
    account.transaction_set.create(type='a', amount=50, status='o', note='Test adding funds')
    return HttpResponseRedirect('/accounts/my')
    """
    pass
    

# TODO: Make real withdraw
@login_required
@commit_on_success
def withdraw(request, template_name='accounts/account_withdraw.djhtml'):
    # get user accounts
    accounts = Account.objects.filter(user = request.user)
    # get user $ account
    account = accounts.get(currency = "USD")
    if request.method == 'POST':
        form = WithdrawForm(request.POST) 
        if form.is_valid():
            payment_system = form.cleaned_data['payment_system']
            payment_account = form.cleaned_data['payment_account']
            amount = form.cleaned_data['amount']
            if account.amount >= amount:
                account.amount = F('amount') - amount
                account.save()
                account = Account.objects.get(pk = account.pk, currency = 'USD')
                transaction_note = "to %s (%s)" % (payment_system, payment_account)
                account.transaction_set.create(type='i', amount=amount, status='w', note=transaction_note)
                html_message = "the request was created, you can track its status in the account history"
                messages.success(request, html_message)
                return redirect('my_account')
            else:
                html_message = "you don't have enough money on your account to withdraw that amount"
                messages.warning(request, html_message)
    else:
        form = WithdrawForm()
         
    context_info = {
        'accounts': accounts,
        'form': form,
    }
    
    return render_to_response(template_name, context_info, context_instance=RequestContext(request))

def _do_paginator(request, object_list, num_items=10):
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

