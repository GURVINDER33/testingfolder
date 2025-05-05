<template>
  <div class="courses-page">
    <div class="hero is-primary">
      <div class="hero-body has-text-centered">
        <h1 class="title">Explore Courses</h1>
      </div>
    </div>
    <section class="section">
      <div class="container">
        <div class="columns">
          
          <div class="column is-3">
            <aside class="menu">
              <p class="menu-label">Course Categories</p>
              <ul class="menu-list">
               <li>
                                    <a 
                                        v-bind:class="{'is-active': !activeCategory}"
                                        @click="setActiveCategory(null)"
                                    >
                                        All courses
                                    </a>
                                </li>
                                <li
                                    v-for="category in categories"
                                    v-bind:key="category.id"
                                    @click="setActiveCategory(category)"
                                >
                                    <a>{{ category.title }}</a>
                                </li>

              </ul>
            </aside>
          </div>
          <!-- Main Content Area -->
          <div class="column is-9">
            <div class="columns is-multiline">
              <div class="column is-4" v-for="course in courses" :key="course.id">
                <itemCourse :course="course" />    
              </div>
              <!-- pagination (if needed) -->
              <div class="column is-12">
                <nav class="pagination is-centered">
                  <a class="pagination-previous">Previous</a>
                  <a class="pagination-next">Next</a>
                  <ul class="pagination-list">
                    <li><a class="pagination-link is-current">1</a></li>
                    <li><a class="pagination-link">2</a></li>
                    <li><a class="pagination-link">3</a></li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import axios from 'axios'
import itemCourse from '@/components/itemCourse.vue'

export default {
  data() {
    return {
      courses: [],
      categories: [],
      activeCategory: null
    }
  },
  components: {
    itemCourse
  },
  mounted() {
    console.log('mounted');
    // Updated endpoint for fetching categories
    axios.get('courses/categories/')
      .then(response => {
        this.categories = response.data
      })
      .catch(error => {
        console.error("Error fetching categories:", error);
      });
    
    this.fetchCourses()
  },
  methods: {
    fetchCourses() {
      let url = 'courses/'
      if (this.activeCategory) {
        url += `?category_id=${this.activeCategory.id}`
      }
      axios.get(url)
        .then(response => {
          this.courses = response.data
        })
        .catch(error => {
          console.error("Error fetching courses:", error)
        })
    },
    setActiveCategory(category) {
      this.activeCategory = category
      this.fetchCourses()
    },
    
  }
}
</script>
