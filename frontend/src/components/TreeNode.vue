<script setup lang="ts">
const props = defineProps<{
  node: any
  depth?: number
}>()
</script>

<template>
  <div class="tree-node" :style="{ paddingLeft: (props.depth || 0) * 20 + 'px' }">
    <div class="node-content">
      <span class="node-icon">
        {{ props.node.type === 'directory' ? '📁' : '📄' }}
      </span>
      <span class="node-name">{{ props.node.name }}</span>
    </div>
    <div v-if="props.node.children && props.node.children.length > 0" class="node-children">
      <TreeNode
        v-for="child in props.node.children"
        :key="child.path"
        :node="child"
        :depth="(props.depth || 0) + 1"
      />
    </div>
  </div>
</template>