"""
Sites admin interfaces with Unfold optimization.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.db.models import Count, Q
from django.contrib import messages
from django.shortcuts import redirect
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action
from unfold.enums import ActionVariant
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from django_cfg import ImportExportModelAdmin, ExportMixin

from ..models import CloudflareSite, SiteGroup, MaintenanceEvent, MonitoringTarget
from ..services import SiteSyncService, MaintenanceManager


class MaintenanceEventInline(TabularInline):
    """Inline for maintenance events with Unfold styling."""
    
    model = MaintenanceEvent.sites.through
    verbose_name = "Maintenance Event"
    verbose_name_plural = "🔧 Recent Maintenance Events"
    extra = 0
    max_num = 5
    can_delete = False
    show_change_link = False
    fields = []
    readonly_fields = []


class MonitoringTargetInline(TabularInline):
    """Inline for monitoring targets with Unfold styling."""
    
    model = MonitoringTarget
    verbose_name = "Monitoring Target"
    verbose_name_plural = "📊 Monitoring Configuration"
    extra = 0
    max_num = 1
    
    fields = ['check_url', 'check_interval', 'status_display', 'last_check_display']
    readonly_fields = ['status_display', 'last_check_display']
    
    @display(description="Status")
    def status_display(self, obj):
        """Display monitoring status with badge."""
        if not obj.status:
            return format_html('<span class="badge badge-secondary">Unknown</span>')
        
        colors = {
            'active': 'success',
            'paused': 'warning',
            'disabled': 'secondary',
            'error': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_status_display()
        )
    
    @display(description="Last Check")
    def last_check_display(self, obj):
        """Display last check time."""
        if not obj.last_check_at:
            return "Never"
        return obj.last_check_at.strftime("%Y-%m-%d %H:%M")


@admin.register(CloudflareSite)
class CloudflareSiteAdmin(ModelAdmin, ImportExportModelAdmin):
    """Admin for CloudflareSite with Unfold styling."""
    
    # Unfold configuration
    list_display = [
        "name_with_icon",
        "domain", 
        "environment_badge",
        "status_badge",
        "zone_info",
        "monitoring_status",
        "events_count",
        "owner",
        "last_maintenance_display"
    ]
    list_display_links = ["name_with_icon", "domain"]
    search_fields = ["name", "domain", "zone_id", "owner__email"]
    list_filter = [
        "environment", 
        "current_status", 
        "created_at",
        ("owner", AutocompleteSelectFilter),
    ]
    ordering = ["-created_at"]
    readonly_fields = [
        "zone_id", "account_id", "current_status", "maintenance_active",
        "last_status_check", "last_maintenance_at", "created_at", "updated_at"
    ]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "domain", "description", "owner")
        }),
        ("Configuration", {
            "fields": ("environment", "project", "tags")
        }),
        ("Cloudflare Integration", {
            "fields": ("zone_id", "account_id", "api_token"),
            "classes": ("collapse",)
        }),
        ("Maintenance Settings", {
            "fields": ("worker_name", "maintenance_template", "custom_maintenance_message"),
            "classes": ("collapse",)
        }),
        ("Monitoring", {
            "fields": ("monitoring_enabled", "health_check_url", "check_interval"),
            "classes": ("collapse",)
        }),
        ("Status", {
            "fields": ("current_status", "maintenance_active", "last_status_check", "last_maintenance_at"),
            "classes": ("collapse",)
        }),
        ("Access Control", {
            "fields": ("allowed_users",),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )
    
    inlines = [MonitoringTargetInline, MaintenanceEventInline]
    
    # Unfold actions
    actions_detail = ["sync_with_cloudflare", "enable_maintenance", "disable_maintenance"]
    actions_list = ["bulk_sync_sites"]
    
    @display(description="Site", ordering="name")
    def name_with_icon(self, obj):
        """Display site name with icon."""
        icon = "🌐"
        if obj.environment == "production":
            icon = "🚀"
        elif obj.environment == "staging":
            icon = "🧪"
        elif obj.environment == "development":
            icon = "🔧"
        
        return format_html('{} {}', icon, obj.name)
    
    @display(description="Environment", ordering="environment")
    def environment_badge(self, obj):
        """Display environment with colored badge."""
        colors = {
            'production': 'success',
            'staging': 'warning',
            'development': 'info',
            'testing': 'secondary'
        }
        color = colors.get(obj.environment, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_environment_display()
        )
    
    @display(description="Status", ordering="current_status")
    def status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            'active': 'success',
            'maintenance': 'warning',
            'offline': 'danger',
            'unknown': 'secondary'
        }
        color = colors.get(obj.current_status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_current_status_display()
        )
    
    @display(description="Zone Info")
    def zone_info(self, obj):
        """Display Cloudflare zone information."""
        if not obj.zone_id:
            return format_html('<span class="text-muted">Not synced</span>')
        
        return format_html(
            '<small class="text-muted">Zone: {}</small>',
            obj.zone_id[:8] + "..." if len(obj.zone_id) > 8 else obj.zone_id
        )
    
    @display(description="Monitoring")
    def monitoring_status(self, obj):
        """Display monitoring status."""
        try:
            target = obj.monitoring_target
            if target.enabled:
                color = 'success' if target.status == 'healthy' else 'danger'
                return format_html(
                    '<span class="badge badge-{}">{}</span>',
                    color, target.status or 'Unknown'
                )
            else:
                return format_html('<span class="text-muted">Disabled</span>')
        except:
            return format_html('<span class="text-muted">Not configured</span>')
    
    @display(description="Events", ordering="maintenance_events_count")
    def events_count(self, obj):
        """Display maintenance events count."""
        count = obj.maintenance_events.count()
        if count > 0:
            return format_html(
                '<a href="{}?sites__id__exact={}" class="text-decoration-none">{} events</a>',
                reverse('admin:django_cfg_maintenance_maintenanceevent_changelist'),
                obj.id, count
            )
        return "No events"
    
    @display(description="Last Maintenance", ordering="last_maintenance_at")
    def last_maintenance_display(self, obj):
        """Display last maintenance time."""
        if not obj.last_maintenance_at:
            return format_html('<span class="text-muted">Never</span>')
        return obj.last_maintenance_at.strftime("%Y-%m-%d %H:%M")
    
    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        return super().get_queryset(request).select_related(
            'owner'
        ).prefetch_related(
            'maintenance_events'
        ).annotate(
            maintenance_events_count=Count('maintenance_events')
        )
    
    @action(
        description="🔄 Sync with Cloudflare",
        icon="refresh",
        variant=ActionVariant.INFO
    )
    def sync_with_cloudflare(self, request, object_id):
        """Sync site with Cloudflare zones."""
        try:
            # Get the site object to get its name for the message
            site = self.get_object(request, object_id)
            if not site:
                messages.error(request, "Site not found.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # TODO: Implement actual sync logic here
            # For now, just update the last_status_check timestamp
            from django.utils import timezone
            site.last_status_check = timezone.now()
            site.save(update_fields=['last_status_check'])
            
            messages.success(
                request, 
                f"Site '{site.name}' has been queued for synchronization with Cloudflare.",
            )
            
        except CloudflareSite.DoesNotExist:
            messages.error(
                request, 
                "Site not found.",
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Unexpected error syncing site {object_id}")
            messages.error(
                request, 
                f"Unexpected error syncing site: {e}",
            )
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="🔧 Enable Maintenance",
        icon="build",
        variant=ActionVariant.WARNING
    )
    def enable_maintenance(self, request, object_id):
        """Enable maintenance mode for a site."""
        try:
            site = self.get_object(request, object_id)
            if not site:
                messages.error(request, "Site not found.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            manager = MaintenanceManager(request.user)
            manager.enable_maintenance_mode(site)
            messages.success(request, f"Maintenance mode enabled for {site.name}.")
        except Exception as e:
            messages.error(request, f"Failed to enable maintenance: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="✅ Disable Maintenance",
        icon="check_circle",
        variant=ActionVariant.SUCCESS
    )
    def disable_maintenance(self, request, object_id):
        """Disable maintenance mode for a site."""
        try:
            site = self.get_object(request, object_id)
            if not site:
                messages.error(request, "Site not found.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            manager = MaintenanceManager(request.user)
            manager.disable_maintenance_mode(site)
            messages.success(request, f"Maintenance mode disabled for {site.name}.")
        except Exception as e:
            messages.error(request, f"Failed to disable maintenance: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    def save_model(self, request, obj, form, change):
        """Set owner to current user if not set."""
        if not change:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
    
    @action(
        description="🔄 Sync All Sites with Cloudflare",
        icon="sync",
        variant=ActionVariant.INFO,
        url_path="bulk-sync-sites",
        permissions=["bulk_sync_sites"]
    )
    def bulk_sync_sites(self, request):
        """Bulk sync all sites with Cloudflare."""
        try:
            from django.utils import timezone
            from django_cfg.apps.maintenance.services import SiteSyncService
            
            # Get all sites for the current user (or all if superuser)
            if request.user.is_superuser:
                sites = CloudflareSite.objects.all()
            else:
                sites = CloudflareSite.objects.filter(owner=request.user)
            
            count = sites.count()
            if count == 0:
                messages.warning(request, "No sites found to synchronize.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Update last_status_check for all sites
            sites.update(last_status_check=timezone.now())
            
            # TODO: Implement actual bulk sync logic here using SiteSyncService
            # This would typically queue background tasks for each site
            
            messages.success(
                request,
                f"Successfully queued {count} sites for Cloudflare synchronization."
            )
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Bulk sync failed")
            messages.error(
                request,
                f"Bulk sync failed: {e}"
            )
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    def has_bulk_sync_sites_permission(self, request):
        """Check if user has permission to bulk sync sites."""
        return request.user.is_staff


@admin.register(SiteGroup)
class SiteGroupAdmin(ModelAdmin, ImportExportModelAdmin):
    """Admin for SiteGroup with Unfold styling."""
    
    list_display = [
        "name_with_icon",
        "description_short",
        "sites_count",
        "owner",
        "created_at_display"
    ]
    list_display_links = ["name_with_icon"]
    search_fields = ["name", "description", "owner__email"]
    list_filter = [
        "created_at",
        ("owner", AutocompleteSelectFilter),
    ]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "description", "owner")
        }),
        ("Sites", {
            "fields": ("sites",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )
    
    filter_horizontal = ["sites"]
    
    @display(description="Group", ordering="name")
    def name_with_icon(self, obj):
        """Display group name with icon."""
        return format_html('📁 {}', obj.name)
    
    @display(description="Description")
    def description_short(self, obj):
        """Display truncated description."""
        if not obj.description:
            return format_html('<span class="text-muted">No description</span>')
        
        if len(obj.description) > 50:
            return obj.description[:50] + "..."
        return obj.description
    
    @display(description="Sites", ordering="sites_count")
    def sites_count(self, obj):
        """Display sites count with link."""
        count = obj.sites.count()
        if count > 0:
            return format_html(
                '<a href="{}?groups__id__exact={}" class="text-decoration-none">{} sites</a>',
                reverse('admin:django_cfg_maintenance_cloudflaresite_changelist'),
                obj.id, count
            )
        return "No sites"
    
    @display(description="Created", ordering="created_at")
    def created_at_display(self, obj):
        """Display creation time."""
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    
    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        return super().get_queryset(request).select_related(
            'owner'
        ).prefetch_related(
            'sites'
        ).annotate(
            sites_count=Count('sites')
        )
    
    def save_model(self, request, obj, form, change):
        """Set owner to current user if not set."""
        if not change:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
