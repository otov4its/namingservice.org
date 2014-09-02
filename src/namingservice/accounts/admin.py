from django.contrib import admin
from namingservice.accounts.models import Account, Transaction

class TransactionInline(admin.TabularInline):
    model = Transaction
    readonly_fields = ('date', )

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency')
    inlines = [TransactionInline, ]

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'date', 'type', 'amount', 'status', 'note')
    readonly_fields = ('date', )

admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction, TransactionAdmin)

