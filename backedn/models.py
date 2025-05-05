from django.db import models

from django.utils import timezone

from django.conf import settings
from django.contrib.auth.models import User

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, default="")
    description = models.TextField(default="No description provided")   # model to catergorise the courses
    created_at = models.DateField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default="No description provided")
    slug = models.SlugField(unique=True, blank=True, default="") 
    short_description = models.CharField(max_length=255, default="No description provided") # model to create the course
    long_description = models.TextField(default="No description provided")
    created_at = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE )
    categories = models.ManyToManyField(Category)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']



    def image_get(self):
        if self.image:
            return settings.WEBSITE_URL + self.image.url
        else:
            return 'https://via.placeholder.com/150'



# this model is used to create the lessons for the courses
class courseLesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default="No description provided")      
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateField(default=timezone.now)
    slug = models.SlugField( blank=True, null=True)

    def __str__(self):
        return self.title
    

    DRAFT = 'draft'
    PUBLISHED = 'published'

    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    ]

    ARTICLE = 'article'
    QUIZ = 'quiz'
    Video = 'video'
    final = 'final'

    LESSON_TYPE_CHOICES = [
        (ARTICLE, 'Article'),
        (QUIZ, 'Quiz'),
        (Video, 'Video'),
        (final, 'final')
    ]


    yt_video_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PUBLISHED)
    lesson_type = models.CharField(max_length=10, choices=LESSON_TYPE_CHOICES, default=ARTICLE)
    article_text = models.TextField(default="", blank=True)
    rag_text = models.TextField(blank=True, default="")


    
    
# this model is used to create the quizzes for the lessons


class Quiz(models.Model):
    lesson = models.ForeignKey(courseLesson, related_name="lessonquizzes" ,on_delete=models.CASCADE)
    question = models.TextField()  
    answer = models.TextField()
    option1 = models.TextField()
    option2 = models.TextField()
    option3 = models.TextField()
    option4 = models.TextField()

    def __str__(self):
        return self.question

# this model is used to store  the responses of the user from the quiz lesson for the 
class QuizResponse(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_responses')
    question = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='responses')
    selected_answer = models.TextField()
    explanation = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    ai_feedback = models.TextField(blank=True, null=True)  # New field to store AI response feedback

    def __str__(self):
        return f"{self.student.username} - Q:{self.question.id}"





# this model is used to create the final exam questions for the lessons
class FinalExamQuestion(models.Model):
    lesson = models.ForeignKey(courseLesson, on_delete=models.CASCADE, related_name='exam_questions')
    question_text = models.TextField()
    option1 = models.TextField()
    option2 = models.TextField()
    option3 = models.TextField()
    option4 = models.TextField()
    correct_option = models.CharField(max_length=10, default="option1")  # e.g. "option1"

    def __str__(self):
        return self.question_text
    


# this model is used to track the progress of the user in the lessons

class UserLessonProgress(models.Model):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

    PROGRESS_CHOICES = [
        (NOT_STARTED, 'Not Started'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(courseLesson, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=PROGRESS_CHOICES, default=NOT_STARTED)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} [{self.status}]"




# this model is used to store the article lesson(reading) responses of the user from the reading lesson

class ReadingResponse(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_responses')
    lesson = models.ForeignKey(courseLesson, on_delete=models.CASCADE, related_name='reading_responses')
    user_text = models.TextField()  # the student's summary or response text
    ai_feedback = models.TextField(blank=True, null=True)  # store AI-generated feedback
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - Reading Lesson {self.lesson.id}"


# this model is used to store the final exam results of the user from the final exam lesson
class FinalExamResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='final_exam_results')
    lesson = models.ForeignKey(courseLesson, on_delete=models.CASCADE, related_name='final_exam_results')
    total_questions = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    final_feedback = models.TextField()  # AI-generated final summary feedback
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - Final Exam for Lesson {self.lesson.id}"
