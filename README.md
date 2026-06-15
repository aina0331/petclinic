
Database Tables

- `CLIENT` — pet owners
- `PET` — pets linked to clients
- `VETERINARIAN` — clinic doctors
- `VET_SCHEDULE` — weekly availability
- `SERVICE` — available treatments
- `APPOINTMENT` — bookings (with unique constraint on vet + date + time)
