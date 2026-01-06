# 📄 B2B Document & Inventory Nexus

A modern, enterprise-grade platform for B2B document management and inventory control. Generate professional invoices, agreements, quotes, and more with customizable templates, branding, and automation.

![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## ✨ Features

### 🎨 Document Generation
- **Professional Templates** - Modern, print-optimized templates for 6 document types
  - Invoices
  - Agreements
  - Quotes
  - Receipts
  - Purchase Orders
  - Delivery Notes
- **Custom Branding** - Upload logos, customize colors and fonts
- **QR Code Generation** - Add verification QR codes to documents
- **Watermarks** - Apply watermarks to draft documents
- **PDF Export** - High-quality PDF generation with image embedding

### 🔧 Template Management
- **Version Control** - Track and manage template versions
- **Template Inheritance** - Build templates from existing ones
- **Asset Management** - Upload and organize images, logos, and assets
- **Rich Metadata** - Comprehensive template metadata support

### 💻 Modern UI/UX
- **Beautiful Dashboard** - Gradient stat cards with trend indicators
- **Drag & Drop** - Easy file upload with preview
- **Toast Notifications** - Real-time feedback for user actions
- **Responsive Design** - Works seamlessly on mobile, tablet, and desktop
- **Loading States** - Skeleton screens for better perceived performance

---

## 🏗️ Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Cache:** Redis
- **ORM:** SQLAlchemy
- **PDF Generation:** WeasyPrint
- **Authentication:** JWT (python-jose)
- **Image Processing:** Pillow

### Frontend
- **Framework:** Vue.js 3
- **Build Tool:** Vite
- **Styling:** Tailwind CSS 4
- **State Management:** Pinia
- **HTTP Client:** Axios
- **Routing:** Vue Router

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL
- Redis

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database:**
   ```bash
   # Edit docker-compose.yml or use your own PostgreSQL instance
   ./deploy_postgres.sh
   ```

5. **Configure environment variables:**
   Create a `.env` file in the backend directory:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   REDIS_URL=redis://localhost:6379
   SECRET_KEY=your-secret-key-here
   UPLOAD_DIR=./uploads
   ```

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   API will be available at `http://localhost:8000`
   
   Interactive API docs at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

   App will be available at `http://localhost:5173`

4. **Build for production:**
   ```bash
   npm run build
   ```

---

## 📁 Project Structure

```
invoice-doc/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, security, dependencies
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   └── templates/     # HTML templates for PDFs
│   ├── uploads/           # File uploads (gitignored)
│   ├── requirements.txt
│   └── docker-compose.yml
│
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable Vue components
│   │   ├── composables/   # Vue composables
│   │   ├── views/         # Page components
│   │   ├── router/        # Vue Router config
│   │   └── stores/        # Pinia stores
│   ├── public/            # Static assets
│   └── package.json
│
└── README.md
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user

### Templates
- `GET /api/v1/templates` - List all templates
- `POST /api/v1/templates` - Create new template
- `GET /api/v1/templates/{id}` - Get template details
- `PUT /api/v1/templates/{id}` - Update template
- `DELETE /api/v1/templates/{id}` - Delete template
- `POST /api/v1/templates/generate` - Generate document from template

### Assets
- `POST /api/v1/templates/{id}/assets` - Upload asset to template
- `GET /api/v1/templates/{id}/assets` - List template assets
- `DELETE /api/v1/assets/{id}` - Delete asset

### Documents
- `GET /api/v1/documents` - List all documents
- `POST /api/v1/documents` - Create new document
- `GET /api/v1/documents/{id}/pdf` - Download document as PDF

For full API documentation, visit `/docs` when running the backend server.

---

## 🎯 Usage Example

### Generate a Branded Invoice

```javascript
// 1. Upload company logo
const formData = new FormData()
formData.append('file', logoFile)
formData.append('asset_type', 'logo')
formData.append('name', 'Company Logo')

await axios.post(`/api/v1/templates/${templateId}/assets`, formData, {
  headers: { 'Authorization': `Bearer ${token}` }
})

// 2. Generate invoice with branding
const response = await axios.post('/api/v1/templates/generate', {
  template_id: templateId,
  data: {
    invoice_number: "INV-2026-001",
    customer_name: "Acme Corporation",
    date: "2026-01-06",
    total_amount: 1500.00,
    items: [
      { description: "Product A", quantity: 2, price: 500.00 },
      { description: "Product B", quantity: 1, price: 500.00 }
    ]
  }
}, {
  headers: { 'Authorization': `Bearer ${token}` }
})

// 3. Download PDF
window.open(response.data.pdf_url, '_blank')
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test  # (if configured)
```

---

## 🎨 Design System

### Color Palette
- **Primary:** Purple-blue gradients (`#8B5CF6` to `#3B82F6`)
- **Success:** Green (`#10B981`)
- **Warning:** Amber (`#F59E0B`)
- **Error:** Red (`#EF4444`)

### Typography
- **Font Family:** Inter (Google Fonts) with system fallbacks
- **Headings:** Bold, various sizes
- **Body:** Regular, 16px base

### Components
- **Cards:** Elevated with shadows, rounded corners, hover effects
- **Buttons:** Gradient backgrounds, smooth transitions
- **Forms:** Clean inputs with focus states
- **Icons:** Heroicons (outline style)

---

## 🛠️ Development

### Code Style
- **Backend:** Follow PEP 8 (Python style guide)
- **Frontend:** Follow Vue.js style guide

### Pre-commit Hooks (Recommended)
```bash
pip install pre-commit
pre-commit install
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## 📊 Roadmap

### Upcoming Features
- [ ] Database migrations with Alembic
- [ ] Cloud storage integration (S3/Azure)
- [ ] Email delivery integration
- [ ] Digital signatures
- [ ] Multi-language support
- [ ] Rich text template editor
- [ ] Drag-and-drop layout builder
- [ ] Advanced analytics with Chart.js
- [ ] Dark mode
- [ ] Enhanced inventory management

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Elixire Tech**

---

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Vue.js for the reactive UI framework
- Tailwind CSS for utility-first styling
- WeasyPrint for PDF generation
- The open-source community

---

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Made with ❤️ by Elixire Tech**
