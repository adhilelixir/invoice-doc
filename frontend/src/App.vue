<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import NotificationToast from './components/NotificationToast.vue'

const router = useRouter()
const route = useRoute()

const showNav = computed(() => {
  return route.path !== '/login'
})

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<template>
  <div class="app-container">
    <!-- Notification Toast -->
    <NotificationToast />
    
    <!-- Navigation -->
    <nav v-if="showNav" class="navbar">
      <div class="nav-content">
        <div class="nav-left">
          <div class="brand">
            <div class="brand-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <div>
              <h1 class="brand-title">B2B Nexus</h1>
              <p class="brand-subtitle">Document & Inventory</p>
            </div>
          </div>
          
          <div class="nav-links">
            <router-link to="/" :class="['nav-link', { active: isActive('/') && route.path === '/' }]">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
              </svg>
              Dashboard
            </router-link>
            
            <router-link to="/inventory" :class="['nav-link', { active: isActive('/inventory') }]">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
              </svg>
              Inventory
            </router-link>
            
            <router-link to="/template-editor" :class="['nav-link', { active: isActive('/template-editor') }]">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
              Templates
            </router-link>
          </div>
        </div>
        
        <div class="nav-right">
          <div class="user-menu">
            <div class="user-avatar">
              <svg fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
              </svg>
            </div>
            <button @click="handleLogout" class="logout-btn">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content" :class="{ 'with-nav': showNav }">
      <router-view></router-view>
    </main>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-attachment: fixed;
}

.navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 50;
}

.nav-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 72px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 3rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.brand-icon svg {
  width: 28px;
  height: 28px;
}

.brand-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #1e293b;
  margin: 0;
  letter-spacing: -0.02em;
}

.brand-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
  font-weight: 500;
}

.nav-links {
  display: flex;
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: 0.5rem;
  text-decoration: none;
  color: #64748b;
  font-weight: 600;
  font-size: 0.875rem;
  transition: all 0.2s;
  position: relative;
}

.nav-link svg {
  width: 20px;
  height: 20px;
}

.nav-link:hover {
  color: #667eea;
  background: #f1f5f9;
}

.nav-link.active {
  color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px 3px 0 0;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-avatar svg {
  width: 24px;
  height: 24px;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: transparent;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  color: #64748b;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn svg {
  width: 18px;
  height: 18px;
}

.logout-btn:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: #fef2f2;
}

.main-content {
  min-height: 100vh;
}

.main-content.with-nav {
  min-height: calc(100vh - 72px);
}

@media (max-width: 768px) {
  .nav-content {
    padding: 0 1rem;
    flex-direction: column;
    gap: 1rem;
    padding-top: 1rem;
    padding-bottom: 1rem;
  }
  
  .nav-left {
    flex-direction: column;
    gap: 1rem;
    width: 100%;
  }
  
  .nav-links {
    width: 100%;
    flex-direction: column;
  }
  
  .nav-link {
    width: 100%;
  }
  
  .brand-subtitle {
    display: none;
  }
}
</style>
