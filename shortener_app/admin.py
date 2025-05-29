
from django.contrib import admin
from django.shortcuts import redirect
from .models import URL , SiteConfiguration, AdUnit

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'long_url', 'clicks', 'created_at') # Columns to display in list view
    list_filter = ('created_at',) # Filters sidebar
    search_fields = ('short_code', 'long_url') # Fields to search by
    readonly_fields = ('short_code', 'clicks', 'created_at') # These fields cannot be edited manually


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('ads_enabled_globally',) # Just show the ad toggle

    # Override methods to ensure only one instance can be added/deleted via admin
    def has_add_permission(self, request):
        # Allow adding if no instance exists, otherwise disallow
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Disallow deleting the configuration
        return False

    # Optional: Customize the admin page to always show the single instance directly
    def changelist_view(self, request, extra_context=None):
        if not SiteConfiguration.objects.exists():
            # If no config exists, redirect to the add form
            return redirect('admin:%s_%s_add' % (self.model._meta.app_label, self.model._meta.model_name))
        else:
            # If config exists, redirect to its change form
            config = SiteConfiguration.objects.first()
            return redirect('admin:%s_%s_change' % (self.model._meta.app_label, self.model._meta.model_name), config.pk)

@admin.register(AdUnit)
class AdUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active', 'created_at')
    list_filter = ('location', 'is_active')
    search_fields = ('name', 'ad_code')
    list_editable = ('is_active',) # Allows toggling active status directly from list view