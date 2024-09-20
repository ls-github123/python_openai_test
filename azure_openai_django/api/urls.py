from django.urls import path
from api.views import ChatView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
]