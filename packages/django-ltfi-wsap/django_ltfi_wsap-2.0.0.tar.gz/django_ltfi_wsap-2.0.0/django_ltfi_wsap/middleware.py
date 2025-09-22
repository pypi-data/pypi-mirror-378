"""
Django middleware for LTFI-WSAP integration
"""

from django.conf import settings
from django.http import JsonResponse
from ltfi_wsap import WSAPClient


class WSAPMiddleware:
    """
    Middleware to handle WSAP-specific endpoints and headers
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.client = WSAPClient(
            api_key=getattr(settings, 'LTFI_WSAP_API_KEY', None),
            base_url=getattr(settings, 'LTFI_WSAP_BASE_URL', 'https://api.ltfi.ai')
        )
    
    def __call__(self, request):
        # Handle .well-known/wsap.json endpoint
        if request.path == '/.well-known/wsap.json':
            return self.handle_wsap_endpoint(request)
        
        # Add WSAP headers to response
        response = self.get_response(request)
        
        # Add WSAP-specific headers if configured
        if getattr(settings, 'LTFI_WSAP_ADD_HEADERS', True):
            response['X-WSAP-Enabled'] = 'true'
            response['X-WSAP-Version'] = '2.0'
        
        return response
    
    def handle_wsap_endpoint(self, request):
        """
        Handle requests to /.well-known/wsap.json
        """
        # Get the domain from the request
        domain = request.get_host().split(':')[0]
        
        try:
            # Try to get WSAP data for this domain
            from .models import WSAPEntity
            entity = WSAPEntity.objects.filter(
                primary_domain=domain,
                domain_verified=True
            ).first()
            
            if entity:
                wsap_data = entity.generate_wsap_json()
                return JsonResponse(wsap_data, json_dumps_params={'indent': 2})
            else:
                return JsonResponse({
                    "error": "No verified WSAP entity for this domain"
                }, status=404)
        except Exception as e:
            return JsonResponse({
                "error": str(e)
            }, status=500)