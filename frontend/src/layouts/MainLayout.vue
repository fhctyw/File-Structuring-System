<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import SideBar from '../components/SideBar.vue'

const route = useRoute()
const currentTitle = computed(() => route.meta.title || 'File Structuring System')
</script>

<template>
  <div class="app-container">
    <SideBar />
    <main class="main-content">
      <header class="header">
        <h1>{{ currentTitle }}</h1>
      </header>
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100%;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  padding: 16px 24px;
  border-bottom: 1px solid #e2e8f0;
  background-color: #fff;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.content {
  flex: 1;
  padding: 24px;
  overflow: auto;
}
</style>