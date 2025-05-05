<template>
    <div class="thread-view">
      <h1 class="title">{{ thread.title }}</h1>
      <div v-for="post in thread.posts" :key="post.id" class="box">
        <p>{{ post.content }}</p>
        <p><small>By {{ post.created_by }}</small></p>
      </div>
  
      <div class="field">
        <label class="label">Add a Post</label>
        <div class="control">
          <textarea class="textarea" v-model="newPostContent" placeholder="Enter your post"></textarea>
        </div>
        <button class="button is-primary" @click="createPost">Submit</button>



        <div class="thread-help">
    <button @click="getThreadAIHelp" class="button is-info">AI Help</button>
    <div v-if="aiHelpResponse" class="notification is-info">
      <h4 class="subtitle is-5">AI Suggestion:</h4>
      <p>{{ aiHelpResponse }}</p>
    </div>
  </div>
      </div>

      
    </div>
  </template>
  
<script>
import axios from 'axios'
  
  export default {
    data() {
      return {
        thread: {},
        newPostContent: '',
        aiHelpResponse: ''
      }
    },
    mounted() {
      this.fetchThread();
    },
    methods: {
      fetchThread() {
        const threadId = this.$route.params.threadId;
        axios.get(`discussion/threads/${threadId}/`)
          .then(response => {
            this.thread = response.data;
          })
          .catch(error => {
            console.error("Error fetching thread:", error);
          });
      },
      createPost() {
        const threadId = this.$route.params.threadId;
        axios.post(`discussion/threads/${threadId}/create-post/`, {
          content: this.newPostContent
        }, {
          headers: { Authorization: `Token ${this.$store.state.user.token}` }
        })
        .then(response => {
          this.thread.posts.push(response.data);
          this.newPostContent = '';
        })
        .catch(error => {
          console.error("Error creating post:", error);
        });
      },
      getThreadAIHelp() {
      const threadContent = this.thread.title + "\n" + this.thread.posts.map(p => p.content).join("\n");
      axios.post('discussion/threads/get_thread_ai_help/', {
        thread_content: threadContent
      },
      {
        headers: { Authorization: `Token ${this.$store.state.user.token}` }
      })
      .then(response => {
        this.aiHelpResponse = response.data.ai_response;
      })
      .catch(error => {
        console.error("Error getting AI help:", error);
      });
    }
    }
  }
</script>
  <style scoped>
  .thread-view {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }

  .title {
    font-size: 2em;
    margin-bottom: 20px;
  }

  .box {
    padding: 15px;
    margin-bottom: 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
  }

  .field {
    margin-top: 20px;
  }

  .label {
    font-weight: bold;
  }

  .textarea {
    width: 100%;
    min-height: 100px;
  }

  .button {
    margin-top: 10px;
  }

  .thread-help {
    margin-top: 20px;
  }

  .notification {
    margin-top: 10px;
  }
  </style>