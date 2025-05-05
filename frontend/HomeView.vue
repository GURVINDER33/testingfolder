<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero is-info is-medium">
      <div class="hero-body">
        <div class="container has-text-centered">
          <h1 class="title">
            Welcome to LevelUP
          </h1>
          <h2 class="subtitle">
            Empowering your learning journey with cutting-edge courses
          </h2>
          <button class="button is-primary" @click="$router.push('/courses')">
            Explore Courses
          </button>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="section">
      <div class="container">
        <div class="columns is-multiline">
          <div class="column is-4" v-for="(feature, index) in features" :key="index">
            <div class="card">
              <div class="card-content">
                <p class="title is-4">{{ feature.title }}</p>
                <p class="content">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "HomeView",
  data() {
    return {
      features: [
        { title: "Expert Instructors", description: "Learn from industry experts." },
        { title: "Flexible Learning", description: "Study at your own pace, anytime, anywhere." },
        { title: "Interactive Quizzes", description: "Engage with real-time quizzes and feedback." }
      ]
    }
  }
}
</script>

<style scoped>
.home-page {
  padding: 20px;
}

.hero {
 
  background-size: cover;
  background-position: center;
}
</style>
