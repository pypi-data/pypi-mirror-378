"""
Deployments admin interfaces with Unfold optimization.
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

from ..models import CloudflareDeployment


@admin.register(CloudflareDeployment)
class CloudflareDeploymentAdmin(ModelAdmin, ImportExportModelAdmin):
    """Admin for CloudflareDeployment with Unfold styling."""
    
    list_display = [
        "deployment_with_icon",
        "site_link",
        "deployment_type_badge",
        "status_badge",
        "worker_name_display",
        "created_at_display",
        "deployed_at_display"
    ]
    list_display_links = ["deployment_with_icon"]
    search_fields = ["site__name", "site__domain", "worker_name", "script_name"]
    list_filter = [
        "deployment_type",
        "status",
        "created_at",
        "deployed_at",
        ("site", AutocompleteSelectFilter),
        ("maintenance_event", AutocompleteSelectFilter),
    ]
    ordering = ["-created_at"]
    readonly_fields = [
        "deployed_at", "created_at"
    ]
    
    fieldsets = (
        ("Deployment Information", {
            "fields": ("site", "deployment_type", "maintenance_event")
        }),
        ("Worker Configuration", {
            "fields": ("worker_name", "script_name", "script_content"),
            "classes": ("collapse",)
        }),
        ("Cloudflare Details", {
            "fields": ("worker_id", "script_id", "deployment_config"),
            "classes": ("collapse",)
        }),
        ("Status & Logs", {
            "fields": ("status", "deployed_at", "deployment_logs"),
            "classes": ("collapse",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )
    
    # Unfold actions
    actions_detail = ["deploy_worker", "undeploy_worker", "view_logs"]
    
    @display(description="Deployment", ordering="worker_name")
    def deployment_with_icon(self, obj):
        """Display deployment with status icon."""
        icons = {
            'pending': '⏳',
            'deploying': '🚀',
            'deployed': '✅',
            'failed': '❌',
            'undeployed': '🗑️'
        }
        icon = icons.get(obj.status, '📦')
        name = obj.worker_name or obj.script_name or f"Deployment #{obj.id}"
        return format_html('{} {}', icon, name)
    
    @display(description="Site")
    def site_link(self, obj):
        """Display site with link."""
        return format_html(
            '<a href="{}" class="text-decoration-none">🌐 {}</a>',
            reverse('admin:django_cfg_maintenance_cloudflaresite_change', 
                   args=[obj.site.id]),
            obj.site.name
        )
    
    @display(description="Type", ordering="deployment_type")
    def deployment_type_badge(self, obj):
        """Display deployment type with colored badge."""
        colors = {
            'maintenance_page': 'warning',
            'redirect': 'info',
            'custom_worker': 'primary',
            'error_page': 'danger'
        }
        color = colors.get(obj.deployment_type, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_deployment_type_display()
        )
    
    @display(description="Status", ordering="status")
    def status_badge(self, obj):
        """Display status with colored badge."""
        colors = {
            'pending': 'secondary',
            'deploying': 'info',
            'deployed': 'success',
            'failed': 'danger',
            'undeployed': 'warning'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_status_display()
        )
    
    @display(description="Worker")
    def worker_name_display(self, obj):
        """Display worker name or script name."""
        if obj.worker_name:
            return obj.worker_name
        elif obj.script_name:
            return format_html('<em>{}</em>', obj.script_name)
        else:
            return format_html('<span class="text-muted">Auto-generated</span>')
    
    @display(description="Created", ordering="created_at")
    def created_at_display(self, obj):
        """Display creation time."""
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    
    @display(description="Deployed", ordering="deployed_at")
    def deployed_at_display(self, obj):
        """Display deployment time."""
        if not obj.deployed_at:
            return format_html('<span class="text-muted">Not deployed</span>')
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.deployed_at
        
        if diff < timedelta(hours=1):
            color = "success"
        elif diff < timedelta(days=1):
            color = "info"
        else:
            color = "secondary"
        
        return format_html(
            '<span class="text-{}">{}</span>',
            color, obj.deployed_at.strftime("%Y-%m-%d %H:%M")
        )
    
    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related(
            'site', 'maintenance_event'
        )
    
    @action(
        description="🚀 Deploy Worker",
        icon="rocket_launch",
        variant=ActionVariant.SUCCESS
    )
    def deploy_worker(self, request, object_id):
        """Deploy Cloudflare Worker."""
        try:
            deployment = CloudflareDeployment.objects.get(id=object_id)
            
            if deployment.status == 'deployed':
                messages.warning(request, "Worker is already deployed")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Deploy worker logic here (placeholder)
            deployment.status = 'deploying'
            deployment.save()
            
            messages.success(
                request,
                f"Deployment started for {deployment.site.name}"
            )
            
        except Exception as e:
            messages.error(request, f"Deployment failed: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="🗑️ Undeploy Worker",
        icon="delete",
        variant=ActionVariant.DANGER
    )
    def undeploy_worker(self, request, object_id):
        """Undeploy Cloudflare Worker."""
        try:
            deployment = CloudflareDeployment.objects.get(id=object_id)
            
            if deployment.status != 'deployed':
                messages.warning(request, "Worker is not currently deployed")
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Undeploy worker logic here (placeholder)
            deployment.status = 'undeployed'
            deployment.save()
            
            messages.success(
                request,
                f"Worker undeployed for {deployment.site.name}"
            )
            
        except Exception as e:
            messages.error(request, f"Undeployment failed: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="📋 View Logs",
        icon="description",
        variant=ActionVariant.INFO
    )
    def view_logs(self, request, object_id):
        """View deployment logs."""
        try:
            deployment = CloudflareDeployment.objects.get(id=object_id)
            
            # This would typically redirect to a logs view
            # For now, just show a message
            messages.info(
                request,
                f"Logs for deployment {deployment.id} would be displayed here"
            )
            
        except Exception as e:
            messages.error(request, f"Failed to retrieve logs: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
