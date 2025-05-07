<template>
  <header class="app-header">
    <h1>Система структурування файлів</h1>
  </header>
  
  <main class="app-main">
    <router-view />
  </main>
  
  <footer class="app-footer">
    <p>&copy; 2025 - Система структурування файлів</p>
  </footer>
</template>

<script setup lang="ts">
// No script logic needed here
</script>

<style>
.app-header {
  padding: 1rem;
  background-color: #4c6ef5;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: calc(100vh - 150px);
}

.app-footer {
  padding: 1rem;
  background-color: #f1f3f5;
  text-align: center;
  border-top: 1px solid #dee2e6;
}
</style>