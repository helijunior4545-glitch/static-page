from django.contrib.auth import views as auth_views
from django.urls import path
from contacts import views
urlpatterns = [
    path("", views.contact, name="contact"),
    path("healthz", views.health, name="health"),
    path("equipe/", views.inbox, name="inbox"),
    path("equipe/login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("equipe/sair/", auth_views.LogoutView.as_view(), name="logout"),
]
