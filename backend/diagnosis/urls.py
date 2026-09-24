from django.urls import path
from .views import DiagnosisView
urlpatterns = [path('', DiagnosisView.as_view(), name='diagnosis')]
