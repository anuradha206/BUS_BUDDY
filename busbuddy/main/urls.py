from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Home
    path('', views.index, name='index'),

    # Search flow
    path('search/', views.search, name='search'),                    # search page (form)
    path('search/results/', views.search_buses, name='search_results'),  # actual results page

    # Auth
    path("login/", views.login_view, name="login"),

    #path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', views.register, name='register'),

    # Conductor
    path('conductor/register/', views.conductor_register, name='conductor_register'),
    path('conductor/dashboard/', views.conductor_dashboard, name='conductor_dashboard'),

    # Bus registration
    path('register_bus/', views.register_bus, name='register_bus'),
    path('bus/<int:pk>/details/', views.bus_details, name='bus_details'),

    # Booking + Payments
    path('start-booking/<int:schedule_id>/', views.start_booking, name='start_booking'),
    path('payment/<int:payment_id>/', views.payment_page, name='payment_page'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    path('bookings/', views.bookings, name='bookings'),
    # Static pages
    path('sectors/', views.sectors, name='sectors'),
    path('connected/', views.connected, name='connected'),
    path('who_we_are/', views.who_we_are, name='who_we_are'),
    path("logout/", views.logout_user, name="logout"),
]

# Serve media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
