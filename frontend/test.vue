<template>
    <div>
      <form @submit.prevent="handleSubmit">
        <textarea
          v-model="quizQuestion"
          placeholder="Enter your quiz question"
          cols="50"
          rows="4"
        ></textarea>
        <button type="submit">Submit Quiz</button>
      </form>
  
      <div v-if="loading">Loading...</div>
  
      <div v-if="quizAnswer">
        <h3>Quiz Answer:</h3>
        <pre>{{ quizAnswer }}</pre>
      </div>
  
      <div v-if="explanation">
        <h3>Explanation:</h3>
        <pre>{{ explanation }}</pre>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const quizQuestion = ref('');
  const quizAnswer = ref('');
  const explanation = ref('');
  const loading = ref(false);
  


  async function handleSubmit() {
    // Reset outputs
    quizAnswer.value = '';
    explanation.value = '';
    loading.value = true;
  
    try {
      const response = await fetch('http://127.0.0.1:8000/answer/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: quizQuestion.value })
      });
  
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = '';
  
      // Read stream chunks until done
      let done = false;
      while (!done) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        accumulatedText += chunk;
  
        // Look for the separator "Explanation:" to split answer and explanation.
        const separator = 'Explanation:';
        const separatorIndex = accumulatedText.indexOf(separator);
        if (separatorIndex !== -1) {
          // Everything before the separator is the quiz answer.
          quizAnswer.value = accumulatedText.substring(0, separatorIndex).trim();
          // Everything from the separator onward is the explanation.
          explanation.value = accumulatedText.substring(separatorIndex).trim();
        } else {
          // If separator not found yet, update the answer area.
          quizAnswer.value = accumulatedText;
        }
      }
    } catch (error) {
      console.error('Error streaming response:', error);
    } finally {
      loading.value = false;
    }
  }
  </script>
  
  <style scoped>
  textarea {
    width: 100%;
    margin-bottom: 1rem;
  }
  
  button {
    display: block;
    margin-bottom: 1rem;
  }
  
  pre {
    background: #f4f4f4;
    padding: 1rem;
    border: 1px solid #ccc;
  }
  </style>
  