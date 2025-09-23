"""
Admin interface for MonitoringTarget model with Unfold features.
"""

from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import redirect
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.enums import ActionVariant
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from import_export.admin import ImportExportModelAdmin

from ..models import MonitoringTarget
from ..services import MaintenanceManager
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(MonitoringTarget)
class MonitoringTargetAdmin(ModelAdmin, ImportExportModelAdmin):
    """Admin for MonitoringTarget with Unfold styling."""
    
    list_display = [
        "site_with_icon",
        "url_display", 
        "status_badge",
        "last_check_display",
        "check_interval_display",
        "failure_count_display"
    ]
    list_display_links = ["site_with_icon", "url_display"]
    search_fields = ["site__name", "site__domain", "check_url"]
    list_filter = [
        "status",
        "check_interval", 
        "failure_threshold",
        "last_check_at",
        ("site", AutocompleteSelectFilter),
    ]
    ordering = ["-last_check_at"]
    readonly_fields = [
        "last_check_at", "status", "last_check_success",
        "created_at", "updated_at"
    ]
    
    fieldsets = (
        ("Target Configuration", {
            "fields": ("site", "check_url", "status")
        }),
        ("Monitoring Settings", {
            "fields": ("check_interval", "timeout", "expected_status_codes", "failure_threshold", "recovery_threshold")
        }),
        ("Response Validation", {
            "fields": ("expected_content", "expected_response_time_ms"),
            "classes": ("collapse",)
        }),
        ("Status Information", {
            "fields": ("consecutive_failures", "consecutive_successes", "last_check_at", "last_check_success"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )
    
    # Unfold actions
    actions_detail = ["run_health_check", "enable_monitoring", "disable_monitoring"]
    
    @display(description="Site", ordering="site__name")
    def site_with_icon(self, obj):
        """Display site name with icon."""
        return format_html('🌐 {}', obj.site.name)
    
    @display(description="URL", ordering="check_url")
    def url_display(self, obj):
        """Display monitoring URL."""
        url = obj.check_url
        if len(url) > 50:
            url = url[:47] + "..."
        return format_html('<code>{}</code>', url)
    
    @display(
        description="Status",
        ordering="status",
        label={
            'active': 'success',
            'paused': 'warning', 
            'disabled': 'secondary',
            'error': 'danger'
        }
    )
    def status_badge(self, obj):
        """Display monitoring status."""
        return obj.status, obj.get_status_display()
    
    @display(description="Last Check", ordering="last_check_at")
    def last_check_display(self, obj):
        """Display last check time."""
        if obj.last_check_at:
            return obj.last_check_at.strftime("%Y-%m-%d %H:%M")
        return "Never"
    
    @display(description="Check Interval", ordering="check_interval")
    def check_interval_display(self, obj):
        """Display check interval in human readable format."""
        seconds = obj.check_interval
        if seconds >= 3600:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
        elif seconds >= 60:
            return f"{seconds // 60}m"
        return f"{seconds}s"
    
    @display(description="Failures", ordering="consecutive_failures")
    def failure_count_display(self, obj):
        """Display failure count with threshold."""
        return f"{obj.consecutive_failures}/{obj.failure_threshold}"
    
    def get_queryset(self, request):
        """Filter queryset based on user permissions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(site__owner=request.user)

    def save_model(self, request, obj, form, change):
        """Set owner to current user if not set."""
        if not change and not obj.site.owner:
            obj.site.owner = request.user
        super().save_model(request, obj, form, change)
    
    @action(
        description="🩺 Run Health Check",
        icon="health_and_safety",
        variant=ActionVariant.INFO
    )
    def run_health_check(self, request, object_id):
        """Run immediate health check."""
        try:
            target = self.get_object(request, object_id)
            if not target:
                messages.error(request, "Monitoring target not found.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # TODO: Implement actual health check logic
            messages.success(
                request, 
                f"Health check queued for {target.check_url}."
            )
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Health check failed for target {object_id}")
            messages.error(
                request, 
                f"Health check failed: {e}"
            )
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="▶️ Enable Monitoring",
        icon="play_arrow",
        variant=ActionVariant.SUCCESS
    )
    def enable_monitoring(self, request, object_id):
        """Enable monitoring for target."""
        try:
            target = self.get_object(request, object_id)
            if not target:
                messages.error(request, "Monitoring target not found.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            target.status = MonitoringTarget.Status.ACTIVE
            target.save(update_fields=['status'])
            
            messages.success(
                request, 
                f"Monitoring enabled for {target.check_url}."
            )
            
        except Exception as e:
            messages.error(request, f"Failed to enable monitoring: {e}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="⏸️ Disable Monitoring",
        icon="pause",
        variant=ActionVariant.WARNING
    )
    def disable_monitoring(self, request, object_id):
        """Disable monitoring for target."""
        try:
            target = self.get_object(request, object_id)
            if not target:
                messages.error(request, "Monitoring target not found.")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            target.status = MonitoringTarget.Status.DISABLED
            target.save(update_fields=['status'])
            
            messages.success(
                request, 
                f"Monitoring disabled for {target.check_url}."
            )
            
        except Exception as e:
            messages.error(request, f"Failed to disable monitoring: {e}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))