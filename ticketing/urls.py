from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('fixtures/', views.fixtures, name='fixtures'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('load-more-news/', views.load_more_news, name='load_more_news'),
    
    # User authentication
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    
    # Ticket booking
    path('book/<int:match_id>/', views.book_ticket, name='book_ticket'),
    path('payment/<int:ticket_id>/', views.payment, name='payment'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('download-ticket/<uuid:ticket_id>/', views.download_ticket, name='download_ticket'),
    
    # Gateman pages
    path('gateman-scanner/', views.gateman_scanner, name='gateman_scanner'),
    path('scan-ticket/', views.scan_ticket, name='scan_ticket'),
    
    # Admin pages
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-matches/', views.admin_matches, name='admin_matches'),
    path('add-match/', views.add_match, name='add_match'),
    path('edit-match/<int:match_id>/', views.edit_match, name='edit_match'),
    path('match-preview/<int:match_id>/', views.match_preview, name='match_preview'),
    path('admin-news/', views.admin_news, name='admin_news'),
    path('edit-news/<int:news_id>/', views.edit_news, name='edit_news'),
    path('delete-news/<int:news_id>/', views.delete_news, name='delete_news'),
    path('admin-reports/', views.admin_reports, name='admin_reports'),
    path('export-reports-csv/', views.export_reports_csv, name='export_reports_csv'),
    path('export-reports-pdf/', views.export_reports_pdf, name='export_reports_pdf'),
    path('download-report/<int:report_id>/', views.download_report, name='download_report'),
    path('admin-gatemen/', views.admin_gatemen, name='admin_gatemen'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('delete-gateman/<int:user_id>/', views.delete_gateman, name='delete_gateman'),
    path('delete-admin/<int:user_id>/', views.delete_admin, name='delete_admin'),
    path('update-match-status/', views.update_match_status, name='update_match_status'),
]
