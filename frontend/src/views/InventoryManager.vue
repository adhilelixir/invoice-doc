<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import AddProductModal from '../components/AddProductModal.vue'
import { useNotification } from '../composables/useNotification'

const { showSuccess, showError } = useNotification()

const inventory = ref([])
const loading = ref(true)
const error = ref(null)
const showModal = ref(false)

const fetchInventory = async () => {
  try {
    loading.value = true
    const response = await api.get('/inventory/products')
    inventory.value = response.data.map(product => ({
      id: product.id,
      sku: product.sku,
      name: product.name,
      quantity: product.inventory ? product.inventory.quantity : 0,
      price: product.base_price
    }))
  } catch (err) {
    error.value = 'Failed to load inventory'
    console.error(err)
    showError('Failed to load inventory')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchInventory()
})

const editMode = ref(null)

const toggleEdit = async (id, item) => {
  if (editMode.value === id) {
    // Save changes
    try {
        await api.put(`/inventory/products/${item.sku}/inventory`, {
            quantity: item.quantity,
            bulk_pricing_tiers: [] // Preserve existing or default
        })
        editMode.value = null
        showSuccess('Inventory updated successfully!')
    } catch (err) {
        showError('Failed to save changes')
        console.error(err)
    }
  } else {
    editMode.value = id
  }
}

const handleProductAdded = () => {
  showModal.value = false
  fetchInventory()
}

const getStockStatus = (quantity) => {
  if (quantity === 0) return 'out-of-stock'
  if (quantity < 10) return 'low-stock'
  return 'in-stock'
}

const getStockBadgeClass = (quantity) => {
  const status = getStockStatus(quantity)
  const classes = {
    'out-of-stock': 'badge-red',
    'low-stock': 'badge-yellow',
    'in-stock': 'badge-green'
  }
  return classes[status]
}

const getStockText = (quantity) => {
  const status = getStockStatus(quantity)
  const text = {
    'out-of-stock': 'Out of Stock',
    'low-stock': 'Low Stock',
    'in-stock': 'In Stock'
  }
  return text[status]
}
</script>

<template>
  <div class="inventory-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Inventory Management</h1>
        <p class="page-subtitle">Manage your product inventory and stock levels</p>
      </div>
      <button @click="showModal = true" class="btn btn-primary">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
        </svg>
        Add Product
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Loading inventory...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <p>{{ error }}</p>
      <button @click="fetchInventory" class="btn btn-secondary">Retry</button>
    </div>

    <!-- Empty State -->
    <div v-else-if="inventory.length === 0" class="empty-state">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
      </svg>
      <h3>No products yet</h3>
      <p>Get started by adding your first product</p>
      <button @click="showModal = true" class="btn btn-primary">Add Your First Product</button>
    </div>

    <!-- Inventory Table -->
    <div v-else class="table-section">
      <div class="table-container">
        <table class="modern-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th>Product Name</th>
              <th>Quantity</th>
              <th>Status</th>
              <th>Price</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in inventory" :key="item.id">
              <td class="font-mono text-sm">{{ item.sku }}</td>
              <td class="font-semibold">{{ item.name }}</td>
              <td>
                <div v-if="editMode === item.id" class="quantity-edit">
                  <input 
                    type="number" 
                    v-model="item.quantity" 
                    class="quantity-input"
                    min="0"
                  />
                </div>
                <span v-else class="quantity-display">{{ item.quantity }}</span>
              </td>
              <td>
                <span class="status-badge" :class="getStockBadgeClass(item.quantity)">
                  {{ getStockText(item.quantity) }}
                </span>
              </td>
              <td class="font-semibold price">${{ item.price.toFixed(2) }}</td>
              <td>
                <button 
                  @click="toggleEdit(item.id, item)" 
                  class="action-btn"
                  :class="{ 'action-btn-save': editMode === item.id }"
                >
                  <svg v-if="editMode === item.id" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                  </svg>
                  <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                  {{ editMode === item.id ? 'Save' : 'Edit' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Product Modal -->
    <AddProductModal 
      v-if="showModal" 
      @close="showModal = false"
      @success="handleProductAdded"
    />
  </div>
</template>

<style scoped>
.inventory-page {
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

.btn-secondary {
  background: white;
  color: #1e293b;
  border: 2px solid #e2e8f0;
}

.btn-secondary:hover {
  border-color: #cbd5e0;
  background: #f8fafc;
}

.loading-container,
.error-container,
.empty-state {
  background: white;
  border-radius: 1rem;
  padding: 3rem;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.loading-container svg,
.error-container svg,
.empty-state svg {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem auto;
  color: #94a3b8;
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

.table-section {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-container {
  overflow-x: auto;
}

.modern-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.modern-table thead tr {
  background: #f8fafc;
}

.modern-table th {
  text-align: left;
  padding: 1rem;
  font-weight: 600;
  color: #475569;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid #e2e8f0;
}

.modern-table th:first-child {
  border-top-left-radius: 0.5rem;
}

.modern-table th:last-child {
  border-top-right-radius: 0.5rem;
}

.modern-table td {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
}

.modern-table tbody tr {
  transition: background 0.2s;
}

.modern-table tbody tr:hover {
  background: #f8fafc;
}

.font-mono {
  font-family: 'Courier New', monospace;
}

.font-semibold {
  font-weight: 600;
}

.text-sm {
  font-size: 0.875rem;
}

.price {
  color: #16a34a;
}

.quantity-edit {
  display: flex;
  align-items: center;
}

.quantity-input {
  width: 80px;
  padding: 0.5rem 0.75rem;
  border: 2px solid #667eea;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #1e293b;
}

.quantity-input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.quantity-display {
  font-weight: 600;
  color: #1e293b;
}

.status-badge {
  display: inline-block;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-green {
  background: #dcfce7;
  color: #16a34a;
}

.badge-yellow {
  background: #fef3c7;
  color: #d97706;
}

.badge-red {
  background: #fee2e2;
  color: #dc2626;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: 2px solid #e2e8f0;
  background: white;
  color: #667eea;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.action-btn:hover {
  border-color: #667eea;
  background: #f8fafc;
}

.action-btn-save {
  border-color: #16a34a;
  color: #16a34a;
}

.action-btn-save:hover {
  background: #dcfce7;
}

@media (max-width: 768px) {
  .inventory-page {
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
}
</style>
