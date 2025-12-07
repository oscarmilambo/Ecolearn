from django.urls import path
from . import views

app_name = 'collaboration'

urlpatterns = [
    # Groups
    path('groups/', views.groups_list, name='groups_list'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/join/', views.join_group, name='join_group'),
    path('groups/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('my-groups/', views.my_groups, name='my_groups'),
    
    # Events
    path('groups/<int:group_id>/events/create/', views.create_event, name='create_event'),
    
    # Chat
    path('groups/<int:group_id>/chat/send/', views.send_chat_message, name='send_chat'),
    path('groups/<int:group_id>/chat/messages/', views.get_chat_messages, name='get_chat_messages'),
    
    # Reports
    path('groups/<int:group_id>/report/generate/', views.generate_impact_report, name='generate_report'),
    path('reports/<int:report_id>/', views.view_report, name='view_report'),
]
