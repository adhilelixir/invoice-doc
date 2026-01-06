<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { useNotification } from '../composables/useNotification'

const { showError } = useNotification()

const stats = ref([
  { name: 'Total Revenue', value: '$0', change: '+0%', trend: 'up', icon: 'dollar' },
  { name: 'Pending Orders', value: '0', change: '0', trend: 'neutral', icon: 'orders' },
  { name: 'Low Stock Items', value: '0', change: '0', trend: 'down', icon: 'inventory' },
  { name: 'Documents Generated', value: '0', change: '+0%', trend: 'up', icon: 'documents' },
])

const recentOrders = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await api.get('/orders/')
    recentOrders.value = response.data.slice(0, 5).map(order => ({
      id: order.id,
      customer: order.customer_name || 'Guest',
      amount: `$${order.total_amount?.toFixed(2) || '0.00'}`,
      status: order.status,
      date: new Date(order.created_at).toLocaleDateString()
    }))
    
    // Calculate stats
    const pending = recentOrders.value.filter(o => o.status === 'pending').length
    stats.value[1].value = pending.toString()
    stats.value[1].change = pending > 0 ? `${pending} new` : 'None'
    
    // Get products for low stock
    const products = await api.get('/inventory/products')
    const lowStock = products.data.filter(p => !p.inventory || p.inventory.quantity < 10).length
    stats.value[2].value = lowStock.toString()
    stats.value[2].change = lowStock > 0 ? 'Needs attention' : 'All good'
    stats.value[2].trend = lowStock > 0 ? 'down' : 'neutral'
    
    // Calculate revenue
    const total = recentOrders.value.reduce((acc, curr) => {
      return acc + parseFloat(curr.amount.replace('$', ''))
    }, 0)
    stats.value[0].value = `$${total.toFixed(2)}`
    stats.value[0].change = '+12%'
    
    stats.value[3].value = recentOrders.value.length.toString()
    stats.value[3].change = '+8%'
    
  } catch (err) {
    console.error('Failed to fetch dashboard data', err)
    showError('Failed to load dashboard data')
  } finally {
    loading.value = false
  }
})

const getStatusColor = (status) => {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-blue-100 text-blue-800',
    shipped: 'bg-purple-100 text-purple-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const getTrendColor = (trend) => {
  const colors = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600'
  }
  return colors[trend] || 'text-gray-600'
}
</script>

<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h1 class="dashboard-title">Dashboard</h1>
        <p class="dashboard-subtitle">Welcome back! Here's what's happening today.</p>
      </div>
      <div class="dashboard-actions">
        <router-link to="/inventory" class="btn btn-secondary">
          Manage Inventory
        </router-link>
        <router-link to="/template-editor" class="btn btn-primary">
          Create Document
        </router-link>
      </div>
    </div>

    <!-- Stats Grid -->
    <div v-if="loading" class="stats-grid">
      <div v-for="n in 4" :key="n" class="stat-card skeleton"></div>
    </div>
    
    <div v-else class="stats-grid">
      <div v-for="stat in stats" :key="stat.name" class="stat-card">
        <div class="stat-icon" :class="`stat-icon-${stat.icon}`">
          <svg v-if="stat.icon === 'dollar'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <svg v-else-if="stat.icon === 'orders'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
          </svg>
          <svg v-else-if="stat.icon === 'inventory'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
          </svg>
          <svg v-else fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
        </div>
        <div class="stat-content">
          <p class="stat-name">{{ stat.name }}</p>
          <p class="stat-value">{{ stat.value }}</p>
          <p class="stat-change" :class="getTrendColor(stat.trend)">
            <svg v-if="stat.trend === 'up'" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
            </svg>
            <svg v-else-if="stat.trend === 'down'" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            {{ stat.change }}
          </p>
        </div>
      </div>
    </div>

    <!-- Recent Orders -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">Recent Orders</h2>
      </div>

      <div v-if="loading" class="table-skeleton">
        <div v-for="n in 5" :key="n" class="skeleton-row"></div>
      </div>

      <div v-else-if="recentOrders.length === 0" class="empty-state">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
        </svg>
        <p>No orders yet</p>
      </div>

      <div v-else class="table-container">
        <table class="modern-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer</th>
              <th>Date</th>
              <th>Amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in recentOrders" :key="order.id">
              <td class="font-semibold">#{{ order.id }}</td>
              <td>{{ order.customer }}</td>
              <td class="text-gray-600">{{ order.date }}</td>
              <td class="font-semibold">{{ order.amount }}</td>
              <td>
                <span class="status-badge" :class="getStatusColor(order.status)">
                  {{ order.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <div class="action-card" @click="$router.push('/template-editor')">
        <div class="action-icon action-icon-purple">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
          </svg>
        </div>
        <h3>Edit Templates</h3>
        <p>Customize document templates</p>
      </div>

      <div class="action-card" @click="$router.push('/inventory')">
        <div class="action-icon action-icon-blue">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
          </svg>
        </div>
        <h3>Manage Inventory</h3>
        <p>Update stock levels</p>
      </div>

      <div class="action-card">
        <div class="action-icon action-icon-green">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        <h3>View Analytics</h3>
        <p>Insights and reports</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.dashboard-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.dashboard-subtitle {
  color: #64748b;
  margin: 0.5rem 0 0 0;
}

.dashboard-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.stat-icon-dollar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon-orders {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon-inventory {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon-documents {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-name {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
  font-weight: 500;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0.25rem 0;
}

.stat-change {
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin: 0;
  font-weight: 600;
}

.stat-change svg {
  width: 16px;
  height: 16px;
}

.section {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.view-all {
  color: #667eea;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.view-all:hover {
  color: #764ba2;
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

.status-badge {
  display: inline-block;
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #94a3b8;
}

.empty-state svg {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem auto;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 1rem;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.action-icon {
  width: 56px;
  height: 56px;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem auto;
}

.action-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.action-icon-purple {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.action-icon-blue {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.action-icon-green {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.action-card h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 0.5rem 0;
}

.action-card p {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

/* Loading skeletons */
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.table-skeleton {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.skeleton-row {
  height: 60px;
  border-radius: 0.5rem;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>
