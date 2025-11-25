from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_results, name='search_results'),
    path('login/', auth_views.LoginView.as_view(
        template_name='main/login.html',
        redirect_authenticated_user=True),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', views.register, name='register'),
    path('bus_register/', views.bus_register, name='bus_register'),

    # Removed: path('bookings/', include('bookings.urls'))

    path('sectors/', views.sectors, name='sectors'),
    path('connected/', views.connected, name='connected'),
    path('who_we_are/', views.who_we_are, name='who_we_are'),
    path('bus/<int:pk>/details/', views.bus_details, name='bus_details'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'),
        name='password_reset'
    ),
    path('register_bus/', views.register_bus, name='register_bus'),
    path('conductor/register/', views.conductor_register, name='conductor_register'),
    # bookings search served here:
    path('bookings/', views.search_buses, name='bookings'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
