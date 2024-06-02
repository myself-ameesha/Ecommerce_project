from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact', views.contact, name='contact'),
    path('shopcart', views.shopcart, name='shopcart'),
    path('checkout', views.checkout, name='checkout'),
    path('wishlist', views.wishlist, name='wishlist'),
    path('register/', views.register, name='register'),
    path('loginn/', views.loginn, name='loginn'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    #path('otp/<str:uid>/', views.otpVerify, name='otp'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('add_address/', views.add_address, name='add_address'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('return_order/', views.return_order, name='return_order'),
    path('cancel_orderr/<str:order_number>/', views.cancel_orderr, name='cancel_orderr'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('change_password/', views.change_password, name='change_password'),
    path('user_wallet/',views.user_wallet,name='user_wallet'),

]   