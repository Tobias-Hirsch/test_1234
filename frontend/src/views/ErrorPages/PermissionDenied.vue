<template>
  <div class="permission-denied-container">
    <h1>Permission Denied</h1>
    <p>You do not have the necessary permissions to view this page.</p>
    <router-link to="/">Go to Home</router-link>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'PermissionDenied',
});
</script>

<style scoped>
.permission-denied-container {
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