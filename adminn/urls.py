from django.urls import path
from . import views

app_name = 'adminn'  # Namespace for admin URLs


urlpatterns = [
    #path('products/', views.product_list, name='product_list'),
    #path('addproducts',views.add_product, name='add_product'),
    path('adminhome/',views.adminhome, name='adminhome'),
    path('users/', views.users, name='users'),
    path('addproduct/', views.addproduct, name='addproduct'),
    path('productlist/', views.productlist, name='productlist'),
    path('deleteproduct/<int:product_id>/', views.deleteproduct, name = 'deleteproduct'),
    path('editproduct/<int:product_id>/', views.editproduct, name = 'editproduct'),
    path('product/image/<int:image_id>/delete/', views.delete_product_image, name='delete_product_image'),
    path('categorylist/', views.categorylist, name='categorylist'),
    path('addcategory/', views.addcategory, name='addcategory'),
    path('editcategory/<int:category_id>/', views.editcategory, name='editcategory'),
    path('deletecategory/<int:category_id>/', views.deletecategory, name='deletecategory'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('orderlist/', views.orderlist, name='orderlist'),
    path('cancelorder/<int:order_id>/', views.cancelorder, name='cancelorder'),
    path('order_detaill/<int:order_id>/', views.order_detaill, name='order_detaill'),
    path('coupon/', views.coupon, name='coupon'),
    path('add_coupon/', views.add_coupon, name='add_coupon'),
    path('edit/coupon/<int:coupon_id>/',views.edit_coupon,name='edit_coupon'),
    path('delete/coupon/<int:coupon_id>/',views.delete_coupon,name='delete_coupon'),
   

    path('sales_report/', views.sales_report, name='sales_report'),
    path('sales/daily/', views.sales_report, {'period': 'daily'}, name='daily_sales_report'),
    path('sales/weekly/', views.sales_report, {'period': 'weekly'}, name='weekly_sales_report'),
    path('sales/monthly/', views.sales_report, {'period': 'monthly'}, name='monthly_sales_report'),
    path('sales/yearly/', views.sales_report, {'period': 'yearly'}, name='yearly_sales_report'),
    path('sales/custom/', views.sales_report, {'period': 'custom'}, name='custom_sales_report'),
   
    path('sales_report/pdf/', views.download_sales_reportpdf, name='download_sales_reportpdf'),
    path('sales_report/excel/', views.download_sales_reportexcel, name='download_sales_reportexcel'),

    path('custom_admin_homepage/', views.custom_admin_homepage, name='custom_admin_homepage'),

]
