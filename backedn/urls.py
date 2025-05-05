from django.urls import path

from courses import views 

# This file contains the URL patterns for the courses app   
urlpatterns = [
    

    path('', views.course_list, name='course_list'),

    path('categories/', views.get_categories, name='get_categories'),
path('user-progress/', views.get_user_progress, name='get_user_progress'),
    path('get-quiz-feedback/', views.get_quiz_feedback, name='get_quiz_feedback'),
    path('user-metrics/', views.get_user_metrics, name='get_user_metrics'),

    path('overall-progress/', views.get_overall_progress, name='get_overall_progress'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:course_slug>/<slug:courselesson_slug>/get-quiz/', views.quiz_list, name='quiz_list'),
    path('lesson/<int:lesson_id>/', views.get_lesson, name='get_lesson'),
    path('lesson/<int:lesson_id>/submit-final/', views.submit_final_exam, name='submit_final_exam'),
    
    path('lesson/<int:lesson_id>/mark-in-progress/', views.mark_lesson_in_progress, name='mark_lesson_in_progress'),
    path('lesson/<int:lesson_id>/mark-completed/', views.mark_lesson_completed, name='mark_lesson_completed'),
    path('lesson/<int:lesson_id>/delete-progress/', views.delete_lesson_progress, name='delete_lesson_progress'),
    path('lesson/<int:lesson_id>/reading-feedback/', views.reading_feedback, name='reading_feedback'),
  
    
]

    
