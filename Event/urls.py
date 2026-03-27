"""
URL configuration for Event project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from app1 import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
path('admin/', admin.site.urls),
path('', views.index),
path('adminPage/', views.admin),
path('delete/<int:id>/', views.delete),
path('update/<int:id>/', views.update),
path('about/', views.about),
path('logOut/', views.logOut),
path('addCategory/', views.addCategory),
path("viewCategory/", views.viewCategory, name="viewCategory"),
path("deleteCategory/<int:id>/", views.deleteCategory, name="deleteCategory"),
path("updateCategory/<int:id>/", views.updateCategory, name="updateCategory"),
path('choosePlan/<int:id>/', views.choosePlan, name='choosePlan'),
path('viewRequest/', views.viewRequest),
path('approve/<int:id>/', views.approve),
path("reject/<int:id>/", views.reject, name="reject"),
path('myEvent/', views.myEvent),
# path('payment/<int:id>/<str:event_name>/<str:pr>/', views.payment),
path('history/', views.payment_history),
path("viewUser/", views.viewUser, name="viewUser"),
path("mainPage/", views.mainPage, name="mainPage"),
path("update-plan-order/", views.update_plan_order, name="update_plan_order"),
path('register/', views.register, name='register'),
path('verify-otp/', views.verify_otp, name='verify_otp'),
path('resend-otp/', views.resend_otp, name='resend_otp'),
path('login/', views.login, name='login'),
path("login-otp/", views.login_otp_page, name="login-otp"),
path('api/send-otp/', views.send_login_otp, name='send-otp'),
path('api/verify-otp/', views.verify_login_otp, name='verify-otp'),
path("api/register-send-otp/",views.register_send_otp),
path("api/register-verify-otp/",views.register_verify_otp),
path("forget/", views.forget_password_page, name="forget_password"),
path("api/send-forget-otp/", views.send_forget_otp),
path("api/verify-forget-otp/", views.verify_forget_otp),
path("api/reset-password/", views.reset_password),
path('customizePlan/', views.customizePlan, name='customizePlan'),
path('adminCustomizations/', views.viewCustomizations),
path('addCustomization/', views.addCustomization),
path('updateCustomization/<int:id>/', views.updateCustomization),
path('deleteCustomization/<int:id>/', views.deleteCustomization),
path('updateCustomizationOrder/', views.updateCustomizationOrder),
path("pay-advance/<int:booking_id>/", views.pay_advance),
path("pay-balance/<int:booking_id>/", views.pay_balance),
path("refund-advance/<int:booking_id>/", views.refund_advance),
path('viewRefunds/', views.viewRefunds, name='viewRefunds'),



]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)