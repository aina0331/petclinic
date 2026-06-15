

| Page | Description |
| Dashboard | Stats overview + recent appointments |
| Appointments | Full list with date/status filters, add/edit/delete |
| New Appointment | Book with client → pet → vet → service flow |
| Clients | Directory with pet count and booking count |
| Veterinarians | Staff list + weekly schedule table |
| Services | Catalog with duration and pricing |

Database Tables

- `CLIENT` — pet owners
- `PET` — pets linked to clients
- `VETERINARIAN` — clinic doctors
- `VET_SCHEDULE` — weekly availability
- `SERVICE` — available treatments
- `APPOINTMENT` — bookings (with unique constraint on vet + date + time)
