from django.urls import path
from .views import send_drawing, index, convert_to_latex

urlpatterns = [
    path('', index, name='index'),
    path('api/send_drawing/', send_drawing, name='send_drawing'),
    path('convert_to_latex/', convert_to_latex, name='convert_to_latex'),
]