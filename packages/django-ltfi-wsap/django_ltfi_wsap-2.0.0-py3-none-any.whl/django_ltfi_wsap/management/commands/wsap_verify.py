from django.core.management.base import BaseCommand
from django.utils import timezone
from django_ltfi_wsap.models import WSAPEntity, DomainVerification
from ltfi_wsap import WSAPClient


class Command(BaseCommand):
    help = 'Verify WSAP domains for entities'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--entity-id',
            type=int,
            help='Specific entity ID to verify'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Verify all unverified entities'
        )
    
    def handle(self, *args, **options):
        client = WSAPClient()
        
        if options['entity_id']:
            entities = WSAPEntity.objects.filter(id=options['entity_id'])
        elif options['all']:
            entities = WSAPEntity.objects.filter(domain_verified=False)
        else:
            self.stdout.write(self.style.ERROR('Please specify --entity-id or --all'))
            return
        
        for entity in entities:
            self.stdout.write(f'Checking verification for {entity.name} ({entity.primary_domain})...')
            
            try:
                result = client.verify_domain(entity.primary_domain, entity.verification_token)
                
                if result.get('verified'):
                    entity.domain_verified = True
                    entity.verified_at = timezone.now()
                    entity.save()
                    
                    DomainVerification.objects.filter(
                        entity=entity,
                        token=entity.verification_token
                    ).update(
                        verified=True,
                        verified_at=timezone.now()
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {entity.name} domain verified!')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'✗ {entity.name} domain not verified yet')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error verifying {entity.name}: {str(e)}')
                )