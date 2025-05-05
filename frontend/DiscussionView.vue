<template>
    <div class="discussion-view">
      <h1 class="title">Discussion Board</h1>
      <div v-for="thread in threads" :key="thread.id" class="thread-item">
  <router-link :to="`/discussion/${thread.id}`">{{ thread.title }}</router-link>
  <p v-if="thread.posts && thread.posts.length > 0">Someone replied to this</p>
  <p v-else>No reply yet</p>
</div>
  
      <div class="field">
        <label class="label">Create New Thread</label>
        <div class="control">
          <input class="input" v-model="newThreadTitle" placeholder="Enter thread title" />
        </div>
        <button class="button is-primary" @click="createThread">Create</button>
      </div>
    </div>
    </template>
<script>
import axios from 'axios'
  
  export default {
    data() {
      return {
        threads: [],
        newThreadTitle: ''
      }
    },
    mounted() {
      this.fetchThreads();
    },
    methods: {
      fetchThreads() {
  axios.get('discussion/threads/', {
    headers: {
      Authorization: `Token ${this.$store.state.user.token}`
    }
  })
    .then(response => {
      this.threads = response.data;
    })
    .catch(error => {
      console.error("Error fetching threads:", error);
    });
},
      createThread() {
        axios.post('discussion/threads/create/', {
          title: this.newThreadTitle
        },)
        .then(response => {
          this.threads.unshift(response.data); // Insert at the top
          this.newThreadTitle = '';
        })
        .catch(error => {
          console.error("Error creating thread:", error);
        });
      }
    }
  }
  </script>
  <style scoped>
  .discussion-view {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f5f5f5;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .title {
    text-align: center;
    margin-bottom: 20px;
    font-size: 2.5em;
    color: #3273dc;
  }
  
  .thread-item {
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-bottom: 15px;
    background-color: white;
    transition: box-shadow 0.3s ease;
  }
  
  .thread-item:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .thread-item p {
    margin: 5px 0;
    color: #4a4a4a;
  }
  
  .thread-item .router-link {
    font-size: 1.2em;
    font-weight: bold;
    color: #3273dc;
    text-decoration: none;
  }
  
  .thread-item .router-link:hover {
    text-decoration: underline;
  }
  
  .field {
    margin-top: 20px;
  }
  
  .label {
    font-weight: bold;
    color: #4a4a4a;
  }
  
  .control {
    margin-bottom: 10px;
  }
  
  .input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
  }
  
  .button {
    display: block;
    width: 100%;
    padding: 10px;
    background-color: #3273dc;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1.2em;
    transition: background-color 0.3s ease;
  }
  
  .button:hover {
    background-color: #275aa8;
  }
  
  .notification {
    margin-top: 10px;
    padding: 15px;
    border-radius: 5px;
    background-color: #3273dc;
    color: white;
    font-size: 1em;
  }
  </style>