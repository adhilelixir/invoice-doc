<script setup>
import { ref } from 'vue'
import api from '../api'
import { useNotification } from '../composables/useNotification'

const emit = defineEmits(['close', 'success'])
const { showSuccess, showError } = useNotification()

const formData = ref({
  sku: '',
  name: '',
  description: '',
  base_price: 0,
  quantity: 0
})

const errors = ref({})
const loading = ref(false)

const validateForm = () => {
  errors.value = {}
  
  if (!formData.value.sku.trim()) {
    errors.value.sku = 'SKU is required'
  }
  
  if (!formData.value.name.trim()) {
    errors.value.name = 'Product name is required'
  }
  
  if (formData.value.base_price <= 0) {
    errors.value.base_price = 'Price must be greater than 0'
  }
  
  if (formData.value.quantity < 0) {
    errors.value.quantity = 'Quantity cannot be negative'
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }
  
  loading.value = true
  
  try {
    const payload = {
      sku: formData.value.sku,
      name: formData.value.name,
      description: formData.value.description || null,
      base_price: parseFloat(formData.value.base_price),
      inventory: {
        quantity: parseInt(formData.value.quantity),
        bulk_pricing_tiers: []
      }
    }
    
    await api.post('/inventory/products', payload)
    showSuccess('Product added successfully!')
    emit('success')
    emit('close')
  } catch (err) {
    console.error('Failed to add product:', err)
    if (err.response?.data?.detail) {
      showError(err.response.data.detail)
    } else {
      showError('Failed to add product. Please try again.')
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal-container">
      <div class="modal-header">
        <h2 class="modal-title">Add New Product</h2>
        <button @click="handleClose" class="close-btn" aria-label="Close">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="modal-body">
        <div class="form-grid">
          <!-- SKU -->
          <div class="form-group">
            <label for="sku" class="form-label">
              SKU <span class="required">*</span>
            </label>
            <input
              id="sku"
              v-model="formData.sku"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.sku }"
              placeholder="e.g., PROD-001"
            />
            <p v-if="errors.sku" class="error-message">{{ errors.sku }}</p>
          </div>
          
          <!-- Name -->
          <div class="form-group">
            <label for="name" class="form-label">
              Product Name <span class="required">*</span>
            </label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.name }"
              placeholder="e.g., Premium Widget"
            />
            <p v-if="errors.name" class="error-message">{{ errors.name }}</p>
          </div>
          
          <!-- Description -->
          <div class="form-group full-width">
            <label for="description" class="form-label">Description</label>
            <textarea
              id="description"
              v-model="formData.description"
              class="form-textarea"
              placeholder="Optional product description"
              rows="3"
            ></textarea>
          </div>
          
          <!-- Price -->
          <div class="form-group">
            <label for="price" class="form-label">
              Base Price <span class="required">*</span>
            </label>
            <div class="input-prefix">
              <span class="prefix">$</span>
              <input
                id="price"
                v-model="formData.base_price"
                type="number"
                step="0.01"
                min="0"
                class="form-input with-prefix"
                :class="{ 'input-error': errors.base_price }"
                placeholder="0.00"
              />
            </div>
            <p v-if="errors.base_price" class="error-message">{{ errors.base_price }}</p>
          </div>
          
          <!-- Quantity -->
          <div class="form-group">
            <label for="quantity" class="form-label">Initial Quantity</label>
            <input
              id="quantity"
              v-model="formData.quantity"
              type="number"
              min="0"
              class="form-input"
              :class="{ 'input-error': errors.quantity }"
              placeholder="0"
            />
            <p v-if="errors.quantity" class="error-message">{{ errors.quantity }}</p>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" @click="handleClose" class="btn btn-secondary" :disabled="loading">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            <span v-if="loading">Adding...</span>
            <span v-else>Add Product</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 1rem;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 0.5rem;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #1e293b;
}

.close-btn svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: 2rem;
  overflow-y: auto;
  max-height: calc(90vh - 140px);
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
  color: #1e293b;
  transition: all 0.2s;
  background: white;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-error {
  border-color: #ef4444 !important;
}

.input-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
}

.error-message {
  font-size: 0.75rem;
  color: #ef4444;
  margin-top: 0.25rem;
}

.input-prefix {
  position: relative;
  display: flex;
  align-items: center;
}

.prefix {
  position: absolute;
  left: 1rem;
  color: #64748b;
  font-weight: 600;
  pointer-events: none;
}

.form-input.with-prefix {
  padding-left: 2rem;
}

.modal-footer {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
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

.btn-secondary {
  background: white;
  color: #1e293b;
  border: 2px solid #e2e8f0;
}

.btn-secondary:hover:not(:disabled) {
  border-color: #cbd5e0;
  background: #f8fafc;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-header,
  .modal-body {
    padding: 1.5rem;
  }
}
</style>
