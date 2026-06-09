# 🐾 PawCare — Pet Clinic Appointment System

A Python Flask + SQLite web application for managing pet clinic appointments.

---

## 📁 Project Structure

```
petclinic/
├── app.py                  ← Main Flask application (routes + DB logic)
├── petclinic.db            ← SQLite database (auto-created on first run)
├── requirements.txt
└── templates/
    ├── base.html           ← Shared layout (sidebar, styles)
    ├── dashboard.html      ← Homepage with stats
    ├── appointments.html   ← Appointments list with filters
    ├── appointment_form.html ← Book / edit appointment
    ├── clients.html        ← Client directory
    ├── client_form.html    ← Add / edit client
    ├── vets.html           ← Vet directory + schedules
    └── services.html       ← Service catalog
```

---

## ⚙️ Setup & Run

### 1. Install Python (3.9+)
Download from https://python.org

### 2. Install Flask
```bash
pip install flask
```

### 3. Run the app
```bash
cd petclinic
python app.py
```

### 4. Open your browser
```
http://127.0.0.1:5000
```

The database is created automatically on first run with sample data.

---

## 🗂️ Features

| Page | Description |
|------|-------------|
| Dashboard | Stats overview + recent appointments |
| Appointments | Full list with date/status filters, add/edit/delete |
| New Appointment | Book with client → pet → vet → service flow |
| Clients | Directory with pet count and booking count |
| Veterinarians | Staff list + weekly schedule table |
| Services | Catalog with duration and pricing |

---

## 🗄️ Database Tables

- `CLIENT` — pet owners
- `PET` — pets linked to clients
- `VETERINARIAN` — clinic doctors
- `VET_SCHEDULE` — weekly availability
- `SERVICE` — available treatments
- `APPOINTMENT` — bookings (with unique constraint on vet + date + time)
