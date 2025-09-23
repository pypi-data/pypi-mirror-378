"""
Base views for maintenance app.

Common functionality and mixins for maintenance views.
"""

import logging
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class MaintenancePermissionMixin:
    """Mixin for maintenance app permissions."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_user_queryset(self, model_class, owner_field='owner'):
        """Get queryset filtered by user permissions."""
        if getattr(self, 'swagger_fake_view', False):
            return model_class.objects.none()
        
        user = self.request.user
        if user.is_staff:
            return model_class.objects.all()
        
        # Use dynamic field lookup
        filter_kwargs = {owner_field: user}
        return model_class.objects.filter(**filter_kwargs)


class MaintenanceResponseMixin:
    """Mixin for standardized API responses."""
    
    def success_response(self, message, data=None):
        """Return standardized success response."""
        response_data = {
            'success': True,
            'message': message
        }
        if data is not None:
            response_data['data'] = data
        return Response(response_data)
    
    def error_response(self, error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
        """Return standardized error response."""
        logger.error(f"API Error: {error}")
        return Response({
            'success': False,
            'error': str(error)
        }, status=status_code)
    
    def validation_error_response(self, errors):
        """Return standardized validation error response."""
        return Response({
            'success': False,
            'error': 'Validation failed',
            'errors': errors
        }, status=status.HTTP_400_BAD_REQUEST)
