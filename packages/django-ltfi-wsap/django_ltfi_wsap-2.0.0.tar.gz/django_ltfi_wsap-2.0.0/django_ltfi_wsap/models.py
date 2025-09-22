from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class WSAPEntity(models.Model):
    """Model representing a WSAP Entity in Django"""
    
    ENTITY_TYPES = [
        ('COMPANY', _('Company')),
        ('NON_PROFIT', _('Non-Profit')),
        ('GOVERNMENT', _('Government')),
        ('PERSONAL', _('Personal Brand')),
        ('AI_AGENT', _('AI Agent')),
        ('OPEN_SOURCE', _('Open Source Project')),
    ]
    
    DISCLOSURE_LEVELS = [
        ('BASIC', _('Basic')),
        ('STANDARD', _('Standard')),
        ('DETAILED', _('Detailed')),
        ('COMPLETE', _('Complete')),
    ]
    
    # Core fields
    wsap_id = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES)
    
    # Domain verification
    primary_domain = models.CharField(max_length=255, validators=[URLValidator()])
    domain_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Disclosure settings
    disclosure_level = models.CharField(
        max_length=20, 
        choices=DISCLOSURE_LEVELS,
        default='BASIC'
    )
    
    # Relationships
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='wsap_entities'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # JSON fields for flexible data
    wsap_data = models.JSONField(default=dict, blank=True)
    encrypted_fields = models.JSONField(default=list, blank=True)
    
    class Meta:
        verbose_name = _('WSAP Entity')
        verbose_name_plural = _('WSAP Entities')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.entity_type})"
    
    def generate_wsap_json(self):
        """Generate WSAP JSON for this entity"""
        from ltfi_wsap import WSAPClient
        
        client = WSAPClient()
        return client.generate_wsap(self.wsap_id)


class DomainVerification(models.Model):
    """Track domain verification attempts"""
    
    VERIFICATION_METHODS = [
        ('DNS_TXT', _('DNS TXT Record')),
        ('FILE_UPLOAD', _('File Upload')),
        ('META_TAG', _('HTML Meta Tag')),
    ]
    
    entity = models.ForeignKey(
        WSAPEntity,
        on_delete=models.CASCADE,
        related_name='verification_attempts'
    )
    domain = models.CharField(max_length=255)
    method = models.CharField(max_length=20, choices=VERIFICATION_METHODS)
    token = models.CharField(max_length=255)
    verified = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Domain Verification')
        verbose_name_plural = _('Domain Verifications')
        ordering = ['-attempted_at']
    
    def __str__(self):
        status = "" if self.verified else ""
        return f"{status} {self.domain} ({self.method})"