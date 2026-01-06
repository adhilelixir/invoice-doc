import api from '../api'

const templateService = {
    // List templates with optional filtering
    async listTemplates(filters = {}) {
        const params = new URLSearchParams()

        if (filters.documentType) {
            params.append('document_type', filters.documentType)
        }
        if (filters.isActive !== undefined) {
            params.append('is_active', filters.isActive)
        }
        if (filters.skip) {
            params.append('skip', filters.skip)
        }
        if (filters.limit) {
            params.append('limit', filters.limit)
        }

        const queryString = params.toString()
        const url = `/templates${queryString ? '?' + queryString : ''}`
        const response = await api.get(url)
        return response.data
    },

    // Get single template by ID
    async getTemplate(id) {
        const response = await api.get(`/templates/${id}`)
        return response.data
    },

    // Create new template
    async createTemplate(template) {
        const response = await api.post('/templates', template)
        return response.data
    },

    // Update existing template
    async updateTemplate(id, updates) {
        const response = await api.put(`/templates/${id}`, updates)
        return response.data
    },

    // Delete template (soft delete)
    async deleteTemplate(id) {
        await api.delete(`/templates/${id}`)
    },

    // Duplicate template
    async duplicateTemplate(id, newName) {
        const response = await api.post(`/templates/${id}/duplicate`, null, {
            params: { new_name: newName }
        })
        return response.data
    },

    // Generate PDF preview
    async previewTemplate(id, data) {
        const response = await api.post(`/templates/${id}/preview`, data, {
            responseType: 'blob'
        })
        return response.data
    },

    // Asset management
    async uploadAsset(templateId, formData) {
        const response = await api.post(`/templates/${templateId}/assets`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        return response.data
    },

    async listAssets(templateId, assetType = null) {
        const url = `/templates/${templateId}/assets${assetType ? `?asset_type=${assetType}` : ''}`
        const response = await api.get(url)
        return response.data
    },

    async deleteAsset(templateId, assetId) {
        await api.delete(`/templates/${templateId}/assets/${assetId}`)
    }
}

export default templateService
