from django.contrib import admin

from .models import User, ChangePasswordEmailConfirmation, EmailCode

admin.site.register(User)
admin.site.register(ChangePasswordEmailConfirmation)
admin.site.register(EmailCode)
