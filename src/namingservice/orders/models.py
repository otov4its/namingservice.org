from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import truncate_words

class Order(models.Model):
    user = models.ForeignKey(User)
    desc = models.CharField(max_length=1000, verbose_name="description", help_text="<b>required field</b> | enter your order description here")
    keywords = models.CharField(max_length=255, blank=True, help_text="optional field | enter order's keywords here,  it'll be useful for contributors to narrow the range of suggestions")
    restrictions = models.CharField(max_length=255, blank=True, help_text="optional field | if you want to set limits, please, write them down")
    note = models.CharField(max_length=255, blank=True, help_text="optional field | enter any additional information, that you consider to be useful")
    error_messages = {
        'min_value': u"don't be so stingy, set a good cost and contributors' answer will be simply beautiful",
        'max_value': u"it seems you are very generous, but please set the lower price and the remaining amount spend on good deeds",
    }
    cost = models.DecimalField(max_digits=9, decimal_places=2, default=50, validators=[MinValueValidator(10), MaxValueValidator(99999)], error_messages=error_messages, help_text="<b>required field</b> | minimal order cost is 10.00")
    STATUS_CHOICES = (
        ('a', 'active'),
        ('c', 'complete'),
        ('n', 'not paid'),
        ('d', 'delete'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='n')
    crdate = models.DateTimeField(auto_now_add=True)
    chdate = models.DateTimeField(auto_now=True)
    lang = models.CharField(max_length=2, default='en')
    CURRENCY_CHOICES = (
        ('USD', '$'),
        ('MMM', 'MMM$'),
    )
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD', help_text="<b>required field</b> | select order's currency ($ or MMM$)")
    
    def __unicode__(self):
        return u'%s: %s($%s)' % (self.user, truncate_words(self.desc, 3), self.cost)
    
    def get_absolute_url(self):
        return "/orders/id/%i/" % self.id    
    
    class Meta:
        ordering = ["-cost"]
    
class Suggestion(models.Model):
    user = models.ForeignKey(User)
    order = models.ForeignKey(Order)
    desc = models.CharField(max_length=255)
    STATUS_CHOICES = (
        ('n', 'new'),
        ('l', 'like'),
        ('d', 'dislike'),
        ('w', 'win'),
        ('s', 'seen'),
        ('x', 'delete'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='n')
    crdate = models.DateTimeField(auto_now_add=True)
    chdate = models.DateTimeField(auto_now=True) 
    
    
    def __unicode__(self):
        return u'%s' % self.user
    
    def get_absolute_url(self):
        return "/orders/id/%i/" % self.order_id
    
    class Meta:
        ordering = ["-crdate"]
        