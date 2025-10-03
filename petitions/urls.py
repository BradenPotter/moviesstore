from django.urls import path
from . import views

urlpatterns = [
    path("", views.petition_list, name="petition_list"),
    path("new/", views.petition_new, name="petition_new"),
    path('<int:id>/vote/', views.petition_vote, name='petition_vote')
]