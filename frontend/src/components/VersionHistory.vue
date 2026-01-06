<script setup>
import { ref, onMounted, computed } from 'vue'
import { useTemplateStore } from '../stores/templateStore'

const props = defineProps({
  templateId: {
    type: [String, Number],
    required: true
  }
})

const templateStore = useTemplateStore()
const versions = ref([])
const loading = ref(false)
const selectedVersion = ref(null)

const currentTemplate = computed(() => templateStore.currentTemplate)

onMounted(async () => {
  await loadVersions()
})

const loadVersions = async () => {
  if (!props.templateId || props.templateId === 'new') return

  loading.value = true
  try {
    // Get current template to find parent chain
    const template = await templateStore.fetchTemplate(props.templateId)
    
    // Build versions array - in real implementation, 
    // backend would provide version history
    versions.value = [{
      id: template.id,
      version: template.version,
      created_at: template.created_at,
      updated_at: template.updated_at,
      created_by: template.created_by,
      is_current: true
    }]
  } catch (err) {
    console.error('Failed to load versions:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getVersionStatus = (version) => {
  if (version.is_current) return 'Current'
  return 'Previous'
}
</script>

<template>
  <div class="version-history">
    <div class="version-header">
      <h3>Version History</h3>
      <div class="version-info">
        <span class="current-version">Current: v{{ currentTemplate?.version || 1 }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading version history...</p>
    </div>

    <div v-else-if="templateId === 'new'" class="empty-state">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <p>Save the template to start tracking versions</p>
    </div>

    <div v-else class="versions-timeline">
      <div v-for="version in versions" :key="version.id" class="version-item">
        <div class="version-marker">
          <div class="marker-dot" :class="{ active: version.is_current }"></div>
          <div v-if="version !== versions[versions.length - 1]" class="marker-line"></div>
        </div>
        
        <div class="version-content">
          <div class="version-header-row">
            <h4 class="version-title">Version {{ version.version }}</h4>
            <span v-if="version.is_current" class="current-badge">Current</span>
          </div>
          
          <div class="version-meta">
            <span class="meta-item">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              {{ formatDate(version.created_at) }}
            </span>
          </div>

          <div v-if="!version.is_current" class="version-actions">
            <button class="action-btn" title="View this version">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              View
            </button>
            <button class="action-btn" title="Compare with current">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
              </svg>
              Compare
            </button>
          </div>
        </div>
      </div>

      <div class="version-note">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p>Each time you save changes, a new version is created automatically.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.version-history {
  padding: 1.5rem;
  height: 100%;
  overflow-y: auto;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.version-header h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.version-info {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.current-version {
  background: #e0e7ff;
  color: #4f46e5;
  padding: 0.375rem 0.875rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #94a3b8;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin: 0 auto 0.75rem auto;
}

.versions-timeline {
  position: relative;
}

.version-item {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.version-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 0.25rem;
}

.marker-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #cbd5e0;
  border: 3px solid white;
  box-shadow: 0 0 0 2px #cbd5e0;
  transition: all 0.2s;
}

.marker-dot.active {
  background: #667eea;
  box-shadow: 0 0 0 2px #667eea;
}

.marker-line {
  width: 2px;
  flex: 1;
  background: #e2e8f0;
  margin-top: 0.5rem;
  min-height: 40px;
}

.version-content {
  flex: 1;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.25rem;
}

.version-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.version-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.current-badge {
  background: #16a34a;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.version-meta {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #64748b;
  font-size: 0.875rem;
}

.meta-item svg {
  width: 16px;
  height: 16px;
}

.version-actions {
  display: flex;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  background: white;
  color: #667eea;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: #667eea;
  background: #f8fafc;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.version-note {
  display: flex;
  gap: 0.75rem;
  padding: 1.25rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  margin-top: 1.5rem;
}

.version-note svg {
  width: 20px;
  height: 20px;
  color: #667eea;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.version-note p {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.5;
}
</style>
