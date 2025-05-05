import re
from rest_framework import serializers
from .models import courseLesson, QuizResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view , authentication_classes , permission_classes
from rest_framework.permissions import AllowAny , IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse
from django.db import transaction
from .models import Course , courseLesson , Category, UserLessonProgress , QuizResponse, ReadingResponse, Quiz, FinalExamResult
from .serializers import CourselistSerializer , CourseMainSerializer , CourseLessonSerializer , QuizSerializer , CategorySerializer 
from courses.models import QuizResponse, ReadingResponse, FinalExamResult
import openai
import os
from pinecone import Pinecone#
import json

# the project is not focused on security . 
# api_view(['GET']) means that this view will only accept GET requests
# permission_classes([AllowAny]) means that this view can be accessed by anyone, regardless of authentication status
# authentication_classes([]) means that no authentication is required for this view
# csrf_exempt means that CSRF protection is not required for this view



# method to get the course detail and lessons
@api_view(['GET'])
def course_detail(request, slug):
    print("Course slug:", slug)  # bebugging line to check the slug value
    coursemain = Course.objects.get(slug=slug)
    coursemain_serializer = CourseMainSerializer(coursemain) 
    course_lesson_serializer = CourseLessonSerializer(coursemain.courselesson_set.all(), many=True)

    data = {
        "course": coursemain_serializer.data,
        "lessons": course_lesson_serializer.data
    }

    return Response(data)



# method to get the lesson detail
# this method is used to get the lesson detail by passing the lesson id
@api_view(['GET'])
@permission_classes([AllowAny]) 
def get_lesson(request, lesson_id):
    lesson = courseLesson.objects.get(id=lesson_id)
    serializer = CourseLessonSerializer(lesson)
    return Response(serializer.data)




# method to get the quiz detail
# this method is used to get the quiz detail by passing the course slug and lesson slug
@api_view(['GET'])
def quiz_list(request, course_slug, courselesson_slug):
    courselesson = courseLesson.objects.get(slug=courselesson_slug)
    quiz = courselesson.lessonquizzes.first()
    serializer = QuizSerializer(quiz)
    return Response(serializer.data)



# method to get the quiz detail by passing the lesson id


@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

# method to get the categories

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
   
    return Response(serializer.data)


# method to get the courses by passing the category id
@api_view(['GET'])
def course_list(request):
    category_id = request.GET.get('category_id', '')
    courses = Course.objects.all()
    
    if category_id:
        courses = courses.filter(categories__id=int(category_id))
    
    serializer = CourselistSerializer(courses, many=True)
    return Response(serializer.data)


    








# starting Pinecone client


pc = Pinecone(api_key="pcsk_2egBVz_RQFPQHFDsvaVpba2GJoc2SmymxRrwr9q9Z6SdqToWqmHPzmUJDr8agRUUTq2C3B")


from django.http import StreamingHttpResponse


# method to get the quiz feedback by passing the question id and selected answer
 
@api_view(['POST'])
@permission_classes([AllowAny])
def get_quiz_feedback(request):
    user = request.user
    question_id     = request.data.get("question_id")
    selected_answer = request.data.get("selected_answer", "")
    explanation     = request.data.get("explanation", "")

    quiz_question  = Quiz.objects.get(id=question_id)
    correct_answer = quiz_question.answer
    is_correct     = selected_answer.strip().lower() == correct_answer.strip().lower()

    # 🔹 embed & fetch trusted context (same as before)
    user_query = f"{quiz_question.question} {explanation}".strip()
    query_embedding = openai.Embedding.create(
        input=[user_query],
        model="text-embedding-3-small"
    )["data"][0]["embedding"]

    course_id  = quiz_question.lesson.course.id
    index_name = re.sub(r"[^a-z0-9-]", "-", f"index-course-{course_id}".lower())
    trusted    = pc.Index(index_name).query(
        vector=query_embedding,
        top_k=4,
        include_metadata=True
    )
    trusted_context = "\n\n".join(m["metadata"]["text"] for m in trusted["matches"])

  
    prompt = f"""
You are an educational assistant. Based on the course material and the student's answer, provide detailed and helpful feedback.

### CONTEXT:
{trusted_context}

### QUESTION:
{quiz_question.question}

### STUDENT'S ANSWER:
{selected_answer}

### EXPLANATION (Optional):
{explanation}

### CORRECT ANSWER:
{correct_answer}

Please respond in 3 short sections with proper format and headings:
1. What they did well  
2. Any repeated mistakes or misunderstandings
3. How they can improve or revise this concept 
4. Provide 1 or 2 concrete follow-up actions or resources.


Be specific, supportive, and encouraging.
"""


    # generator that will stream tokens and records full text
    def stream():
        full = ""
        resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
            stream=True
        )
        for chunk in resp:
            if chunk.choices[0].delta.get("content"):
                token = chunk.choices[0].delta.content         
                full += token
                yield token

        # saving once streaming ends
        QuizResponse.objects.create(
            student=user,
            question=quiz_question,
            selected_answer=selected_answer,
            explanation=explanation,
            is_correct=is_correct,
            ai_feedback=full
        )

    return StreamingHttpResponse(stream(), content_type="text/plain")

# method to get the final exam feedback by passing the lesson id and answers

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_final_exam(request, lesson_id):
    lesson       = courseLesson.objects.get(id=lesson_id, lesson_type="final")
    answers      = request.data.get("answers", [])
    explanation  = request.data.get("explanation", "")

    total_questions = lesson.exam_questions.count()
    correct_count   = 0
    combined_text   = ""

    for ans in answers:
        q = lesson.exam_questions.get(id=ans["question_id"])
        student = ans.get("selected_option")
        correct = getattr(q, q.correct_option)
        is_ok   = student == correct
        if is_ok:
            correct_count += 1
        combined_text += (
            f"Question: {q.question_text}\n"
            f"Student Answer: {student}\n"
            f"Correct Answer: {correct}\n"
            f"Is Correct: {is_ok}\n\n"
        )

    # embed + Pinecone
    query_embedding = openai.Embedding.create(
        input=[combined_text + "\n" + explanation],
        model="text-embedding-3-small"
    )["data"][0]["embedding"]

    course_id  = lesson.course.id
    index_name = re.sub(r"[^a-z0-9-]", "-", f"index-course-{course_id}".lower())
    trusted    = pc.Index(index_name).query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True
    )
    trusted_context = "\n\n".join(m["metadata"]["text"] for m in trusted["matches"])

    prompt = f"""
You are the student's teacher. Review their final exam.

### COURSE CONTEXT
{trusted_context}

### STUDENT RESPONSES
{combined_text}

Total: {total_questions} Correct: {correct_count}

Additional explanation:
{explanation}

Give direct, second-person feedback: strengths, weak areas, time to review, resources.
"""

    def stream():
        full = ""
        resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
            stream=True
        )
        for chunk in resp:
            if chunk.choices[0].delta.get("content"):
                token = chunk.choices[0].delta.content
                full += token
                yield token

        FinalExamResult.objects.create(
            student=request.user,
            lesson=lesson,
            total_questions=total_questions,
            correct_count=correct_count,
            final_feedback=full
        )

    return StreamingHttpResponse(stream(), content_type="text/plain")


# method to mark the lesson as in progress
@api_view(['POST'])
@permission_classes([AllowAny])
def mark_lesson_in_progress(request, lesson_id):
    lesson = courseLesson.objects.get(id=lesson_id)
    # Either get or create the progress object
    progress, _ = UserLessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    progress.status = UserLessonProgress.IN_PROGRESS
    progress.save()
    return Response({"message": "Lesson marked as in progress"}) 


# method to mark the lesson as completed
@api_view(['POST'])
@permission_classes([AllowAny])
def mark_lesson_completed(request, lesson_id):
    lesson = courseLesson.objects.get(id=lesson_id)
    progress, _ = UserLessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    progress.status = UserLessonProgress.COMPLETED
    progress.save()
    return Response({"message": "Lesson marked as completed"})


# method to get the user progress
@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_progress(request):
    # get all progress objects for the user
    progress_entries = UserLessonProgress.objects.filter(user=request.user).select_related('lesson__course')
    
    # building a result grouping by course
    data = {}
    for entry in progress_entries:
        try:
            course_id = entry.lesson.course.id
            course_title = entry.lesson.course.title
            course_slug = entry.lesson.course.slug 
            lesson_title = entry.lesson.title
            
            status = entry.status

            if course_id not in data:
                data[course_id] = {
                    "course_id": course_id,
                    "course_title": course_title,
                    "course_slug": course_slug,
                    "lessons": []
                }
            data[course_id]["lessons"].append({
                "lesson_id": entry.lesson.id,
                "lesson_title": lesson_title,
                "status": status
            })
        except AttributeError:
            # handling missing lesson or course
            continue

    # converting  dictitonary  to a list
    response_data = list(data.values())

    return Response(response_data)



# method to delete the lesson progress
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_lesson_progress(request, lesson_id):
    from .models import UserLessonProgress, courseLesson
    lesson = courseLesson.objects.get(id=lesson_id)
    try:
        progress = UserLessonProgress.objects.get(user=request.user, lesson=lesson)
        progress.delete()  # removing the record entirely
        return Response({"message": "Progress removed."})
    except UserLessonProgress.DoesNotExist:
        return Response({"error": "No progress record found."}, status=404)





# method to get the reading feedback by passing the lesson id and user text
@api_view(['POST'])
@permission_classes([AllowAny])
def reading_feedback(request, lesson_id):
    if request.method != "POST":
        return Response({'detail': 'POST only'}, status=405)

    lesson = courseLesson.objects.get(id=lesson_id, lesson_type='article')
    user_text = json.loads(request.body).get("user_text", "")

    query_embedding = openai.Embedding.create(
        input=[user_text],
        model="text-embedding-3-small"
    )["data"][0]["embedding"]

    course_id  = lesson.course.id
    raw_name   = f"index-course-{course_id}"
    index_name = re.sub(r'[^a-z0-9-]', '-', raw_name.lower())
    index      = pc.Index(index_name)

    results = index.query(vector=query_embedding, top_k=4, include_metadata=True)
    trusted_context = "\n\n".join(m["metadata"]["text"] for m in results["matches"])

    prompt = f"""
You are a helpful teacher evaluating a student's reflection.

You have access to:
1. The original article the student was asked to read  
2. Supporting context pulled from other course materials

Use both the article and the supporting context to give helpful, informative feedback.  
If the student's response misses points covered in either the article or the supporting context, you may mention it gently.

### ARTICLE TEXT:
{lesson.article_text}

### SUPPORTING CONTEXT:
{trusted_context}

### STUDENT'S WRITING:
{user_text}

Give clear, encouraging feedback in 3–4 parts:
• What the student explained well  
• Any mistakes or missing points  
• Suggestions for how to improve  
• 1–2 practical tips or resources to review
"""




    def chat_stream():
        full_response = ""
        openai_response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
            stream=True
        )

        for chunk in openai_response:
            content = chunk.choices[0].delta.get("content")
            if content:
                full_response += content
                yield content

        # after the straeming is finished then save to database in transaction
        with transaction.atomic():
            ReadingResponse.objects.create(
                student=request.user,
                lesson=lesson,
                user_text=user_text,
                ai_feedback=full_response
            )

    return StreamingHttpResponse(chat_stream(), content_type="text/plain")







# method to get the user metrics
from courses.utils import (
    calculate_user_quiz_metrics,
    calculate_user_reading_metrics,
    calculate_user_exam_metrics
)

# This method is used to get the user metrics by passing the user id


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_metrics(request):
    user = request.user
    quiz_metrics = calculate_user_quiz_metrics(user)
    reading_metrics = calculate_user_reading_metrics(user)
    exam_metrics = calculate_user_exam_metrics(user)

    return Response({
        **quiz_metrics,
        **reading_metrics,
        **exam_metrics
    })


# method to get the overall progress of the user (MAIN FUNCTION)
# This method is used to get the overall progress of the user by passing the user id
# and the course id

@api_view(['GET'])
@permission_classes([AllowAny])
def get_overall_progress(request):
    import re
    user = request.user
    # gathering learning history
    learning_history = {'quiz_responses': [], 'reading_responses': [], 'final_exams': []}

    # gathering quiz responses
    quiz_responses = QuizResponse.objects.filter(
        student=user, question__lesson__course__isnull=False
    ).select_related('question__lesson__course')[:10]


    for response in quiz_responses:
        try:
            course = response.question.lesson.course
            learning_history['quiz_responses'].append({
                'course': course.title,
                'question': response.question.question,
                'is_correct': response.is_correct,
                'explanation': response.explanation,
                'ai_feedback': response.ai_feedback,
                'date': response.submitted_at.strftime("%Y-%m-%d")
            })
        except Exception:
            continue

    # gathering reading responses
    reading_responses = ReadingResponse.objects.filter(
        student=user, lesson__course__isnull=False
    ).select_related('lesson__course')[:5]

    for response in reading_responses:
        try:
            course = response.lesson.course
            learning_history['reading_responses'].append({
                'course': course.title,
                'lesson': response.lesson.title,
                'summary': response.user_text,
                'ai_feedback': response.ai_feedback,
                'date': response.submitted_at.strftime("%Y-%m-%d")
            })
        except Exception:
            continue

    # gathering final exam resoneses
    final_exam_results = FinalExamResult.objects.filter(
        student=user, lesson__course__isnull=False
    ).select_related('lesson__course')[:3]

    for result in final_exam_results:
        try:
            course = result.lesson.course
            learning_history['final_exams'].append({
                'course': course.title,
                'score': f"{result.correct_count}/{result.total_questions}",
                'feedback': result.final_feedback,
                'date': result.submitted_at.strftime("%Y-%m-%d")
            })
        except Exception:
            continue

    # embedding learning history text
    combined_history_text = json.dumps(learning_history, indent=2)
    query_embedding = openai.Embedding.create(
        input=[combined_history_text],
        model="text-embedding-3-small"
    )["data"][0]["embedding"]

    # query all relevant pinecone indexes
    all_matches = []
    course_ids_seen = set()
    for section in learning_history.values():
        for entry in section:
            if 'course' in entry:
                course_title = entry['course']
                course = Course.objects.filter(title=course_title).first()
                if course and course.id not in course_ids_seen:
                    course_ids_seen.add(course.id)
                    raw_name = f"index-course-{course.id}"
                    index_name = re.sub(r'[^a-z0-9-]', '-', raw_name.lower())
                    try:
                        index = pc.Index(index_name)
                        result = index.query(vector=query_embedding, top_k=2, include_metadata=True)
                        all_matches.extend(result["matches"])
                    except Exception as e:
                        print(f"Error querying index for course {course.id}: {str(e)}")

    # trimming and merging contxt
    trusted_context = "\n\n".join([match["metadata"]["text"][:300] for match in all_matches])

    
    prompt = f"""
You are an advanced educational assistant analyzing a student's learning history and course material.

### COURSE CONTEXT FROM DATABASE:
{trusted_context}

### STUDENT'S LEARNING HISTORY:
{combined_history_text}

Please provide a comprehensive report that includes:

1. STRENGTHS
2. AREAS FOR IMPROVEMENT
3. LEARNING PATTERNS
4. RECOMMENDATIONS
5. NEXT STEPS

Use a constructive and positive tone. Give practical insights.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )

        analysis = response.choices[0].message.content

        return Response({
            "overall_analysis": analysis
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
