from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('report/', views.report_dumping, name='report_dumping'),
    path('report/success/<str:reference_number>/', views.report_success, name='report_success'),
    path('track/', views.track_report, name='track_report'),
    path('map/', views.reports_map, name='reports_map'),
    path('my-reports/', views.my_reports, name='my_reports'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('report/<int:report_id>/update/', views.update_report, name='update_report'),
    path('statistics/', views.statistics_view, name='statistics'),
]
