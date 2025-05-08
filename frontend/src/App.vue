<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  // Ensure we start at the home page
  if (router.currentRoute.value.path !== '/') {
    router.push('/')
  }
})
</script>

<template>
  <router-view />
</template>

<style>
/* Global styles will be inherited from style.css */
</style>