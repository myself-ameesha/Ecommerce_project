from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile, Address
from django.utils.html import format_html

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display=('email','first_name','last_name','username','last_login','date_joined','is_active')
    list_display_links=('email','first_name','last_name')
    readonly_fields=('last_login','date_joined')
    ordering=('date_joined',)


    filter_horizontal=()
    list_filter=()
    fieldsets=()


class AddressAdmin(admin.ModelAdmin):
    list_display = ('street_address', 'city', 'state', 'country', 'phone_number')

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.profile_picture:  # Check if profile_picture exists
            return format_html('<img src="{}" width="30" style="border-radius: 50%;">'.format(obj.profile_picture.url))
        else:
            return "No Image"  # Or you can return a default placeholder image

admin.site.register(Account,AccountAdmin)
admin.site.register(UserProfile,UserProfileAdmin) 
admin.site.register(Address, AddressAdmin)



