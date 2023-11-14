from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy as Token

from .models import MyUser


admin.site.unregister(Group)
admin.site.unregister(Token)


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email',
                    'first_name', 'last_name', 'is_blocked')
    list_filter = ('email', 'username')

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

    def block_user(self, request, queryset):
        for user in queryset:
            user.is_blocked = True
            user.save()

    actions = [block_user]
