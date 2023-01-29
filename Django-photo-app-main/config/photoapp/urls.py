'''Photoapp URL patterns'''

from django.urls import path

from . import views
from .views import (PhotoCreateView, PhotoDeleteView, PhotoDetailView,
                    PhotoListView, PhotoTagListView, PhotoUpdateView)

app_name = 'photo'

urlpatterns = [
    path('', PhotoListView.as_view(), name='list'),

    path('tag/<slug:tag>/', PhotoTagListView.as_view(), name='tag'),

    path('photo/<int:pk>/', PhotoDetailView.as_view(), name='detail'),

    path('photo/create/', PhotoCreateView.as_view(), name='create'),

    path('photo/<int:pk>/update/', PhotoUpdateView.as_view(), name='update'),

    path('photo/<int:pk>/delete/', PhotoDeleteView.as_view(), name='delete'),
    
    path('search/', views.search_view, name='search'),
]
