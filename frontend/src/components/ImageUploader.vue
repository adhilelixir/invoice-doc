<template>
  <div class="image-uploader">
    <div
      class="upload-zone"
      :class="{ 'drag-over': isDragging, 'has-image': imagePreview }"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/gif,image/webp,image/svg+xml"
        @change="handleFileSelect"
        class="hidden"
      />
      
      <div v-if="!imagePreview" class="upload-prompt">
        <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
        </svg>
        <p class="upload-text">Drag and drop your image here</p>
        <p class="upload-subtext">or click to browse</p>
        <p class="upload-hint">PNG, JPG, GIF, SVG, WEBP (max {{ maxSizeMB }}MB)</p>
      </div>
      
      <div v-else class="preview-container">
        <img :src="imagePreview" :alt="fileName" class="preview-image" />
        <div class="preview-overlay">
          <button @click.stop="removeImage" class="remove-btn">
            <svg  fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="preview-info">
          <p class="file-name">{{ fileName }}</p>
          <p class="file-size">{{ fileSizeFormatted }}</p>
        </div>
      </div>
    </div>
    
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [File, String, null],
    default: null
  },
  maxSizeMB: {
    type: Number,
    default: 10
  },
  existingUrl: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const isDragging = ref(false)
const imagePreview = ref(props.existingUrl || null)
const fileName = ref('')
const fileSize = ref(0)
const error = ref('')

const fileSizeFormatted = computed(() => {
  if (fileSize.value === 0) return ''
  const kb = fileSize.value / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  return `${(kb / 1024).toFixed(1)} MB`
})

const handleDragOver = () => {
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = (e) => {
  isDragging.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const processFile = (file) => {
  error.value = ''
  
  // Validate file type
  const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp', 'image/svg+xml']
  if (!validTypes.includes(file.type)) {
    error.value = 'Invalid file type. Please upload PNG, JPG, GIF, SVG, or WEBP image.'
    return
  }
  
  // Validate file size
  const maxSizeBytes = props.maxSizeMB * 1024 * 1024
  if (file.size > maxSizeBytes) {
    error.value = `File size exceeds ${props.maxSizeMB}MB limit.`
    return
  }
  
  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
    fileName.value = file.name
    fileSize.value = file.size
    emit('update:modelValue', file)
  }
  reader.readAsDataURL(file)
}

const removeImage = () => {
  imagePreview.value = null
  fileName.value = ''
  fileSize.value = 0
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('update:modelValue', null)
}
</script>

<style scoped>
.image-uploader {
  width: 100%;
}

.upload-zone {
  border: 2px dashed #cbd5e0;
  border-radius: 0.75rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8fafc;
  position: relative;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-zone:hover {
  border-color: #4f46e5;
  background: #eef2ff;
}

.upload-zone.drag-over {
  border-color: #4f46e5;
  background: #dbeafe;
  transform: scale(1.02);
}

.upload-zone.has-image {
  padding: 0;
  border-style: solid;
}

.hidden {
  display: none;
}

.upload-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.upload-icon {
  width: 64px;
  height: 64px;
  color: #94a3b8;
}

.upload-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.upload-subtext {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.upload-hint {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

.preview-container {
  width: 100%;
  position: relative;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
  border-radius: 0.5rem;
}

.preview-overlay {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}

.remove-btn {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.remove-btn:hover {
  background: #dc2626;
  transform: scale(1.1);
}

.remove-btn svg {
  width: 16px;
  height: 16px;
}

.preview-info {
  margin-top: 1rem;
  text-align: left;
  padding: 0 1rem 1rem 1rem;
}

.file-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  word-break: break-all;
}

.file-size {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  font-weight: 500;
}
</style>
