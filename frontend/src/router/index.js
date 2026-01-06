import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import InventoryManager from '../views/InventoryManager.vue'
import TemplateEditor from '../views/TemplateEditor.vue'
import Login from '../views/Login.vue'

const routes = [
    { path: '/login', component: Login, meta: { guest: true } },
    { path: '/', component: Dashboard, meta: { requiresAuth: true } },
    { path: '/inventory', component: InventoryManager, meta: { requiresAuth: true } },
    { path: '/template-editor', component: TemplateEditor, meta: { requiresAuth: true } },
    { path: '/template-editor/:id', component: TemplateEditor, meta: { requiresAuth: true } },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else if (to.meta.guest && token) {
        next('/')
    } else {
        next()
    }
})

export default router
