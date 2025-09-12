<template>
  <div class="general-error-container">
    <h1>An Error Occurred</h1>
    <p>Something went wrong. Please try again later.</p>
    <p v-if="errorMessage">{{ errorMessage }}</p>
    <router-link to="/">Go to Home</router-link>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRoute } from 'vue-router';

export default defineComponent({
  name: 'GeneralError',
  setup() {
    const route = useRoute();
    const errorMessage = ref(route.query.message as string || '');

    return {
      errorMessage,
    };
  },
});
</script>

<style scoped>
.general-error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
}

h1 {
  font-size: 4em;
  margin-bottom: 0.5em;
}

p {
  font-size: 1.5em;
  margin-bottom: 1em;
}
</style>