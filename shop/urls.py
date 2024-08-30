from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'), 
    path('products', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'), 
    path('logout/confirm/', views.logout_confirm, name='logout_confirm'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('admin/approve-order/<int:order_id>/', views.approve_order, name='approve_order'),
    path('admin/orders/', views.order_list, name='order_list'),
    path('admin/approve-order/<int:order_id>/', views.approve_order, name='approve_order'),
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('admin/reject-order/<int:order_id>/', views.reject_order, name='reject_order'),
    path('category/<int:category_id>/', views.product_list_by_category, name='product_list_by_category'),
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
