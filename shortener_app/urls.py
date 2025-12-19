from django.urls import path
from . import views # Import views from the current app
from .views import api_shorten

urlpatterns = [ # <--- Ensure this is a list []
    # URL for the homepage where users shorten links
    path('', views.create_short_url, name='create_short_url'),

    # URL for the waiting page: e.g., http://127.0.0.1:8000/abcdef/
    path('<str:short_code>/', views.redirect_to_download, name='redirect_to_download'),

    # URL for the final redirect after the timer: e.g., http://127.0.0.1:8000/download/abcdef/finalize/
    path('download/<str:short_code>/finalize/', views.finalize_download, name='finalize_download'),
    path("api/shorten/", api_shorten, name="api_shorten"),
]

