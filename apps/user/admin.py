from django.contrib import admin

from apps.user.models import ContactMe, Subscribe


class ContactMeAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'name', 'email', 'user', 'reviewed')
    list_editable = ('reviewed',)
    search_fields = ('name', 'email', 'user__username', 'user__first_name', 'user__last_name')
    ordering = ['date']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'email', 'user', 'subscribed')
    list_editable = ('subscribed',)
    search_fields = ('email', 'user__username', 'user__first_name', 'user__last_name')
    ordering = ['date']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


admin.site.register(ContactMe, ContactMeAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
