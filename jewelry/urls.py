from django.contrib import admin
from django.urls import path,include
from home.views import *
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path
from home.admin import ReportAdmin

 # Import the custom admin site



urlpatterns = [
    
    path('', home, name='home'),
    path('login/',user_login,name='login'),
    path('register/',register,name='register'),
    path('profile/',profile,name='profile'),
    
    path('order-detail/<int:order_id>',orderdetail,name='order-detail'),
    path('address/', adress,name='address'),
    path('forget/',forget,name='forget'),
    path('wishlist/',wishlist,name='wishlist'),
    path("change-password/", change_password, name="change_password"),
    path("logout/",logout_view,name='logout'),
   
    path('add_to_wishlist/<int:product_id>/',add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('category/<slug:slug>',category_view,name='category'),
    path('category/subcategory/<slug:subcategory_slug>/',subcategory,name='subcategory'),
    path('productGrid/', productGrid, name='productGrid'),
    path('productDetail/<slug:product_slug>/', product_detail, name='productDetail'),
    path('category/<slug:subcategory_slug>/', category_products, name='category_products'),
   
    path('cart_page/', cart_page, name='cart_page'),
    path('add_to_cart/<int:getid>',add_to_cart,name='add_to_cart'),
    path('remove-from-cart/<int:getid>/', remove_from_cart, name='remove_from_cart'),

    
    # path('blogs/<str:blog_name>/', blog_detail, name='blog_detail'),  # Dynamic blog pages
    path('checkout/', checkout, name='checkout'),
    # path("create-order/", create_order, name="create_order"),
    path('payment_success/', payment_success, name='payment_success'),
    path('addadres/', add_address, name='addadres'),
    path("subscribe/", subscribe, name="subscribe"),
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
   
    path('search/', search_results, name='search_results'),
    
    
    path('term/', term, name='term'),
    path('blog/', blog, name='blog'),
    path('blog1/', blog1, name='blog1'),
    path('blog2/', blog2, name='blog2'),
    path('blog3/', blog3, name='blog3'),
    path('blog4/', blog4, name='blog4'),
    path('blog5/', blog5, name='blog5'),
    path('blog6/', blog6, name='blog6'),
    path('faqs/',faq, name='faqs'),
    path('about/',about, name='about'),
    path('apply_coupon/',apply_coupon,name='apply_coupon'),
    path('placeorder/',placeorder,name='placeorder'),
    path('proceed-to-pay/',razorpaycheck),
    path('productDetail/<slug:product_slug>/feedback/', submit_feedback, name='submit_feedback'),
    path('order/', my_orders,name='order'),
    path("track-order/<str:tracking_no>/", get_order_tracking, name="track_order"),
    path("admin/home/report/generate_report/", ReportAdmin.generate_report, name="generate_report"),
    
    
    
    

    path('admin/', admin.site.urls),
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
