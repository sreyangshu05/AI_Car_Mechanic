from django.urls import path
from .views import BookingCreateView, BookingDetailView
urlpatterns = [path('', BookingCreateView.as_view(), name='booking-create'), path('<int:booking_id>/', BookingDetailView.as_view(), name='booking-detail')]
