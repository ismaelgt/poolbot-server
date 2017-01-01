from django.contrib import admin
from .models import Match


class MatchAdmin(admin.ModelAdmin):
    """
    Custom admin model to skip around the default delete action
    calling bulk delete and bypassing the delete() method.
    """

    actions=['delete_and_updated_denormalized_selected']

    def get_actions(self, request):
        actions = super(MatchAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_and_updated_denormalized_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        if queryset.count() == 1:
            message_bit = "1 match entry was"
        else:
            message_bit = "%s match entries were" % queryset.count()
        self.message_user(request, "%s successfully deleted and all denormalized fields updated." % message_bit)
    delete_and_updated_denormalized_selected.short_description = "Delete selected entries via delete()"


admin.site.register(Match, MatchAdmin)