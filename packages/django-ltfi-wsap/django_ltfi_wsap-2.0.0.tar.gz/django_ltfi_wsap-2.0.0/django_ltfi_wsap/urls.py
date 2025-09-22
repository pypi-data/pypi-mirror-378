from django.urls import path
from . import views

app_name = 'ltfi_wsap'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.entity_dashboard, name='dashboard'),
    
    # Entity management
    path('entity/create/', views.create_entity, name='create_entity'),
    path('entity/<int:entity_id>/verify/', views.verify_domain, name='verify_domain'),
    path('entity/<int:entity_id>/check-verification/', views.check_verification, name='check_verification'),
    
    # Public WSAP endpoint
    path('.well-known/wsap.json', views.wsap_json_endpoint, name='wsap_json'),
]