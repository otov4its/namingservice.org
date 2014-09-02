from django.contrib import admin
from namingservice.orders.models import Order, Suggestion

class SuggestionInline(admin.TabularInline):
    model = Suggestion

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'desc', 'cost', 'currency','crdate')
    inlines = [SuggestionInline, ]

class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'desc', 'status', 'crdate', 'chdate')

admin.site.register(Order, OrderAdmin)
admin.site.register(Suggestion, SuggestionAdmin)

