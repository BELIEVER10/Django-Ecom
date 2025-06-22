from django.urls import path, include
from .import views
from .views import EsewaView



urlpatterns = [
   path('place_order/', views.place_order, name='place_order'),
   path('payments/', views.payments, name='payments'),
   path('esewaform/', EsewaView.as_view(), name='esewaform'),
   path('esewaverify/<int:order_number>/', views.esewa_verify, name='esewaverify'),
   path('payment_fail/', views.payment_fail, name='payment_fail'),
   path('download-pdf/<int:order_number>/', views.download_pdf, name='download_pdf'),
   path('workingonpayment/', views.workingonpayment, name='workingonpayment'),
   
   # path('payment_success/', views.payment_success, name='order_complete'),



   

]
    
    