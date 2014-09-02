from django import forms

# withdraw form
class WithdrawForm(forms.Form):
    PAY_SYSTEM_CHOICES = (
        # ('', '-- choose payment system --'),
        ('PayPal', 'PayPal'),
        # ('Moneybookers', 'Moneybookers'),
        # ('Perfect Money', 'Perfect Money'),
        # ('Liberty Reserve', 'Liberty Reserve'),
        
    )
    payment_system = forms.ChoiceField(choices=PAY_SYSTEM_CHOICES, help_text="<b>required field</b> | choose payment system")
    payment_account = forms.CharField(max_length=50, help_text="<b>required field</b> | carefully enter your PayPal email")
    amount = forms.DecimalField(max_digits=9, decimal_places=2, min_value=30, widget=forms.TextInput(attrs={'size': 7, 'maxlength': 7, 'style':'width: auto'}), help_text="<b>required field</b> | minimal amount to withdraw is $30.00")