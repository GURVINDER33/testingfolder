<template>
  <div class="courses-page">
    <div class="hero is-primary">
      <div class="hero-body has-text-centered">
        <h1 class="title">{{ course.title }}</h1>
        <button 
  class="button is-success" 
  :disabled="isEnrolled || !lessonActive" 
  @click="enrollInCourse"
>
  {{ isEnrolled ? "ENROLLED" : "ENROLL" }}
</button>

      </div>
    </div>
    <section class="section">
      <div class="container">
        <div class="columns content">
          <div class="column is-2">
            <h3>Content</h3>
            
            <ul>
              <li v-for="lesson in lessons" 
              v-bind:key="lesson.id">
                <a @click="activeLessonSet(lesson)">{{ lesson.title }}</a>
              </li>
            </ul>
          </div>
          <div class="column is-10">
            <template v-if="$store.state.user.isAuthenticated">
              <template v-if="lessonActive">

                
                <h2>{{ lessonActive.title }}</h2>
                
                <p>{{ lessonActive.description }}</p>
                <hr>
                <template v-if="lessonActive.lesson_type === 'quiz'">
  <h3>{{ quiz.question }}</h3>
  <div class="control">
    <label class="radio">
      <input type="radio" :value="quiz.option1" v-model="answerselected" id="option1">
      {{ quiz.option1 }}
    </label>
  </div>
  <div class="control">
    <label class="radio">
      <input type="radio" :value="quiz.option2" v-model="answerselected" id="option2">
      {{ quiz.option2 }}
    </label>
  </div>
  <div class="control">
    <label class="radio">
      <input type="radio" :value="quiz.option3" v-model="answerselected" id="option3">
      {{ quiz.option3 }}
    </label>
  </div>
  <div class="control">
    <label class="radio">
      <input type="radio" :value="quiz.option4" v-model="answerselected" id="option4">
      {{ quiz.option4 }}
    </label>
  </div>
  <!-- New Explanation Field -->
  <div class="field" style="margin-top: 1rem;">
    <label class="label">Explain your answer (optional):</label>
    <div class="control">
      <textarea v-model="explanation" class="textarea" placeholder="Type your explanation here"></textarea>
    </div>
  </div>
  <div class="control">
    <!-- quiz section -->
<button class="button is-primary"
        @click="submitAnswer"
        :disabled="isSubmittingQuiz">
  {{ isSubmittingQuiz ? 'Submitting…' : 'Submit answer' }}
</button>

  </div>
  <template v-if="resultquiz === 'correct'">
    <div class="notification is-success">Correct Answer</div>
  </template>
  <template v-else-if="resultquiz === 'incorrect'">
    <div class="notification is-danger">Incorrect Answer</div>
  </template>
  <div v-if="feedback" class="notification is-info">
    <h4 class="subtitle is-5">AI Feedback:</h4>
    <p>{{ feedback }}</p>
  </div>
</template>
<template v-else-if="lessonActive.lesson_type === 'final'">
                  <div v-for="(question, index) in lessonActive.exam_questions" :key="question.id" class="exam-question">
                    <h3>{{ question.question_text }}</h3>
                    <div class="control">
                      <label class="radio">
                        <input type="radio" :name="'question-' + question.id" :value="question.option1" v-model="finalAnswers[index]">
                        {{ question.option1 }}
                      </label>
                    </div>
                    <div class="control">
                      <label class="radio">
                        <input type="radio" :name="'question-' + question.id" :value="question.option2" v-model="finalAnswers[index]">
                        {{ question.option2 }}
                      </label>
                    </div>
                    <div class="control">
                      <label class="radio">
                        <input type="radio" :name="'question-' + question.id" :value="question.option3" v-model="finalAnswers[index]">
                        {{ question.option3 }}
                      </label>
                    </div>
                    <div class="control">
                      <label class="radio">
                        <input type="radio" :name="'question-' + question.id" :value="question.option4" v-model="finalAnswers[index]">
                        {{ question.option4 }}
                      </label>
                    </div>
                  </div>
                  <div class="field" style="margin-top: 1rem;">
    <label class="label">Additional Comments (Optional):</label>
    <div class="control">
      <textarea class="textarea" v-model="finalExplanation" placeholder="Enter your comments"></textarea>
    </div>
  </div>
  <button class="button is-primary"
        @click="submitFinalExam"
        :disabled="isSubmittingFinal">
  {{ isSubmittingFinal ? 'Submitting…' : 'Submit exam' }}
</button>
  <div v-if="finalFeedback" class="notification is-info">
    <h4 class="subtitle is-5">AI Feedback:</h4>
    <p>{{ finalFeedback }}</p>
  </div>


  
                </template>

<template v-else-if="lessonActive.lesson_type === 'video'">
  <Video :yt_video_id="lessonActive.yt_video_id" />
</template>


<template v-else-if="lessonActive.lesson_type === 'article'">
  <div class="content">
    <div>{{ lessonActive.article_text }}</div>

    <label for="readingResponse">Share what you learned:</label>
    <textarea 
      id="readingResponse" 
      class="textarea" 
      v-model="readingResponse" 
      placeholder="Type your summary or main points..."
    ></textarea>
    <button 
      class="button is-primary" 
      @click="submitReadingResponse"
      :disabled="isSubmitting"
    >
      {{ isSubmitting ? 'Getting Feedback...' : 'Submit' }}
    </button>

    <!-- Streaming feedback display -->
    <div v-if="readingFeedback" class="notification is-info feedback-stream">
      <h4>AI Feedback:</h4>
      <p v-html="formattedFeedback"></p>
    </div>
  </div>
</template>
              </template>
              <template v-else>
                {{ course.description }}
              </template>
            </template>
            <template v-else>
              <p>Please login to view course content</p>
            </template>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import axios from 'axios'
import Video from '@/components/video.vue'

export default {
  data() {
    return {
      course: {},
      lessons: [],
      lessonActive: null,
      quiz: {},
      answerselected: null,
      resultquiz: null,
      
      explanation: "",
      feedback: null,
      finalAnswers: [],
      finalExplanation: "",
      finalFeedback: "",
      readingResponse: "",
       readingFeedback: "", 
    isEnrolled: false, // Tracks if the course is enrolled
    isCompleted: false,
    isSubmitting: false,
    isSubmittingQuiz: false,   // new for quiz submissions
    isSubmittingFinal: false,
    }
  },
  computed: {
    formattedFeedback() {
      // Convert the streaming text to HTML with proper formatting
      return this.readingFeedback
        .replace(/\n/g, '<br>')
        .replace(/•/g, '&bull;');
    }
  },
  components: {
    Video,
    // other components...
  },
  mounted() {
    console.log('mounted');
    const slug = this.$route.params.slug;
    // Updated course detail endpoint with API prefix
    axios.get(`courses/${slug}/`)
      .then(response => {
        this.course = response.data.course
        this.lessons = response.data.lessons
      })
      .catch(error => {
        console.error("Error fetching course data:", error);
      });
  },
  methods: {
    async submitAnswer() {
    this.resultquiz     = null;
    this.feedback       = '';
    
    this.isSubmittingQuiz = true; // New flag for quiz submission

  if (!this.answerselected) {
    alert('Please select an answer');
    this.isSubmittingQuiz = false;
    this.
    return;
  }

  // 1. show local correct / incorrect badge immediately
  this.resultquiz = (this.answerselected === this.quiz.answer)
      ? 'correct'
      : 'incorrect';

  // 2. STREAM the AI feedback
  const url = `http://127.0.0.1:8000/api/v1/courses/get-quiz-feedback/`;

  try {
    const res = await fetch(url, {
      method : 'POST',
      headers: {
        'Content-Type' : 'application/json',
        Authorization  : `Token ${this.$store.state.user.token}`
      },
      body: JSON.stringify({
        question        : this.quiz.question,
        selected_answer : this.answerselected,
        explanation     : this.explanation,
        correct_answer  : this.quiz.answer,
        question_id     : this.quiz.id
      })
    });

    if (!res.ok) throw new Error('Bad response');
  
        const reader = res.body.getReader();
        const decoder = new TextDecoder('utf-8');
        const pump = async () => {
          const { done, value } = await reader.read();
          if (done) {
            this.isSubmittingQuiz = false;
            return;
          }
          this.feedback += decoder.decode(value, { stream: true });
          pump();
        };
        pump();
      } catch (err) {
        console.error('Error streaming quiz feedback:', err);
        this.isSubmittingQuiz = false;
      }
},
  
    activeLessonSet(lesson) {
      this.lessonActive = lesson
      if (lesson.lesson_type === 'quiz') {
        this.getQuiz()
      }
      if (lesson.lesson_type === 'final') {
        axios.get(`courses/lesson/${lesson.id}/`, {
          headers: { Authorization: `Token ${this.$store.state.user.token}` }
        })
        .then(response => {
          // The response should contain the exam_questions
          this.lessonActive = response.data
          // Setup finalAnswers array
          this.finalAnswers = this.lessonActive.exam_questions.map(() => "");
        })
        .catch(error => {
          console.error("Error fetching final lesson data:", error);
        });
      }
    },
    submitFinalExam() {
  if (this.finalAnswers.some(a => !a)) {
    alert('Please answer all questions!');
    return;
  }

  this.isSubmittingFinal = true;
      this.finalFeedback = "";

  const payload = {
    answers: this.lessonActive.exam_questions.map((q, i) => ({
      question_id    : q.id,
      selected_option: this.finalAnswers[i]
    })),
    explanation: this.finalExplanation
  };

  const url =
    `http://127.0.0.1:8000/api/v1/courses/lesson/${this.lessonActive.id}/submit-final/`;

  fetch(url, {
    method : 'POST',
    headers: {
      'Content-Type' : 'application/json',
      Authorization  : `Token ${this.$store.state.user.token}`
    },
    body: JSON.stringify(payload)
  })
    .then(res => {
      if (!res.ok) throw new Error('Bad response');
      const reader  = res.body.getReader();
      const decoder = new TextDecoder('utf-8');

      const pump = async () => {
            const { done, value } = await reader.read();
            if (done) {
              this.isSubmittingFinal = false;
              return;
            }
            this.finalFeedback += decoder.decode(value, { stream: true });
            pump();
          };
          pump();
    })
    .catch(err => {
      console.error('Error streaming final exam feedback:', err);
      this.isSubmittingFinal = false;
    });
},

    

    getQuiz() {
      axios.get(`courses/${this.course.slug}/${this.lessonActive.slug}/get-quiz/`)
        .then(response => {
          console.log(response.data)
          this.quiz = response.data
        })
        .catch(error => {
          console.error("Error fetching quiz data:", error)
        })
    },

    
submitReadingResponse() {
  this.isSubmitting = true;
  this.readingFeedback = '';

  const url = `http://127.0.0.1:8000/api/v1/courses/lesson/${this.lessonActive.id}/reading-feedback/`;

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Token ${this.$store.state.user.token}`
    },
    body: JSON.stringify({ user_text: this.readingResponse })
  })
  .then(res => {
    if (!res.ok) throw new Error('Bad response');
    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');

    const readStream = async () => {
      const { done, value } = await reader.read();
      if (done) {
        this.isSubmitting = false;
        return;
      }
      this.readingFeedback += decoder.decode(value, { stream: true });
      await readStream(); // recursively keep reading
    };

    readStream();
  })
  .catch(err => {
    console.error('Error streaming feedback:', err);
    this.isSubmitting = false;
  });
},



  enrollInCourse() {
    if (!this.lessonActive || !this.lessonActive.id) {
      console.error("No lesson selected or lesson ID is missing.");
      return;
    }

    axios.post(`courses/lesson/${this.lessonActive.id}/mark-in-progress/`, {}, {
      headers: { Authorization: `Token ${this.$store.state.user.token}` }
    })
    .then(response => {
      console.log(response.data.message);
      this.isEnrolled = true; // Mark the course as enrolled
    })
    .catch(error => {
      console.error("Error marking lesson in progress:", error);
    });
},


    markInProgress(lesson) {
  if (!lesson || !lesson.id) {
    console.error("No lesson selected or lesson ID is missing.");
    return;
  }

  axios.post(`courses/lesson/${lesson.id}/mark-in-progress/`, {}, {
    headers: { Authorization: `Token ${this.$store.state.user.token}` }
  })
  .then(response => {
    console.log(response.data.message);
    // Optionally update local UI or show a notification
  })
  .catch(error => {
    console.error("Error marking lesson in progress:", error);
  });
}
  },


  downloadArticle() {
      // Implement functionality to download the article, e.g., as a PDF or plain text file.
      // For now, you might simply log a message:
      console.log("Downloading article");
    },
    printArticle() {
      // Implement printing functionality, e.g. by opening a print window
      window.print();
    }
}
</script>

<style scoped>
/* General Page Styling */
.courses-page {
  background-color: #f9f9f9;
  min-height: 100vh;
  padding: 20px;
}

/* Hero Section */
.hero {
  margin-bottom: 20px;
  animation: fadeIn 1s ease-in-out;
}

.hero .title {
  font-size: 2.5rem;
  color: #ffffff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

/* Sidebar Styling */
.column.is-2 {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 15px;
  animation: slideInLeft 0.8s ease-in-out;
}

.column.is-2 h3 {
  font-size: 1.5rem;
  color: #3273dc;
  margin-bottom: 10px;
}

.column.is-2 ul {
  list-style: none;
  padding: 0;
}

.column.is-2 ul li {
  margin-bottom: 10px;
}

.column.is-2 ul li a {
  color: #3273dc;
  text-decoration: none;
  font-weight: bold;
  transition: transform 0.3s ease, color 0.3s ease;
}

.column.is-2 ul li a:hover {
  color: #275aa8;
  transform: scale(1.1);
}

/* Main Content Styling */
.column.is-10 {
  animation: fadeIn 1s ease-in-out;
}

.box {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.box:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.feedback-stream {
  margin-top: 20px;
  white-space: pre-line;
}
/* Quiz Options */
.radio {
  display: block;
  margin-bottom: 10px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.radio:hover {
  transform: scale(1.05);
}

/* Buttons */
.button {
  background-color: #3273dc;
  color: #ffffff;
  border: none;
  border-radius: 5px;
  padding: 10px 20px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: transform 0.3s ease, background-color 0.3s ease;
}

.button:hover {
  background-color: #275aa8;
  transform: scale(1.1);
}

.button.is-primary {
  background-color: #00d1b2;
}

.button.is-primary:hover {
  background-color: #00b89c;
}

/* Notifications */
.notification {
  border-radius: 5px;
  padding: 15px;
  font-size: 1rem;
  animation: fadeIn 0.5s ease-in-out;
}

.notification.is-success {
  background-color: #23d160;
  color: #ffffff;
}

.notification.is-danger {
  background-color: #ff3860;
  color: #ffffff;
}

.notification.is-info {
  background-color: #209cee;
  color: #ffffff;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Textarea Styling */
.textarea {
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
  font-size: 1rem;
  transition: box-shadow 0.3s ease;
}

.textarea:focus {
  box-shadow: 0 0 8px rgba(50, 115, 220, 0.5);
  outline: none;
}

/* Additional Comments Section */
.field {
  margin-top: 20px;
}

.label {
  font-weight: bold;
  color: #4a4a4a;
}

/* Print and Download Buttons */
.download-print-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.download-print-buttons .button {
  flex: 1;
  margin: 0 5px;
}
</style>