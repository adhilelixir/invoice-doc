import { reactive } from 'vue'

let toastId = 0

export const toastState = reactive({
    toasts: [],

    addToast(message, type = 'info', duration = 3000) {
        const id = ++toastId
        const toast = { id, message, type }

        this.toasts.push(toast)

        if (duration > 0) {
            setTimeout(() => {
                this.removeToast(id)
            }, duration)
        }

        return id
    },

    removeToast(id) {
        const index = this.toasts.findIndex(t => t.id === id)
        if (index > -1) {
            this.toasts.splice(index, 1)
        }
    }
})

export function useNotification() {
    const showSuccess = (message, duration = 3000) => {
        return toastState.addToast(message, 'success', duration)
    }

    const showError = (message, duration = 5000) => {
        return toastState.addToast(message, 'error', duration)
    }

    const showWarning = (message, duration = 4000) => {
        return toastState.addToast(message, 'warning', duration)
    }

    const showInfo = (message, duration = 3000) => {
        return toastState.addToast(message, 'info', duration)
    }

    return {
        showSuccess,
        showError,
        showWarning,
        showInfo
    }
}
