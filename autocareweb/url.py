from . import views 
from .views import  delete_customer, service_manager_list, delete_service_manager
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('',views.home,name='home'),
    path('about',views.about,name='about'), 
    path('contact',views.contact,name='contact'),
    path('customerLogin',views.cust_login,name='customerLogin'),
    path('customerRegister',views.cust_register,name='customerRegister'),
    path('logout',views.logout_view,name="logout"),
    path('location',views.location,name="location"),
    path('price',views.price),
    path('service',views.service,name="service"),
    path('booking',views.booking,name="booking"),

    path('complaints/submit/', views.receive_complaint, name='submit_complaint'),
    path('complaints/', views.complaint_list, name='complaint_list'),

    

    #///////////////  Vehicle Select /////////////
    path('select-vehicle/', views.select_vehicle, name='select_vehicle'),
    path('add_vehicle_number/<int:variant_id>/', views.add_vehicle_number, name='add_vehicle_number'),
    path('vehicle-brand/', views.vehicle_brand, name='vehicle_brand'),

    # URL for displaying variants of a selected brand
    # path('brand-variants/<int:brand_id>/', views.brand_variants, name='brand_variants'),
    path('brand/<int:brand_id>/variants/', views.vehicle_variants, name='vehicle_variants'),

    #////////////////// Services For Customers ///////////////////////
    
     path('service/service-categories/', views.customer_service_category, name='customer_service_category'),
    # Customer view for service types of a specific category
    path('service/service-types/<int:category_id>/', views.customer_service_type, name='customer_service_type'),

    #////////////////// Service Cart /////////////////////////////////

    path('add_to_cart/<int:service_type_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),

    #/////////////////////   Oreder Items ///////////////////////////
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
    path('create_order/', views.create_order, name='create_order'),

    path('my-orders/', views.my_orders, name='my_orders'),



    #///////////////   Password Reset///////////////////////

    path('password-reset/', 
        views.CustomPasswordResetView.as_view(
            template_name='password/password_reset.html',
            email_template_name='password/password_reset_email.html',
            subject_template_name='password/password_reset_subject.txt'
        ),
        name='password_reset'),
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='password/password_reset_done.html'
        ),
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password/password_reset_confirm.html'
        ),
        name='password_reset_confirm'),
    path('password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password/password_reset_complete.html'
        ),
        name='password_reset_complete'),


        #///////////////////  change password ///////////////////
    path('change-password/', views.change_password, name='change_password'),


    #/////////Admin Dashboard///////////
    path('cst_admin',views.cst_admin,name="cst_admin"),
    # path('all-orders/', views.all_orders, name='all_orders'),
    path('customerdetails',views.customerdetails,name = 'customerdetails'),
    path('delete_customer/<str:email>/',delete_customer, name='delete_customer'),
    path('service_manager_list/', service_manager_list, name='service_manager_list'),
    path('delete_service_manager/<str:email>/', delete_service_manager, name='delete_service_manager'),
    path('add_service_manager/', views.add_service_manager, name='add_service_manager'),
    # path('mechanic_list/', views.mechanic_list, name='mechanic_list'),

    # path('mechanics/update_level/<int:mechanic_id>/', views.update_mechanic_level, name='update_mechanic_level'),

    # path('delete_mechanic/<str:email>/', views.delete_mechanic, name='delete_mechanic'),
    # path('add_mechanic/', views.add_mechanic, name='add_mechanic'),

    path('mechanic_list/', views.mechanic_list, name='mechanic_list'),
    path('mechanics/update_level/<int:mechanic_id>/', views.update_mechanic_level, name='update_mechanic_level'),
    path('delete_mechanic/<str:email>/', views.delete_mechanic, name='delete_mechanic'),
    path('add_mechanic/', views.add_mechanic, name='add_mechanic'),
    path('mechanic_profile/<str:email>/', views.mechanic_profile, name='mechanic_profile'),  # New URL for profile
    path('mechanic/<int:mechanic_id>/edit/', views.edit_mechanic_profile, name='edit_mechanic_profile'),


    path('cst_admin/vehicle-make/create/', views.create_vehicle_make, name='create_vehicle_make'),
    path('cst_admin/vehicle-model/create/', views.create_vehicle_model, name='create_vehicle_model'),
    path('cst_admin/manage_vehicle', views.manage_vehicle, name='manage_vehicle'),
    path('brands/<int:brand_id>/add_variant/', views.add_vehicle_model, name='add_variant'),
    path('cst_admin/manage_vehicle/<int:brand_id>/brand_variants/', views.brand_variants, name='brand_variants'),
    path ('cst_admin/addSlot/', views.manageSlot ,name='addslot'),
    # path ('cst_admin/slot_list/', views.Slotlist ,name='slot_list'),
    path('cst_admin/slots/', views.slot_list, name='slot_list'),
    path('allocate-manager/<slug:slug>/', views.allocate_manager, name='allocate_manager'),


    #/////////// Service Manager /////////////////////////////////////////

    path('serviceManager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/allocate_mechanic/<slug:slot_slug>/', views.allocate_mechanic, name='allocate_mechanic'),
    path('remove-mechanic/', views.remove_mechanic, name='remove_mechanic'),


    #///////////////////   Mechanics ////////////////////////////////////////
    # path('mechanic',views.mechanic_dashboard,name="mechanic"),
    # path('add-junior-mechanic/<int:slot_id>/', views.add_junior_mechanic, name='add_junior_mechanic'),
    # path('remove-junior-mechanic/<int:slot_id>/<int:junior_mechanic_id>/', views.remove_junior_mechanic, name='remove_junior_mechanic'),
 
    path('mechanic-dashboard/', views.mechanic_dashboard, name='mechanic_dashboard'),
    path('allocate_juniormechanic/', views.allocate_juniormechanic, name='allocate_juniormechanic'),
    path('add-junior-mechanic/<int:slot_id>/', views.add_junior_mechanic, name='add_junior_mechanic'),
    path('remove-junior-mechanic/<int:slot_id>/<int:junior_mechanic_id>/', views.remove_junior_mechanic, name='remove_junior_mechanic'),
    path('update-order-status/', views.update_order_status, name='update_order_status'),


    #////////////////////// Service Categories/////////////////////////////////
    path('cst_admin/service-categories/', views.service_category_list, name='service_category_list'),
    path('cst_admin/service-categories/edit/<int:pk>/', views.edit_service_category, name='edit_service_category'),
    path('cst_admin/service-categories/delete/<int:pk>/', views.delete_service_category, name='delete_service_category'),

    #////////////////   Service Types /////////////////////////////////////
    path('cst_admin/service-categories/<int:category_id>/service-types/', views.service_type_list, name='service_type_list'),
    path('cst_admin/service-types/edit/<int:pk>/', views.edit_service_type, name='edit_service_type'),
    path('cst_admin/service-types/delete/<int:pk>/', views.delete_service_type, name='delete_service_type'),

    #///////////////////////   Service Price ///////////////////////////////////////
    path('cst_admin/service_price/brands/', views.brands, name='brands'),
    path('cst_admin/service_price/brands/<int:make_id>/variants/', views.variants, name='variants'),
    path('cst_admin/service_price/variants/<int:variant_id>/categories/', views.service_category, name='service_category'),
    path('cst_admin/service_price/categories/<int:category_id>/variants/<int:variant_id>/types/', views.service_type, name='service_type'),
    path('cst_admin/service_price/types/<int:service_type_id>/variants/<int:variant_id>/add_price/', views.add_service_price, name='add_service_price'),
    path('cst_admin/edit_service_price/<int:service_price_id>/', views.edit_service_price, name='edit_service_price'),
   
    #////////////////////   CUSTOMER PROFILE ///////////////
     path('customer_profile/', views.customer_profile, name='customer_profile'),
      path('profile/edit/', views.edit_profile, name='edit_profile'),

    #///////////////  Job Portal /////////////////////////////////////
    path('serviceManager/dashboard/post-job/', views.post_job, name='post_job'),
    path('jobs/', views.job_list, name='job_list'),
    path('serviceManager/dashboard/jobs/', views.manager_job_list, name='manager_job_list'),
     path('serviceManager/dashboard/job/<int:job_id>/candidates/', views.view_candidates, name='view_candidates'),
    path('apply-job/<int:job_id>/', views.apply_job, name='apply_job'),
    path('serviceManager/dashboard/application/<int:application_id>/select/', views.select_candidate, name='select_candidate'),
    # path('job-thanks/', views.apply_job, name='job_thanks'),
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)