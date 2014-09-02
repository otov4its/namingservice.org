from namingservice.orders.models import Order
from django import forms
import re, urllib2
import pywhois
from pywhois.parser import PywhoisError

# add order form
class AddOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('desc', 'keywords', 'restrictions', 'note', 'currency','cost')
        widgets = {
            'desc': forms.Textarea(attrs={'rows': 5}),
            'keywords': forms.TextInput(attrs={'size': 56}),
            'restrictions': forms.Textarea(attrs={'cols': 55, 'rows': 3}),
            'note': forms.Textarea(attrs={'cols': 55, 'rows': 5}),
            'cost': forms.TextInput(attrs={'size': 7, 'maxlength': 7, 'style':'width: auto'}),
        }

# add suggestion form
class AddSuggestionForm(forms.Form):
    # hidden field with order id
    order_id = forms.IntegerField(widget=forms.HiddenInput)
    # suggestion field
    error_messages = {
        'required': u'you can not send an empty suggestion, just turn on your imagination and write an amazing one',
        'max_length': u'the length of suggestion can not be longer than 255 characters',
    }
    desc = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'style':'width: 88%'}), error_messages=error_messages)
    
    # custom validation for domain names
    def clean_desc(self):
        data = self.cleaned_data['desc'].strip()
        # url regexp
        regex = re.compile(                           
            r'^(https?://)?' # http:// or https://
            r'(?P<domain>(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        match = regex.search(data)
        # if suggestion is url expect that for the domain name order
        if match:
            domain = match.group('domain')
            already_registered = False
            # first try open url
            try:
                urllib2.urlopen('http://%s' % domain)    
            # if url not open try perform whois, may be domain already registered
            except:
                try:
                    whois = pywhois.whois(domain)
                    if whois.status:
                        already_registered = True
                except PywhoisError:
                    already_registered = False
                except:
                    raise forms.ValidationError("sorry, but domain <b>%s</b> is invalid" % domain)
            # if url open hence domain name already registered
            else:
                already_registered = True
            
            if already_registered:
                raise forms.ValidationError("sorry, but domain <b>%s</b> has been already registered, you can suggest only not registered domains" % domain) 
                                
        return data
    
# delete order form
class DeleteOrderForm(forms.Form):
    # only one hidden field with order id
    order_id = forms.IntegerField(widget=forms.HiddenInput)

# delete suggestion form
class DeleteSuggestionForm(forms.Form):
    # only one hidden field with suggestion id
    suggestion_id = forms.IntegerField(widget=forms.HiddenInput)

# win suggestion form
class WinSuggestionForm(forms.Form):
    # only one hidden field with win suggestion id
    suggestion_id = forms.IntegerField(widget=forms.HiddenInput)
    
# pay order form
class PayOrderForm(forms.Form):
    # hidden field with order id
    order_id = forms.IntegerField(widget=forms.HiddenInput)
    # hidden field with order cost
    cost = forms.DecimalField(max_digits=9, decimal_places=2, min_value=10, widget=forms.HiddenInput)
    

