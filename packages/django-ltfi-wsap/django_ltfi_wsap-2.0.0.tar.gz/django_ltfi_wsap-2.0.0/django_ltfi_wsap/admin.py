from django.contrib import admin
from .models import WSAPEntity, DomainVerification


@admin.register(WSAPEntity)
class WSAPEntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'entity_type', 'primary_domain', 'domain_verified', 'disclosure_level', 'owner', 'created_at']
    list_filter = ['entity_type', 'domain_verified', 'disclosure_level', 'created_at']
    search_fields = ['name', 'primary_domain', 'wsap_id']
    readonly_fields = ['wsap_id', 'verification_token', 'verified_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'entity_type', 'owner')
        }),
        ('Domain & Verification', {
            'fields': ('primary_domain', 'domain_verified', 'verification_token', 'verified_at')
        }),
        ('WSAP Configuration', {
            'fields': ('wsap_id', 'disclosure_level', 'wsap_data', 'encrypted_fields')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(DomainVerification)
class DomainVerificationAdmin(admin.ModelAdmin):
    list_display = ['domain', 'entity', 'method', 'verified', 'attempted_at', 'verified_at']
    list_filter = ['method', 'verified', 'attempted_at']
    search_fields = ['domain', 'entity__name', 'token']
    readonly_fields = ['attempted_at', 'verified_at']
    
    def has_add_permission(self, request):
        # Verifications should be created through the API
        return False