from django.urls import path,include
from .import views

urlpatterns = [
    path("adminlogin/", views.adminLogin,name = 'adminlogin'), 
    path("dashboard/", views.adminHome,name = 'dashboard'), 
    path("user_management/", views.user_management,name = 'user_management'), 
    path("block/<int:id>", views.block,name = 'block'), 
    path("unblock/<int:id>", views.block,name = 'unblock'),     

    path("category_management/", views.category_management,name = 'category_management'), 
    path("add_category/", views.add_category,name = 'add_category'), 
    path("edit_category/<int:id>", views.edit_category,name = 'edit_category'), 
    path("delete_category/<int:id>'", views.delete_category,name = 'delete_category'), 

    path("subcategory/'", views.sub_category,name = 'subcategory'), 
    path("add_subcategory/'", views.add_sub_cat,name = 'add_subcategory'), 
    path("edit_subcategory/<int:id>", views.edit_sub_cat,name = 'edit_subcategory'), 
    path("delete_subcategory/<int:id>'", views.delete_sub_cat,name = 'delete_subcategory'), 

    path("product_management/", views.product_management,name = 'product_management'), 
    path("add_product/", views.add_product,name = 'add_product'),  
    path("edit_product/<int:id>", views.edit_product,name = 'edit_product'),
    path("delete_product/<int:id>", views.delete_product,name = 'delete_product'),
    
    path("adminlogout/", views.adminLogout,name = 'adminlogout'),   

    path("order_management/", views.order_management,name = 'order_management'), 
    path("coupon_management/", views.coupon_management,name = 'coupon_management'), 
    path("add_coupon/", views.add_coupon,name = 'add_coupon'),
    path("delivery_status/<int:id>", views.delivery_status,name = 'delivery_status'),
    path("get_subcategories/", views.get_subcategories,name = 'get_subcategories'),
    path("banner_management/", views.banner_management,name = 'banner_management'),
    path("add_banner/", views.add_banner,name = 'add_banner'),
    path("delete_banner/<int:id>", views.delete_banner,name = 'delete_banner'),
    path("edit_banner/<int:id>", views.edit_banner,name = 'edit_banner'),
    path("sales_excel_report/", views.sales_excel_report,name = 'sales_excel_report'),
    path("sales/", views.sales,name = 'sales'),
    path("sales_csv_report/", views.sales_csv_report,name = 'sales_csv_report'),
    path("sales_filter/", views.sales_filter,name = 'sales_filter'),
    path("delete_coupon/<int:id>", views.delete_coupon,name = 'delete_coupon'),
    ]