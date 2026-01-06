<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTemplateStore } from '../stores/templateStore'
import { useNotification } from '../composables/useNotification'
import AssetManager from './AssetManager.vue'
import VersionHistory from './VersionHistory.vue'

const router = useRouter()
const route = useRoute()
const templateStore = useTemplateStore()
const { showSuccess, showError } = useNotification()

const props = defineProps({
  templateId: {
    type: [String, Number],
    default: null
  }
})

// Form data
const templateData = ref({
  name: '',
  title: '',
  description: '',
  document_type: 'invoice',
  html_content: '',
  css_content: '',
  variables: [],
  branding_config: {
    primary_color: '#1E40AF',
    secondary_color: '#64748B',
    font_family: 'Inter, sans-serif'
  }
})

const activeTab = ref('html') // html, css, variables, branding, assets, versions
const loading = ref(false)
const previewData = ref({})

// Sample data for preview
const sampleData = ref({
  company_name: 'Acme Inc.',
  client_name: 'John Doe',
  invoice_number: 'INV-001',
  date: new Date().toLocaleDateString(),
  due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString(),
  total_amount: '$1,234.56',
  items: [
    { description: 'Product A', quantity: 2, price: '$100.00', total: '$200.00' },
    { description: 'Service B', quantity: 5, price: '$50.00', total: '$250.00' }
  ]
})

const documentTypes = [
  { value: 'invoice', label: 'Invoice' },
  { value: 'agreement', label: 'Agreement' },
  { value: 'quote', label: 'Quote' },
  { value: 'receipt', label: 'Receipt' },
  { value: 'purchase_order', label: 'Purchase Order' },
  { value: 'delivery_note', label: 'Delivery Note' }
]

// Computed preview HTML
const previewHtml = computed(() => {
  let html = templateData.value.html_content || '<p>Start editing to see preview...</p>'
  
  // Simple template variable replacement
  Object.keys(sampleData.value).forEach(key => {
    const openBraces = String.fromCharCode(123, 123)
    const closeBraces = String.fromCharCode(125, 125)
    const regex = new RegExp(openBraces + '\\s*' + key + '\\s*' + closeBraces, 'g')
    html = html.replace(regex, sampleData.value[key])
  })
  
  return html
})

const previewCss = computed(() => {
  return templateData.value.css_content || ''
})

// Full preview document
const previewDocument = computed(() => {
  return `
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <style>
          body {
            font-family: ${templateData.value.branding_config?.font_family || 'Arial, sans-serif'};
            margin: 0;
            padding: 20px;
            color: #333;
          }
          ${previewCss.value}
        </style>
      </head>
      <body>
        ${previewHtml.value}
      </body>
    </html>
  `
})

onMounted(async () => {
  if (props.templateId && props.templateId !== 'new') {
    await loadTemplate()
  } else {
    // New template - set defaults
    templateData.value.html_content = getDefaultHtmlTemplate()
    templateData.value.css_content = getDefaultCssTemplate()
  }
})

const loadTemplate = async () => {
  loading.value = true
  try {
    const template = await templateStore.fetchTemplate(props.templateId)
    templateData.value = {
      name: template.name,
      title: template.title,
      description: template.description || '',
      document_type: template.document_type,
      html_content: template.html_content,
      css_content: template.css_content || '',
      variables: template.variables || [],
      branding_config: template.branding_config || {
        primary_color: '#1E40AF',
        secondary_color: '#64748B',
        font_family: 'Inter, sans-serif'
      }
    }
  } catch (err) {
    showError('Failed to load template')
    router.push('/template-editor')
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  // Validate
  if (!templateData.value.name) {
    showError('Template name is required')
    return
  }
  if (!templateData.value.title) {
    showError('Template title is required')
    return
  }
  if (!templateData.value.html_content) {
    showError('HTML content is required')
    return
  }

  loading.value = true
  try {
    if (props.templateId && props.templateId !== 'new') {
      // Update existing - creates new version
      await templateStore.updateTemplate(props.templateId, templateData.value)
      showSuccess('Template updated successfully!')
    } else {
      // Create new
      const newTemplate = await templateStore.createTemplate(templateData.value)
      showSuccess('Template created successfully!')
      router.push(`/template-editor/${newTemplate.id}`)
    }
  } catch (err) {
    showError('Failed to save template')
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.push('/template-editor')
}

const extractVariables = () => {
  const regex = /\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}/g
  const matches = templateData.value.html_content.matchAll(regex)
  const variables = new Set()
  
  for (const match of matches) {
    variables.add(match[1])
  }
  
  return Array.from(variables)
}

const updateVariables = () => {
  const detected = extractVariables()
  const existingVars = templateData.value.variables.map(v => v.name)
  
  // Add new variables
  detected.forEach(varName => {
    if (!existingVars.includes(varName)) {
      templateData.value.variables.push({
        name: varName,
        description: '',
        example: sampleData.value[varName] || '',
        data_type: 'string',
        required: false
      })
    }
  })
  
  showSuccess(`Found ${detected.length} variables`)
}

function getDefaultHtmlTemplate() {
  const open = String.fromCharCode(123, 123)
  const close = String.fromCharCode(125, 125)
  
  return `<div style="max-width: 800px; margin: 0 auto;">
  <h1>${open} document_type ${close} Template</h1>
  
  <div style="margin: 20px 0;">
    <strong>From:</strong> ${open} company_name ${close}<br>
    <strong>To:</strong> ${open} client_name ${close}<br>
    <strong>Date:</strong> ${open} date ${close}
  </div>
  
  <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    <thead>
      <tr style="background: #f1f5f9;">
        <th style="padding: 10px; text-align: left; border: 1px solid #e2e8f0;">Description</th>
        <th style="padding: 10px; text-align: right; border: 1px solid #e2e8f0;">Amount</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="padding: 10px; border: 1px solid #e2e8f0;">Item 1</td>
        <td style="padding: 10px; text-align: right; border: 1px solid #e2e8f0;">$100.00</td>
      </tr>
    </tbody>
  </table>
  
  <div style="text-align: right; margin-top: 20px;">
    <strong>Total:</strong> ${open} total_amount ${close}
  </div>
</div>`
}

function getDefaultCssTemplate() {
  return `/* Custom styles for your template */
h1 {
  color: #1e293b;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

table {
  font-size: 14px;
}

th {
  font-weight: 600;
}
`
}
</script>

<template>
  <div class="editor-container">
    <!-- Header -->
    <div class="editor-header">
      <button @click="handleCancel" class="back-btn">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
        Back to Templates
      </button>
      <h1 class="editor-title">
        {{ templateId === 'new' ? 'Create Template' : 'Edit Template' }}
      </h1>
    </div>

    <!-- Metadata Form -->
    <div class="metadata-section">
      <div class="form-grid">
        <div class="form-group">
          <label class="form-label">Name <span class="required">*</span></label>
          <input v-model="templateData.name" type="text" class="form-input" placeholder="e.g., invoice-standard" />
        </div>

        <div class="form-group">
          <label class="form-label">Document Type <span class="required">*</span></label>
          <select v-model="templateData.document_type" class="form-input">
            <option v-for="type in documentTypes" :key="type.value" :value="type.value">
              {{ type.label }}
            </option>
          </select>
        </div>

        <div class="form-group full-width">
          <label class="form-label">Title <span class="required">*</span></label>
          <input v-model="templateData.title" type="text" class="form-input" placeholder="e.g., Standard Invoice Template" />
        </div>

        <div class="form-group full-width">
          <label class="form-label">Description</label>
          <textarea v-model="templateData.description" class="form-textarea" rows="2" placeholder="Brief description of this template"></textarea>
        </div>
      </div>
    </div>

    <!-- Editor Area -->
    <div class="editor-area">
      <!-- Left: Code Editor -->
      <div class="code-panel">
        <div class="tab-bar">
          <button
            @click="activeTab = 'html'"
            :class="['tab', { active: activeTab === 'html' }]"
          >
            HTML
          </button>
          <button
            @click="activeTab = 'css'"
            :class="['tab', { active: activeTab === 'css' }]"
          >
            CSS
          </button>
          <button
            @click="activeTab = 'variables'"
            :class="['tab', { active: activeTab === 'variables' }]"
          >
            Variables
          </button>
          <button
            @click="activeTab = 'branding'"
            :class="['tab', { active: activeTab === 'branding' }]"
          >
            Branding
          </button>
          <button
            @click="activeTab = 'assets'"
            :class="['tab', { active: activeTab === 'assets' }]"
          >
            Assets
          </button>
          <button
            v-if="templateId !== 'new'"
            @click="activeTab = 'versions'"
            :class="['tab', { active: activeTab === 'versions' }]"
          >
            Versions
          </button>
        </div>

        <!-- HTML Editor -->
        <div v-show="activeTab === 'html'" class="editor-content">
          <div class="editor-toolbar">
            <button @click="updateVariables" class="toolbar-btn">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"/>
              </svg>
              Detect Variables
            </button>
          </div>
          <textarea
            v-model="templateData.html_content"
            class="code-editor"
            placeholder="Enter your HTML template here. Use {{ variable_name }} for dynamic content."
            spellcheck="false"
          ></textarea>
        </div>

        <!-- CSS Editor -->
        <div v-show="activeTab === 'css'" class="editor-content">
          <textarea
            v-model="templateData.css_content"
            class="code-editor"
            placeholder="Enter custom CSS styles here."
            spellcheck="false"
          ></textarea>
        </div>

        <!-- Variables Tab -->
        <div v-show="activeTab === 'variables'" class="editor-content variables-panel">
          <div class="variables-header">
            <h3>Template Variables</h3>
            <button @click="updateVariables" class="btn btn-secondary btn-sm">
              Scan Template
            </button>
          </div>

          <div v-if="templateData.variables.length === 0" class="empty-variables">
            <p>No variables detected. Use {{ variable_name }} syntax in your HTML.</p>
          </div>

          <div v-else class="variables-list">
            <div v-for="(variable, index) in templateData.variables" :key="index" class="variable-item">
              <div class="variable-name">{{ variable.name }}</div>
              <input
                v-model="variable.description"
                type="text"
                class="variable-input"
                placeholder="Description"
              />
              <input
                v-model="variable.example"
                type="text"
                class="variable-input"
                placeholder="Example value"
              />
            </div>
          </div>
        </div>

        <!-- Branding Tab -->
        <div v-show="activeTab === 'branding'" class="editor-content branding-panel">
          <h3>Branding Configuration</h3>
          
          <div class="branding-form">
            <div class="form-group">
              <label class="form-label">Primary Color</label>
              <div class="color-input-group">
                <input
                  v-model="templateData.branding_config.primary_color"
                  type="color"
                  class="color-picker"
                />
                <input
                  v-model="templateData.branding_config.primary_color"
                  type="text"
                  class="form-input"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Secondary Color</label>
              <div class="color-input-group">
                <input
                  v-model="templateData.branding_config.secondary_color"
                  type="color"
                  class="color-picker"
                />
                <input
                  v-model="templateData.branding_config.secondary_color"
                  type="text"
                  class="form-input"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Font Family</label>
              <input
                v-model="templateData.branding_config.font_family"
                type="text"
                class="form-input"
                placeholder="e.g., Arial, sans-serif"
              />
            </div>
          </div>
        </div>

        <!-- Assets Tab -->
        <div v-show="activeTab === 'assets'" class="editor-content">
          <AssetManager :template-id="templateId" />
        </div>

        <!-- Versions Tab -->
        <div v-show="activeTab === 'versions'" class="editor-content">
          <VersionHistory :template-id="templateId" />
        </div>
      </div>

      <!-- Right: Live Preview -->
      <div class="preview-panel">
        <div class="preview-header">
          <h3>Live Preview</h3>
          <span class="preview-badge">Auto-updating</span>
        </div>
        <div class="preview-container">
          <iframe
            :srcdoc="previewDocument"
            class="preview-frame"
            sandbox="allow-same-origin"
          ></iframe>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="editor-actions">
      <button @click="handleCancel" class="btn btn-secondary" :disabled="loading">
        Cancel
      </button>
      <button @click="handleSave" class="btn btn-primary" :disabled="loading">
        <span v-if="loading">Saving...</span>
        <span v-else>{{ templateId === 'new' ? 'Create Template' : 'Save Changes' }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.editor-container {
  min-height: calc(100vh - 72px);
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.editor-header {
  background: white;
  border-bottom: 2px solid #e2e8f0;
  padding: 1.5rem 2rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #667eea;
  background: none;
  border: none;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 0.75rem;
  transition: all 0.2s;
}

.back-btn:hover {
  color: #764ba2;
}

.back-btn svg {
  width: 20px;
  height: 20px;
}

.editor-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.metadata-section {
  background: white;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.5rem;
}

.required {
  color: #ef4444;
}

.form-input,
.form-textarea {
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.editor-area {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  min-height: 600px;
}

.code-panel,
.preview-panel {
  display: flex;
  flex-direction: column;
  background: white;
}

.code-panel {
  border-right: 2px solid #e2e8f0;
}

.tab-bar {
  display: flex;
  border-bottom: 2px solid #e2e8f0;
  background: #f8fafc;
}

.tab {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: #64748b;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}

.tab:hover {
  color: #667eea;
  background: white;
}

.tab.active {
  color: #667eea;
  background: white;
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #667eea;
}

.editor-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-toolbar {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  gap: 0.5rem;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  background: white;
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.toolbar-btn svg {
  width: 16px;
  height: 16px;
}

.code-editor {
  flex: 1;
  padding: 1rem;
  border: none;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  resize: none;
  background: #fafafa;
}

.code-editor:focus {
  outline: none;
  background: white;
}

.variables-panel,
.branding-panel {
  padding: 1.5rem;
  overflow-y: auto;
}

.variables-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.variables-header h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.empty-variables {
  text-align: center;
  padding: 3rem 1rem;
  color: #94a3b8;
}

.variables-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.variable-item {
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.variable-name {
  font-weight: 700;
  color: #667eea;
  font-family: 'Courier New', monospace;
}

.variable-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.branding-panel h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 1.5rem 0;
}

.branding-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.color-input-group {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.color-picker {
  width: 50px;
  height: 40px;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  cursor: pointer;
}

.preview-panel {
  background: #f8fafc;
}

.preview-header {
  padding: 1rem 1.5rem;
  border-bottom: 2px solid #e2e8f0;
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.preview-badge {
  background: #dcfce7;
  color: #16a34a;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.preview-container {
  flex: 1;
  padding: 1.5rem;
  overflow: hidden;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  background: white;
}

.editor-actions {
  padding: 1.5rem 2rem;
  background: white;
  border-top: 2px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: white;
  color: #1e293b;
  border: 2px solid #e2e8f0;
}

.btn-secondary:hover:not(:disabled) {
  border-color: #cbd5e0;
  background: #f8fafc;
}

@media (max-width: 1024px) {
  .editor-area {
    grid-template-columns: 1fr;
  }

  .code-panel {
    border-right: none;
    border-bottom: 2px solid #e2e8f0;
    min-height: 400px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
