<script setup lang="ts">
import { ref, onMounted } from 'vue'

const isCollapsed = ref(false)

onMounted(() => {
  isCollapsed.value = localStorage.getItem('sidebar-collapsed') === 'true'
  applyState()
})

function toggle() {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebar-collapsed', String(isCollapsed.value))
  applyState()
}

function applyState() {
  document.documentElement.dataset.sidebarCollapsed = String(isCollapsed.value)
}
</script>

<template>
  <!-- 收起按钮：跟随 sidebar 一起滑出屏幕 -->
  <button class="sidebar-collapse-btn" @click="toggle" title="收起侧边栏">
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M15 18l-6-6 6-6" />
    </svg>
  </button>

  <!-- 展开按钮：Teleport 到 body，固定在屏幕左侧，不受 sidebar transform 影响 -->
  <Teleport to="body">
    <Transition name="sidebar-expand">
      <button v-if="isCollapsed" class="sidebar-expand-btn" @click="toggle" title="展开侧边栏">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 18l6-6-6-6" />
        </svg>
      </button>
    </Transition>
  </Teleport>
</template>
