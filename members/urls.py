from django.urls import path
from.import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('seller_dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('buyer_dashboard/', views.buyer_dashboard, name='buyer_dashboard'),

    path('register/', views.register, name='register'),
    path('userlogin/', views.userlogin, name='userlogin'),
    # path('allproperties/', views.allproperties, name='allproperties'),
    path('single_property/', views.single_property, name='single_property'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.user_logout, name='logout'),
    path('newproperty/', views.newproperty, name='newproperty'),
    path('all_properties/', views.all_properties, name='all_properties'),
    path('success_page/', views.success_page, name='success_page'),
    path('error_page/', views.error_page, name='error_page'),
    path('property/<int:id>/', views.single_property, name='single_property'),
    path('property/delete/<int:id>/', views.delete_property, name='delete_property'),
    path('property/edit/<int:id>/', views.edit_property, name='edit_property'),
    # review
    path('properties/<int:id>/reviews/', views.add_review, name='add_review'),
    path('properties/<int:property_id>/reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    # profile
    path('my_profile/', views.my_profile, name='my_profile'),
    

    # search action
    path('search_properties/', views.search_properties, name='search_properties'),

    path('manage_properties/', views.manage_properties, name='manage_properties'),

    # book visit
    path('property/<int:id>/book-visit/', views.book_visit, name='book_visit'),
    path('visit-requests/', views.visit_requests_received, name='visit_requests_received'),

    # contact handling
    path('handle_contact/', views.handle_contact, name='handle_contact'),

    # like button
    path('like-review/<int:review_id>/', views.like_review, name='like_review'),

    # apply real estate agent
    path('apply_agent/', views.apply_agent, name='apply_agent'),

    # real estate agent approvel by admin
    path('approve-agents/', views.approve_agents, name='approve_agents'),
    path('approve-agent/<int:user_id>/', views.approve_agent, name='approve_agent'),
    path('reject-agent/<int:user_id>/', views.reject_agent, name='reject_agent'),
    
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/properties/', views.PropertyListView.as_view(), name='property_list'),
    path('api/properties/<int:pk>/', views.PropertyDetailView.as_view(), name='property_detail'),
    path('api/visit-requests/create/', views.VisitRequestCreateView.as_view(), name='visit-request-create'),
       
]