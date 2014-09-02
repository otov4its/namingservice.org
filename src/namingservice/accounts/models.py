from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Account(models.Model):
    user = models.ForeignKey(User)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    CURRENCY_CHOICES = (
        ('USD', '$'),
        ('MMM', 'MMM$'),
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    
    def __unicode__(self):
        return u'%s' % self.user

# Create user accounts in $ and MMM$ by Django User model post_save signal
def create_account(sender, **kwargs):
    if kwargs['created']:
        Account.objects.create(user=kwargs['instance'], currency='USD')
        Account.objects.create(user=kwargs['instance'], currency='MMM')
        
post_save.connect(create_account, sender=User, dispatch_uid="create_account_only_once")
    
class Transaction(models.Model):
    account = models.ForeignKey(Account)
    date = models.DateTimeField(auto_now_add=True)
    TYPE_CHOICES = (
        ('a', 'add funds'),
        ('p', 'pay order'),
        ('w', 'win suggestion'),
        ('i', 'withdraw'),
    )
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    STATUS_CHOICES = (
        ('o', 'ok'),
        ('w', 'wait'),
        ('e', 'error'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    note = models.CharField(max_length=100, blank=True)
    
    def __unicode__(self):
        return u'%s' % self.account
    
    class Meta:
        ordering = ["-date"]
    