from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    
    path("product_detail/<int:id>/",views.single_product,name='product_detail'),
    path("add_to_cartcart/<int:id>/",views.add_to_cart,name='add_to_cart'),
    path("view_cart/",views.view_cart,name='view_cart'),
    path("checkout/",views.checkout,name='checkout'),
    path("update_quantity/",views.update_quantity,name='update_quantity'),
    path("check_stock/",views.check_stock,name='check_stock'),
    path("remove_cart/<int:id>/",views.remove_cart,name='remove_cart'),
    path("save_details/",views.save_details,name='save_details'),
    path("place_order/",views.place_order,name='place_order'),
    path("profile/",views.profile,name='profile'),
    path("invoice/<int:id>/",views.invoice,name='invoice'),
    path("proceed_to_pay/",views.proceed_to_pay,name='proceed_to_pay'),
    path("order_remove/<int:id>/",views.order_remove,name='order_remove'),
    path("add_to_wishlist/<int:id>/",views.add_to_wishlist,name='add_to_wishlist'),
    path("product_list_by_category/<int:id>/",views.product_list_by_category,name='product_list_by_category'),
    path("apply_coupon/",views.apply_coupon,name='apply_coupon'),
    path("product_view_sorting/",views.product_view_sorting,name='product_view_sorting'),
    path("success/",views.success,name='success'),
    path("set_address/",views.set_address,name='set_address'),
    path("wishlist/",views.wishlist,name='wishlist'),
    path("remove_item/<int:id>/",views.remove_item,name='remove_item'),
    path("order_deatails/",views.order_deatails,name='order_deatails'),
    path("order_cancel/<int:id>/",views.order_cancel,name='order_cancel'),
    path("order_return/<int:id>/",views.order_return,name='order_return'),
    path("address_list/",views.address_list,name='address_list'),
    path("delete_address/<int:id>",views.delete_address,name='delete_address'),
    path("edit_address/<int:address_id>",views.edit_address,name='edit_address'),
    path("contact/",views.contact,name='contact'),
    path("blog/",views.blog,name='blog'),
    path("order_confirmation/",views.order_confirmation,name='order_confirmation'),
    path("search/",views.search,name='search'),
]