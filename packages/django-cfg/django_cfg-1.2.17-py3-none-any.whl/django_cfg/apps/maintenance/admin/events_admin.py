"""
Events admin interfaces with Unfold optimization.
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
from unfold.contrib.filters.admin import AutocompleteSelectFilter, AutocompleteSelectMultipleFilter
from django_cfg import ImportExportModelAdmin, ExportMixin

from ..models import MaintenanceEvent, MaintenanceLog, CloudflareSite


class MaintenanceLogInline(TabularInline):
    """Inline for maintenance logs with Unfold styling."""
    
    model = MaintenanceLog
    verbose_name = "Log Entry"
    verbose_name_plural = "📋 Maintenance Logs"
    extra = 0
    max_num = 0
    can_delete = False
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    fields = [
        'timestamp_display', 'level_badge', 'component', 
        'operation', 'message_preview', 'user'
    ]
    readonly_fields = [
        'timestamp_display', 'level_badge', 'component',
        'operation', 'message_preview', 'user'
    ]
    
    @display(description="Time", ordering="timestamp")
    def timestamp_display(self, obj):
        """Display timestamp."""
        return obj.timestamp.strftime("%H:%M:%S")
    
    @display(description="Level", ordering="level")
    def level_badge(self, obj):
        """Display log level with colored badge."""
        colors = {
            'DEBUG': 'secondary',
            'INFO': 'info',
            'WARNING': 'warning',
            'ERROR': 'danger',
            'CRITICAL': 'danger'
        }
        color = colors.get(obj.level, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.level
        )
    
    @display(description="Message")
    def message_preview(self, obj):
        """Display truncated message."""
        if len(obj.message) > 50:
            return obj.message[:50] + "..."
        return obj.message


@admin.register(MaintenanceEvent)
class MaintenanceEventAdmin(ModelAdmin, ImportExportModelAdmin):
    """Admin for MaintenanceEvent with Unfold styling."""
    
    list_display = [
        "title_with_icon",
        "status_badge",
        "sites_count",
        "duration_display",
        "initiated_by",
        "created_at_display"
    ]
    list_display_links = ["title_with_icon"]
    search_fields = ["title", "description", "initiated_by__email"]
    list_filter = [
        "status", 
        "created_at",
        ("initiated_by", AutocompleteSelectFilter),
        ("sites", AutocompleteSelectMultipleFilter),
    ]
    ordering = ["-created_at"]
    readonly_fields = [
        "created_at", "updated_at"
    ]
    
    fieldsets = (
        ("Event Details", {
            "fields": ("title", "description", "reason", "initiated_by")
        }),
        ("Scheduling", {
            "fields": ("started_at", "ended_at", "estimated_duration", "status")
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
    inlines = [MaintenanceLogInline]
    
    # Unfold actions
    actions_detail = ["start_maintenance", "complete_maintenance", "cancel_maintenance"]
    
    @display(description="Event", ordering="title")
    def title_with_icon(self, obj):
        """Display event title with status icon."""
        icons = {
            'scheduled': '📅',
            'in_progress': '🔧',
            'completed': '✅',
            'failed': '❌',
            'cancelled': '🚫'
        }
        icon = icons.get(obj.status, '📋')
        return format_html('{} {}', icon, obj.title)
    
    @display(description="Status", ordering="status")
    def status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            'scheduled': 'info',
            'in_progress': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_status_display()
        )
    
    @display(description="Sites", ordering="sites_count")
    def sites_count(self, obj):
        """Display affected sites count."""
        count = obj.sites.count()
        if count > 0:
            return format_html(
                '<a href="{}?maintenance_events__id__exact={}" class="text-decoration-none">{} sites</a>',
                reverse('admin:django_cfg_maintenance_cloudflaresite_changelist'),
                obj.id, count
            )
        return "No sites"
    
    @display(description="Duration")
    def duration_display(self, obj):
        """Display event duration."""
        if obj.actual_start and obj.actual_end:
            duration = obj.actual_end - obj.actual_start
            hours = duration.total_seconds() / 3600
            if hours < 1:
                return f"{int(duration.total_seconds() / 60)}m"
            return f"{hours:.1f}h"
        elif obj.scheduled_start and obj.scheduled_end:
            duration = obj.scheduled_end - obj.scheduled_start
            hours = duration.total_seconds() / 3600
            if hours < 1:
                return f"{int(duration.total_seconds() / 60)}m (planned)"
            return f"{hours:.1f}h (planned)"
        return "-"
    
    @display(description="Scheduled Start", ordering="scheduled_start")
    def scheduled_start_display(self, obj):
        """Display scheduled start time."""
        if not obj.scheduled_start:
            return "-"
        return obj.scheduled_start.strftime("%Y-%m-%d %H:%M")
    
    @display(description="Created", ordering="created_at")
    def created_at_display(self, obj):
        """Display creation time."""
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    
    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        return super().get_queryset(request).select_related(
            'initiated_by', 'completed_by'
        ).prefetch_related(
            'sites'
        ).annotate(
            sites_count=Count('sites')
        )
    
    @action(
        description="🚀 Start Maintenance",
        icon="play_arrow",
        variant=ActionVariant.WARNING
    )
    def start_maintenance(self, request, object_id):
        """Start maintenance event."""
        try:
            event = MaintenanceEvent.objects.get(id=object_id)
            
            if event.status != 'scheduled':
                messages.error(request, "Only scheduled events can be started")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Start maintenance logic here
            event.status = 'in_progress'
            event.save()
            
            messages.success(
                request,
                f"Maintenance event '{event.title}' has been started"
            )
            
        except Exception as e:
            messages.error(request, f"Failed to start maintenance: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="✅ Complete Maintenance",
        icon="check_circle",
        variant=ActionVariant.SUCCESS
    )
    def complete_maintenance(self, request, object_id):
        """Complete maintenance event."""
        try:
            event = MaintenanceEvent.objects.get(id=object_id)
            
            if event.status != 'in_progress':
                messages.error(request, "Only in-progress events can be completed")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Complete maintenance logic here
            event.status = 'completed'
            event.save()
            
            messages.success(
                request,
                f"Maintenance event '{event.title}' has been completed"
            )
            
        except Exception as e:
            messages.error(request, f"Failed to complete maintenance: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="🚫 Cancel Maintenance",
        icon="cancel",
        variant=ActionVariant.DANGER
    )
    def cancel_maintenance(self, request, object_id):
        """Cancel maintenance event."""
        try:
            event = MaintenanceEvent.objects.get(id=object_id)
            
            if event.status in ['completed', 'failed']:
                messages.error(request, "Cannot cancel completed or failed events")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Cancel maintenance logic here
            event.status = 'cancelled'
            event.save()
            
            messages.success(
                request,
                f"Maintenance event '{event.title}' has been cancelled"
            )
            
        except Exception as e:
            messages.error(request, f"Failed to cancel maintenance: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    def save_model(self, request, obj, form, change):
        """Set initiated_by to current user if not set."""
        if not change:
            obj.initiated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(ModelAdmin):
    """Admin for MaintenanceLog with Unfold styling (read-only)."""
    
    list_display = [
        "timestamp_display",
        "level_badge",
        "component",
        "operation",
        "message_preview",
        "user",
        "maintenance_event_link"
    ]
    list_display_links = ["timestamp_display"]
    search_fields = ["message", "component", "operation", "user__email"]
    list_filter = [
        "level",
        "component",
        "operation",
        "timestamp",
        ("user", AutocompleteSelectFilter),
        ("maintenance_event", AutocompleteSelectFilter),
    ]
    ordering = ["-timestamp"]
    readonly_fields = [
        "timestamp", "level", "message", "component", 
        "operation", "user"
    ]
    
    def has_add_permission(self, request):
        """Disable manual log creation."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make logs read-only."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable log deletion."""
        return False
    
    @display(description="Time", ordering="timestamp")
    def timestamp_display(self, obj):
        """Display timestamp."""
        return obj.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @display(description="Level", ordering="level")
    def level_badge(self, obj):
        """Display log level with colored badge."""
        colors = {
            'DEBUG': 'secondary',
            'INFO': 'info',
            'WARNING': 'warning',
            'ERROR': 'danger',
            'CRITICAL': 'danger'
        }
        color = colors.get(obj.level, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.level
        )
    
    @display(description="Message")
    def message_preview(self, obj):
        """Display truncated message."""
        if len(obj.message) > 100:
            return obj.message[:100] + "..."
        return obj.message
    
    @display(description="Event")
    def maintenance_event_link(self, obj):
        """Display link to maintenance event."""
        if obj.maintenance_event:
            return format_html(
                '<a href="{}" class="text-decoration-none">{}</a>',
                reverse('admin:django_cfg_maintenance_maintenanceevent_change', 
                       args=[obj.maintenance_event.id]),
                obj.maintenance_event.title
            )
        return "-"
