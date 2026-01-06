<script setup>
import { ref, onMounted, watch } from 'vue'
import templateService from '../services/templateService'
import { useNotification } from '../composables/useNotification'

const props = defineProps({
  templateId: {
    type: [String, Number],
    required: true
  }
})

const { showSuccess, showError } = useNotification()

const assets = ref([])
const loading = ref(false)
const uploading = ref(false)
const dragOver = ref(false)

const assetTypes = [
  { value: 'logo', label: 'Logo' },
  { value: 'image', label: 'Image' },
  { value: 'signature', label: 'Signature' },
  { value: 'watermark', label: 'Watermark' }
]

const newAsset = ref({
  file: null,
  asset_type: 'logo',
  name: '',
  description: '',
  is_default: false
})

onMounted(() => {
  loadAssets()
})

watch(() => props.templateId, () => {
  loadAssets()
})

const loadAssets = async () => {
  if (!props.templateId || props.templateId === 'new') return

  loading.value = true
  try {
    assets.value = await templateService.listAssets(props.templateId)
  } catch (err) {
    console.error('Failed to load assets:', err)
  } finally {
    loading.value = false
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    newAsset.value.file = file
    if (!newAsset.value.name) {
      newAsset.value.name = file.name.split('.')[0]
    }
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  dragOver.value = false
  
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    newAsset.value.file = file
    if (!newAsset.value.name) {
      newAsset.value.name = file.name.split('.')[0]
    }
  } else {
    showError('Please upload an image file')
  }
}

const handleDragOver = (event) => {
  event.preventDefault()
  dragOver.value = true
}

const handleDragLeave = () => {
  dragOver.value = false
}

const handleUpload = async () => {
  if (!newAsset.value.file) {
    showError('Please select a file')
    return
  }

  if (!newAsset.value.name) {
    showError('Please enter an asset name')
    return
  }

  if (props.templateId === 'new') {
    showError('Please save the template first before uploading assets')
    return
  }

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', newAsset.value.file)
    formData.append('asset_type', newAsset.value.asset_type)
    formData.append('name', newAsset.value.name)
    formData.append('description', newAsset.value.description || '')
    formData.append('is_default', newAsset.value.is_default)

    await templateService.uploadAsset(props.templateId, formData)
    
    showSuccess('Asset uploaded successfully!')
    
    // Reset form
    newAsset.value = {
      file: null,
      asset_type: 'logo',
      name: '',
      description: '',
      is_default: false
    }
    
    // Clear file input
    const fileInput = document.querySelector('input[type="file"]')
    if (fileInput) fileInput.value = ''
    
    // Reload assets
    await loadAssets()
  } catch (err) {
    showError('Failed to upload asset')
    console.error(err)
  } finally {
    uploading.value = false
  }
}

const handleDelete = async (assetId) => {
  if (!confirm('Are you sure you want to delete this asset?')) return

  try {
    await templateService.deleteAsset(props.templateId, assetId)
    showSuccess('Asset deleted successfully!')
    await loadAssets()
  } catch (err) {
    showError('Failed to delete asset')
    console.error(err)
  }
}

const getAssetUrl = (asset) => {
  // In production, this would be the actual asset URL
  // For now, we'll use a placeholder
  return asset.file_path
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const getAssetTypeColor = (type) => {
  const colors = {
    logo: 'bg-blue-100 text-blue-800',
    image: 'bg-green-100 text-green-800',
    signature: 'bg-purple-100 text-purple-800',
    watermark: 'bg-orange-100 text-orange-800'
  }
  return colors[type] || 'bg-gray-100 text-gray-800'
}
</script>

<template>
  <div class="asset-manager">
    <div class="asset-manager-header">
      <h3>Template Assets</h3>
      <span class="asset-count">{{ assets.length }} {{ assets.length === 1 ? 'asset' : 'assets' }}</span>
    </div>

    <!-- Upload Section -->
    <div class="upload-section">
      <h4>Upload New Asset</h4>
      
      <div
        class="dropzone"
        :class="{ 'drag-over': dragOver }"
        @drop="handleDrop"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
      >
        <input
          type="file"
          accept="image/*"
          @change="handleFileSelect"
          class="file-input"
          id="asset-file-input"
        />
        <label for="asset-file-input" class="dropzone-label">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
          </svg>
          <span v-if="newAsset.file">{{ newAsset.file.name }}</span>
          <span v-else>Drop image here or click to browse</span>
        </label>
      </div>

      <div class="upload-form">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Asset Type</label>
            <select v-model="newAsset.asset_type" class="form-input">
              <option v-for="type in assetTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Name <span class="required">*</span></label>
            <input v-model="newAsset.name" type="text" class="form-input" placeholder="e.g., Company Logo" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Description</label>
          <input v-model="newAsset.description" type="text" class="form-input" placeholder="Optional description" />
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="newAsset.is_default" />
            <span>Set as default {{ newAsset.asset_type }}</span>
          </label>
        </div>

        <button
          @click="handleUpload"
          :disabled="!newAsset.file || !newAsset.name || uploading"
          class="btn btn-primary"
        >
          <span v-if="uploading">Uploading...</span>
          <span v-else>Upload Asset</span>
        </button>
      </div>
    </div>

    <!-- Assets Gallery -->
    <div class="assets-section">
      <h4>Current Assets</h4>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading assets...</p>
      </div>

      <div v-else-if="assets.length === 0" class="empty-state">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
        <p>No assets uploaded yet</p>
      </div>

      <div v-else class="assets-grid">
        <div v-for="asset in assets" :key="asset.id" class="asset-card">
          <div class="asset-preview">
            <img :src="getAssetUrl(asset)" :alt="asset.name" loading="lazy" />
            <div v-if="asset.is_default" class="default-badge">Default</div>
          </div>
          
          <div class="asset-info">
            <div class="asset-header">
              <h5 class="asset-name">{{ asset.name }}</h5>
              <span :class="['asset-type-badge', getAssetTypeColor(asset.asset_type)]">
                {{ asset.asset_type }}
              </span>
            </div>
            
            <p v-if="asset.description" class="asset-description">{{ asset.description }}</p>
            
            <div class="asset-meta">
              <span class="meta-item">{{ formatFileSize(asset.file_size) }}</span>
              <span v-if="asset.width && asset.height" class="meta-item">
                {{ asset.width }}×{{ asset.height }}
              </span>
            </div>

            <button @click="handleDelete(asset.id)" class="delete-btn">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.asset-manager {
  padding: 1.5rem;
  height: 100%;
  overflow-y: auto;
}

.asset-manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.asset-manager-header h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.asset-count {
  background: #f1f5f9;
  color: #64748b;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.upload-section {
  background: #f8fafc;
  border: 2px dashed #cbd5e0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.upload-section h4 {
  font-size: 1rem;
  font-weight: 700;
  color: #475569;
  margin: 0 0 1rem 0;
}

.dropzone {
  border: 2px dashed #cbd5e0;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  transition: all 0.2s;
  background: white;
  margin-bottom: 1.5rem;
}

.dropzone.drag-over {
  border-color: #667eea;
  background: #f0f4ff;
}

.file-input {
  display: none;
}

.dropzone-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  color: #64748b;
}

.dropzone-label svg {
  width: 48px;
  height: 48px;
  color: #94a3b8;
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
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

.form-input {
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #64748b;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
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

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.assets-section h4 {
  font-size: 1rem;
  font-weight: 700;
  color: #475569;
  margin: 0 0 1rem 0;
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

.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.asset-card {
  border: 2px solid #e2e8f0;
  border-radius: 0.75rem;
  overflow: hidden;
  background: white;
  transition: all 0.2s;
}

.asset-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.asset-preview {
  position: relative;
  width: 100%;
  height: 180px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.asset-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.default-badge {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: #16a34a;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.asset-info {
  padding: 1rem;
}

.asset-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  gap: 0.5rem;
}

.asset-name {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
  flex: 1;
}

.asset-type-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.asset-description {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}

.asset-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f1f5f9;
}

.meta-item {
  font-size: 0.8125rem;
  color: #94a3b8;
}

.delete-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border: 2px solid #fecaca;
  border-radius: 0.5rem;
  background: #fef2f2;
  color: #dc2626;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #dc2626;
  color: white;
  border-color: #dc2626;
}

.delete-btn svg {
  width: 16px;
  height: 16px;
}
</style>
