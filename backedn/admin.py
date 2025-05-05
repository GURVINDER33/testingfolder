
# This file lets me manage the models in the Django admin interface
from django.contrib import admin
from django.contrib import admin 
from .models import Course, Category , courseLesson , Quiz, FinalExamQuestion , QuizResponse, ReadingResponse, FinalExamResult

admin.site.register(Course)
admin.site.register(Category)
admin.site.register(courseLesson)
admin.site.register(Quiz)
admin.site.register(FinalExamQuestion)

@admin.register(ReadingResponse)
class ReadingResponseAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'submitted_at']
    list_filter = ['student', 'lesson']
    search_fields = ['user_text', 'ai_feedback']
    readonly_fields = ['submitted_at']

@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ['student', 'question', 'is_correct', 'submitted_at']
    list_filter = ['student', 'is_correct']
    search_fields = ['selected_answer', 'explanation', 'ai_feedback']
    readonly_fields = ['submitted_at']

@admin.register(FinalExamResult)
class FinalExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'correct_count', 'total_questions', 'submitted_at']
    list_filter = ['student', 'lesson']
    search_fields = ['final_feedback']
    readonly_fields = ['submitted_at']