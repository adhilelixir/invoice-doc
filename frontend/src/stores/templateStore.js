import { defineStore } from 'pinia'
import templateService from '../services/templateService'

export const useTemplateStore = defineStore('templates', {
    state: () => ({
        templates: [],
        currentTemplate: null,
        loading: false,
        error: null,
        filters: {
            search: '',
            documentType: null,
            isActive: true
        }
    }),

    getters: {
        // Group templates by document type
        groupedTemplates: (state) => {
            const filtered = state.templates.filter(template => {
                // Apply search filter
                if (state.filters.search) {
                    const search = state.filters.search.toLowerCase()
                    const matchesSearch =
                        template.name.toLowerCase().includes(search) ||
                        template.title.toLowerCase().includes(search) ||
                        (template.description && template.description.toLowerCase().includes(search))

                    if (!matchesSearch) return false
                }

                // Apply document type filter
                if (state.filters.documentType && template.document_type !== state.filters.documentType) {
                    return false
                }

                // Apply active filter
                if (state.filters.isActive !== null && template.is_active !== state.filters.isActive) {
                    return false
                }

                return true
            })

            // Group by document type
            const grouped = {}
            filtered.forEach(template => {
                const type = template.document_type
                if (!grouped[type]) {
                    grouped[type] = []
                }
                grouped[type].push(template)
            })

            return grouped
        },

        // Get template by ID
        getTemplateById: (state) => (id) => {
            return state.templates.find(t => t.id === id)
        },

        // Count templates
        totalCount: (state) => state.templates.length,

        // Count active templates
        activeCount: (state) => state.templates.filter(t => t.is_active).length
    },

    actions: {
        async fetchTemplates(filters = {}) {
            this.loading = true
            this.error = null

            try {
                this.templates = await templateService.listTemplates(filters)
            } catch (err) {
                this.error = err.response?.data?.detail || 'Failed to fetch templates'
                console.error('Failed to fetch templates:', err)
            } finally {
                this.loading = false
            }
        },

        async fetchTemplate(id) {
            this.loading = true
            this.error = null

            try {
                this.currentTemplate = await templateService.getTemplate(id)
                return this.currentTemplate
            } catch (err) {
                this.error = err.response?.data?.detail || 'Failed to fetch template'
                console.error('Failed to fetch template:', err)
                throw err
            } finally {
                this.loading = false
            }
        },

        async createTemplate(template) {
            this.loading = true
            this.error = null

            try {
                const newTemplate = await templateService.createTemplate(template)
                this.templates.push(newTemplate)
                return newTemplate
            } catch (err) {
                this.error = err.response?.data?.detail || 'Failed to create template'
                console.error('Failed to create template:', err)
                throw err
            } finally {
                this.loading = false
            }
        },

        async updateTemplate(id, updates) {
            this.loading = true
            this.error = null

            try {
                const updatedTemplate = await templateService.updateTemplate(id, updates)

                // Update in list
                const index = this.templates.findIndex(t => t.id === id)
                if (index !== -1) {
                    this.templates[index] = updatedTemplate
                }

                // Update current if it's the same
                if (this.currentTemplate?.id === id) {
                    this.currentTemplate = updatedTemplate
                }

                return updatedTemplate
            } catch (err) {
                this.error = err.response?.data?.detail || 'Failed to update template'
                console.error('Failed to update template:', err)
                throw err
            } finally {
                this.loading = false
            }
        },

        async deleteTemplate(id) {
            this.loading = true
            this.error = null

            try {
                await templateService.deleteTemplate(id)

                // Remove from list or mark as inactive
                const index = this.templates.findIndex(t => t.id === id)
                if (index !== -1) {
                    this.templates[index].is_active = false
                }
            } catch (err) {
                this.error = err.response?.data?.detail || 'Failed to delete template'
                console.error('Failed to delete template:', err)
                throw err
            } finally {
                this.loading = false
            }
        },

        async duplicateTemplate(id, newName) {
            this.loading = true
            this.error = null

            try {
                const duplicate = await templateService.duplicateTemplate(id, newName)
                this.templates.push(duplicate)
                return duplicate
            } catch (err) {
                this.error = err.response?.data?.detail || 'Failed to duplicate template'
                console.error('Failed to duplicate template:', err)
                throw err
            } finally {
                this.loading = false
            }
        },

        setFilter(key, value) {
            this.filters[key] = value
        },

        resetFilters() {
            this.filters = {
                search: '',
                documentType: null,
                isActive: true
            }
        },

        clearCurrentTemplate() {
            this.currentTemplate = null
        }
    }
})
