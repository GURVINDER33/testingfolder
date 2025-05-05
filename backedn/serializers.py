# this file contains the serializers for the models in the courses app (the way the data is represented in the API)

from django.contrib.auth.models import User

from rest_framework import serializers

from .models import Course , courseLesson , Quiz, Category , FinalExamQuestion , QuizResponse, ReadingResponse, FinalExamResult

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id' , 'first_name', 'last_name']

class CourseMainSerializer(serializers.ModelSerializer):

    created_by = UserSerializer(many=False)
    image_get = serializers.SerializerMethodField()

        

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'long_description', 'created_by', 'image_get']

    def get_image_get(self, obj):
        return obj.image_get()


class FinalExamQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalExamQuestion
        fields = ['id', 'question_text', 'option1', 'option2', 'option3', 'option4', 'correct_option']

class CourseLessonSerializer(serializers.ModelSerializer):
    exam_questions = FinalExamQuestionSerializer(many=True, read_only=True)
    class Meta:
        model = courseLesson
        fields = ['id', 'title', 'description', 'slug','lesson_type',  'yt_video_id', 'article_text', 'exam_questions']



class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id','question', 'answer', 'option1', 'option2', 'option3', 'option4']

        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'description', 'created_at']


class CourselistSerializer(serializers.ModelSerializer):
    
    
    
    
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'image_get'] 









class QuizResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResponse
        fields = ['id', 'student', 'question', 'selected_answer', 'explanation', 'ai_feedback', 'submitted_at']

class ReadingResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingResponse
        fields = ['id', 'student', 'lesson', 'user_text', 'ai_feedback', 'submitted_at']

class FinalExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalExamResult
        fields = ['id', 'student', 'lesson', 'total_questions', 'correct_count', 'final_feedback', 'submitted_at']
