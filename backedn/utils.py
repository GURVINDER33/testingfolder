
from .models import QuizResponse, ReadingResponse, FinalExamResult


# this file is used so that i send myself the metrics rather than let ai caluculate 
# and not have hallucinations 
# contains utility functions to calculate user metrics for quizzes, readings and exams 
def calculate_user_quiz_metrics(user):
    quiz_responses = QuizResponse.objects.filter(
        student=user,
        question__lesson__course__isnull=False
    )
    total = quiz_responses.count()
    correct = quiz_responses.filter(is_correct=True).count()
    accuracy = (correct / total * 100) if total > 0 else 0

    return {
        "total_quizzes": total,
        "correct_quizzes": correct,
        "quiz_accuracy": accuracy
    }

def calculate_user_reading_metrics(user):
    reading_responses = ReadingResponse.objects.filter(
        student=user,
        lesson__course__isnull=False
    )
    total_readings = reading_responses.count()

    return {
        "total_readings": total_readings
    }

def calculate_user_exam_metrics(user):
    final_exam_results = FinalExamResult.objects.filter(
        student=user,
        lesson__course__isnull=False
    )
    total_exams = final_exam_results.count()

    return {
        "total_exams": total_exams
    }
