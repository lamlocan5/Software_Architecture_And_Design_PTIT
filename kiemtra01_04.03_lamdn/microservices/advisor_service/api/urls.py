from django.urls import path
from . import views

urlpatterns = [
    path('',                views.info,            name='advisor-info'),
    path('track/',          views.track,           name='advisor-track'),
    path('chat/',           views.chat,            name='advisor-chat'),
    path('history/',        views.chat_history,    name='advisor-history'),
    path('recommendations/',views.recommendations, name='advisor-recommendations'),
    path('kb/rebuild/',     views.kb_rebuild,      name='advisor-kb-rebuild'),
]
