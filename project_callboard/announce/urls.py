from django.urls import path
from .views import *

urlpatterns = [
    path('', NoteList.as_view(), name='list'),
    path('create/', NoteCreate.as_view(), name='note_create'),
    path('<int:pk>', notedetail, name="Note"),
    path('response/', response, name="Response"),
    ]