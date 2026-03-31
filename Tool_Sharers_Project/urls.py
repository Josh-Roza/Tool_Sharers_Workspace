"""
URL configuration for Tool_Sharers_Project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from Tool_Sharers_App import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path("admin/", admin.site.urls), 
    path("", views.homePage, name="home"),
    path("add_user/", views.add_user, name="add_user"),
    path("create/", views.create_listing, name="create_listing"),
    path("edit/<int:listing_id>/", views.edit_listing, name="edit_listing"),
    path("listing/<int:listing_id>/", views.view_listing, name="view_listing"),
    path("my-listings/", views.my_listings, name="my_listings"),
    path("delete/<int:listing_id>/", views.delete_listing, name='delete_listing'),

    path("my-profile/", views.my_profile, name="my_profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("profile/<int:user_id>/", views.view_profile, name="view_profile"),
    path("report/<int:user_id>/", views.create_report, name="create_report"),
    path("delete-user/", views.delete_user, name="delete_user"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
