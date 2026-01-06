<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTemplateStore } from '../stores/templateStore'
import { useNotification } from '../composables/useNotification'

const router = useRouter()
const templateStore = useTemplateStore()
const { showSuccess, showError } = useNotification()

const documentTypes = [
  { value: null, label: 'All Types' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'agreement', label: 'Agreement' },
  { value: 'quote', label: 'Quote' },
  { value: 'receipt', label: 'Receipt' },
  { value: 'purchase_order', label: 'Purchase Order' },
  { value: 'delivery_note', label: 'Delivery Note' }
]

const viewMode = ref('grid') // 'grid' or 'list'
const showInactive = ref(false)

onMounted(async () => {
  await loadTemplates()
})

const loadTemplates = async () => {
  await templateStore.fetchTemplates({
    is_active: !showInactive.value
  })
}

const groupedTemplates = computed(() => templateStore.groupedTemplates)

const handleSearch = (value) => {
  templateStore.setFilter('search', value)
}

const handleTypeFilter = (type) => {
  templateStore.setFilter('documentType', type)
}

const handleCreateNew = () => {
  router.push('/template-editor/new')
}

const handleEdit = (template) => {
  router.push(`/template-editor/${template.id}`)
}

const handleDuplicate = async (template) => {
  try {
    const newName = prompt(`Enter new name for duplicated template:`, `${template.name} (Copy)`)
    if (!newName) return

    await templateStore.duplicateTemplate(template.id, newName)
    showSuccess('Template duplicated successfully!')
  } catch (err) {
    showError('Failed to duplicate template')
  }
}

const handleDelete = async (template) => {
  if (!confirm(`Are you sure you want to delete "${template.title}"?`)) return

  try {
    await templateStore.deleteTemplate(template.id)
    showSuccess('Template deleted successfully!')
  } catch (err) {
    showError('Failed to delete template')
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getTypeColor = (type) => {
  const colors = {
    invoice: 'bg-blue-100 text-blue-800',
    agreement: 'bg-purple-100 text-purple-800',
    quote: 'bg-green-100 text-green-800',
    receipt: 'bg-yellow-100 text-yellow-800',
    purchase_order: 'bg-orange-100 text-orange-800',
    delivery_note: 'bg-pink-100 text-pink-800'
  }
  return colors[type] || 'bg-gray-100 text-gray-800'
}

const getTypeLabel = (type) => {
  const labels = {
    invoice: 'Invoice',
    agreement: 'Agreement',
    quote: 'Quote',
    receipt: 'Receipt',
    purchase_order: 'Purchase Order',
    delivery_note: 'Delivery Note'
  }
  return labels[type] || type
}
</script>

<template>
  <div class="templates-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Document Templates</h1>
        <p class="page-subtitle">Create and manage templates for your documents</p>
      </div>
      <button @click="handleCreateNew" class="btn btn-primary">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Create Template
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="search-box">
        <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          type="text"
          placeholder="Search templates..."
          :value="templateStore.filters.search"
          @input="handleSearch($event.target.value)"
          class="search-input"
        />
      </div>

      <div class="filter-controls">
        <select
          :value="templateStore.filters.documentType"
          @change="handleTypeFilter($event.target.value || null)"
          class="filter-select"
        >
          <option v-for="type in documentTypes" :key="type.value" :value="type.value">
            {{ type.label }}
          </option>
        </select>

        <label class="checkbox-label">
          <input type="checkbox" v-model="showInactive" @change="loadTemplates" />
          <span>Show Inactive</span>
        </label>

        <div class="view-toggle">
          <button
            @click="viewMode = 'grid'"
            :class="['view-btn', { active: viewMode === 'grid' }]"
            title="Grid view"
          >
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
            </svg>
          </button>
          <button
            @click="viewMode = 'list'"
            :class="['view-btn', { active: viewMode === 'list' }]"
            title="List view"
          >
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="templateStore.loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading templates...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="Object.keys(groupedTemplates).length === 0" class="empty-state">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
      <h3>No templates found</h3>
      <p>{{ templateStore.filters.search ? 'Try adjusting your search' : 'Get started by creating your first template' }}</p>
      <button v-if="!templateStore.filters.search" @click="handleCreateNew" class="btn btn-primary">
        Create Your First Template
      </button>
    </div>

    <!-- Templates Grid/List -->
    <div v-else class="templates-container">
      <div v-for="(templates, type) in groupedTemplates" :key="type" class="template-group">
        <h2 class="group-header">
          <span class="group-title">{{ getTypeLabel(type) }}</span>
          <span class="group-count">{{ templates.length }}</span>
        </h2>

        <div :class="['templates-grid', { 'list-view': viewMode === 'list' }]">
          <div
            v-for="template in templates"
            :key="template.id"
            class="template-card"
            :class="{ inactive: !template.is_active }"
          >
            <div class="card-header">
              <div class="card-title-section">
                <h3 class="card-title">{{ template.title }}</h3>
                <div class="card-meta">
                  <span :class="['type-badge', getTypeColor(template.document_type)]">
                    {{ getTypeLabel(template.document_type) }}
                  </span>
                  <span class="version-badge">v{{ template.version }}</span>
                  <span v-if="!template.is_active" class="inactive-badge">Inactive</span>
                </div>
              </div>
              <div class="card-actions">
                <button
                  @click="handleEdit(template)"
                  class="action-btn primary"
                  title="Edit template"
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                </button>
                <button
                  @click="handleDuplicate(template)"
                  class="action-btn"
                  title="Duplicate template"
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                  </svg>
                </button>
                <button
                  @click="handleDelete(template)"
                  class="action-btn danger"
                  title="Delete template"
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </div>

            <p v-if="template.description" class="card-description">
              {{ template.description }}
            </p>

            <div class="card-footer">
              <div class="card-stats">
                <span class="stat-item" title="Assets">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                  {{ template.asset_count || 0 }}
                </span>
              </div>
              <span class="card-date">{{ formatDate(template.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.templates-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.page-subtitle {
  color: #64748b;
  margin: 0.5rem 0 0 0;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn svg {
  width: 18px;
  height: 18px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

/* Filters */
.filters-bar {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.search-box {
  flex: 1;
  min-width: 250px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #94a3b8;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-select:hover {
  border-color: #cbd5e0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.view-toggle {
  display: flex;
  gap: 0.25rem;
  background: #f1f5f9;
  border-radius: 0.5rem;
  padding: 0.25rem;
}

.view-btn {
  padding: 0.5rem;
  border: none;
  background: transparent;
  border-radius: 0.375rem;
  cursor: pointer;
  color: #64748b;
  transition: all 0.2s;
}

.view-btn svg {
  width: 20px;
  height: 20px;
}

.view-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Loading & Empty States */
.loading-container,
.empty-state {
  background: white;
  border-radius: 1rem;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.spinner {
  width: 48px;
  height: 48px;
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
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem auto;
  color: #94a3b8;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #64748b;
  margin: 0 0 1.5rem 0;
}

/* Templates */
.templates-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.template-group {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.group-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem 0;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e2e8f0;
}

.group-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.group-count {
  background: #f1f5f9;
  color: #64748b;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.templates-grid.list-view {
  grid-template-columns: 1fr;
}

.template-card {
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.2s;
  background: white;
}

.template-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.template-card.inactive {
  opacity: 0.6;
  background: #f8fafc;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 1rem;
}

.card-title-section {
  flex: 1;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.card-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.type-badge,
.version-badge,
.inactive-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.version-badge {
  background: #e0e7ff;
  color: #4f46e5;
}

.inactive-badge {
  background: #fee2e2;
  color: #dc2626;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 0.5rem;
  border: 2px solid #e2e8f0;
  background: white;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f8fafc;
}

.action-btn.primary:hover {
  background: #667eea;
  color: white;
}

.action-btn.danger:hover {
  border-color: #ef4444;
  background: #ef4444;
  color: white;
}

.card-description {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #f1f5f9;
}

.card-stats {
  display: flex;
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
}

.stat-item svg {
  width: 16px;
  height: 16px;
}

.card-date {
  font-size: 0.875rem;
  color: #94a3b8;
}

@media (max-width: 768px) {
  .templates-page {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    width: 100%;
  }

  .filter-controls {
    width: 100%;
    justify-content: space-between;
  }

  .templates-grid {
    grid-template-columns: 1fr;
  }
}
</style>
