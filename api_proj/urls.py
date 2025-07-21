from django.urls import path
from .views import AIView, HistoryView


urlpatterns = [
    path('ai/generate/', AIView.as_view(), name='ai_view'),
    path('ai/info/', AIView.as_view(), name='ai_info'),
    path('history/', HistoryView.as_view(), name='history_view'),
]