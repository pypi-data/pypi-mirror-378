from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from ltfi_wsap import WSAPClient
from .models import WSAPEntity, DomainVerification
import json


@login_required
def entity_dashboard(request):
    """Dashboard view for managing WSAP entities"""
    entities = WSAPEntity.objects.filter(owner=request.user)
    return render(request, 'django_ltfi_wsap/dashboard.html', {
        'entities': entities
    })


@login_required
@require_http_methods(["POST"])
def create_entity(request):
    """Create a new WSAP entity"""
    data = json.loads(request.body)
    
    entity = WSAPEntity.objects.create(
        owner=request.user,
        name=data['name'],
        entity_type=data['entity_type'],
        primary_domain=data['primary_domain'],
        disclosure_level=data.get('disclosure_level', 'BASIC'),
        wsap_data=data.get('wsap_data', {})
    )
    
    # Initialize with WSAP API
    client = WSAPClient()
    wsap_response = client.entities.create({
        'name': entity.name,
        'type': entity.entity_type,
        'domain': entity.primary_domain,
        'disclosure_level': entity.disclosure_level
    })
    
    entity.wsap_id = wsap_response['id']
    entity.save()
    
    return JsonResponse({
        'id': entity.id,
        'wsap_id': entity.wsap_id,
        'name': entity.name
    })


@login_required
@require_http_methods(["POST"])
def verify_domain(request, entity_id):
    """Initiate domain verification"""
    entity = get_object_or_404(WSAPEntity, id=entity_id, owner=request.user)
    data = json.loads(request.body)
    
    method = data.get('method', 'DNS_TXT')
    
    # Generate verification token
    import secrets
    token = f"wsap-verify={secrets.token_urlsafe(32)}"
    
    # Create verification record
    verification = DomainVerification.objects.create(
        entity=entity,
        domain=entity.primary_domain,
        method=method,
        token=token
    )
    
    # Return instructions based on method
    instructions = {}
    if method == 'DNS_TXT':
        instructions = {
            'method': 'DNS_TXT',
            'record_type': 'TXT',
            'record_name': '_wsap',
            'record_value': token,
            'instructions': f'Add a TXT record named "_wsap" with value "{token}" to your DNS'
        }
    elif method == 'FILE_UPLOAD':
        instructions = {
            'method': 'FILE_UPLOAD',
            'file_path': '/.well-known/wsap-verify.txt',
            'file_content': token,
            'instructions': f'Upload a file to {entity.primary_domain}/.well-known/wsap-verify.txt containing: {token}'
        }
    elif method == 'META_TAG':
        instructions = {
            'method': 'META_TAG',
            'tag': f'<meta name="wsap-verification" content="{token}">',
            'instructions': f'Add this meta tag to your homepage: <meta name="wsap-verification" content="{token}">'
        }
    
    entity.verification_token = token
    entity.save()
    
    return JsonResponse({
        'verification_id': verification.id,
        'token': token,
        'instructions': instructions
    })


@login_required
@require_http_methods(["POST"])
def check_verification(request, entity_id):
    """Check if domain verification is complete"""
    entity = get_object_or_404(WSAPEntity, id=entity_id, owner=request.user)
    
    # Use WSAP client to verify
    client = WSAPClient()
    result = client.verify_domain(entity.primary_domain, entity.verification_token)
    
    if result.get('verified'):
        entity.domain_verified = True
        entity.verified_at = timezone.now()
        entity.save()
        
        # Update verification record
        DomainVerification.objects.filter(
            entity=entity,
            token=entity.verification_token
        ).update(
            verified=True,
            verified_at=timezone.now()
        )
    
    return JsonResponse({
        'verified': entity.domain_verified,
        'verified_at': entity.verified_at.isoformat() if entity.verified_at else None
    })


@csrf_exempt
def wsap_json_endpoint(request):
    """
    Public endpoint for WSAP JSON
    Serves at /.well-known/wsap.json
    """
    domain = request.get_host().split(':')[0]
    
    try:
        entity = WSAPEntity.objects.get(
            primary_domain=domain,
            domain_verified=True
        )
        
        wsap_data = entity.generate_wsap_json()
        return JsonResponse(wsap_data, json_dumps_params={'indent': 2})
    except WSAPEntity.DoesNotExist:
        return JsonResponse({
            'error': 'No verified WSAP entity for this domain'
        }, status=404)