<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TemplateList from '../components/TemplateList.vue'
import TemplateEditorComponent from '../components/TemplateEditorComponent.vue'

const route = useRoute()

// Determine if we're in list or edit mode based on route
const mode = computed(() => {
  return route.params.id ? 'edit' : 'list'
})

const templateId = computed(() => route.params.id)
</script>

<template>
  <div class="template-editor-container">
    <!-- List Mode -->
    <TemplateList v-if="mode === 'list'" />

    <!-- Edit Mode -->
    <TemplateEditorComponent v-else :template-id="templateId" />
  </div>
</template>

<style scoped>
.template-editor-container {
  min-height: calc(100vh - 72px);
}
</style>
