from django.urls import path
from .views import ConversationDetailView

urlpatterns = [path('<uuid:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail')]
