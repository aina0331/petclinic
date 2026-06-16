from flask import Flask, render_template, request, redirect, url_for, flash, jsonify # type: ignore
import sqlite3, os
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = "petclinic_secret_2024"
DB = "petclinic.db"

# DB
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS CLIENT (
            client_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name     TEXT NOT NULL,
            last_name      TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            email          TEXT NOT NULL UNIQUE,
            address        TEXT,
            created_at     TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS VETERINARIAN (
            vet_id         INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name     TEXT NOT NULL,
            last_name      TEXT NOT NULL,
            specialization TEXT,
            contact_number TEXT NOT NULL,
            is_active      INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS VET_SCHEDULE (
            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vet_id      INTEGER NOT NULL,
            day_of_week TEXT NOT NULL,
            start_time  TEXT NOT NULL,
            end_time    TEXT NOT NULL,
            FOREIGN KEY (vet_id) REFERENCES VETERINARIAN(vet_id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS SERVICE (
            service_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name     TEXT NOT NULL,
            description      TEXT,
            duration_minutes INTEGER NOT NULL,
            price            REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS PET (
            pet_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            pet_name  TEXT NOT NULL,
            species   TEXT NOT NULL,
            breed     TEXT,
            age       INTEGER,
            weight_kg REAL,
            FOREIGN KEY (client_id) REFERENCES CLIENT(client_id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS APPOINTMENT (
            appointment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id        INTEGER NOT NULL,
            pet_id           INTEGER NOT NULL,
            vet_id           INTEGER NOT NULL,
            service_id       INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            status           TEXT DEFAULT 'Pending',
            notes            TEXT,
            created_at       TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id)  REFERENCES CLIENT(client_id),
            FOREIGN KEY (pet_id)     REFERENCES PET(pet_id),
            FOREIGN KEY (vet_id)     REFERENCES VETERINARIAN(vet_id),
            FOREIGN KEY (service_id) REFERENCES SERVICE(service_id),
            UNIQUE (vet_id, appointment_date, appointment_time)
        );
        """)
       
        if conn.execute("SELECT COUNT(*) FROM CLIENT").fetchone()[0] == 0:
            conn.executescript("""
            INSERT INTO CLIENT (first_name,last_name,contact_number,email,address) VALUES
            ('Ricka','Arzola','09171234567','ricka@mail.com','Binan City'),
            ('Aina','Al-harmali','09391234567','aina@mail.com','Pasig City'),
            ('Cadey','Torralba','09281234567','cadey@mail.com','Makati City'),
            ('Josh','De Lejos','09451234567','Josh@mail.com','Taguig City'),
            ('Pedro','Lim','09561234567','pedro@mail.com','Manila City');

            INSERT INTO VETERINARIAN (first_name,last_name,specialization,contact_number) VALUES
            ('Kelly','Garcia','General Practice','09171110001'),
            ('Thea','Dela Cruz','Dental Care','09171110002'),
            ('Vash','Arzola','Surgery','09171110003'),
            ('Grachel','Bautista','Dermatology','09171110004'),
            ('Cyrille','Ruiz','Emergency & Critical Care','09171110005'),
            ('Eros','Agulto','Internal Medicine','09171110006'),
            ('Emman','Flores','Oncology','09171110007'),
            ('Sofia','Reyes','Ophthalmology','09171110008');
            ('Maria','Santos','Emergency & Critical Care','09171110009');

            INSERT INTO VET_SCHEDULE (vet_id,day_of_week,start_time,end_time) VALUES
            (1,'MON','08:00','17:00'),(1,'WED','08:00','17:00'),(1,'FRI','08:00','17:00'),
            (2,'TUE','09:00','18:00'),(2,'THU','09:00','18:00'),
            (3,'MON','10:00','16:00'),(3,'SAT','08:00','12:00'),
            (4,'WED','13:00','20:00'),(4,'FRI','13:00','20:00'),
            (5,'MON','08:00','20:00'),(5,'TUE','08:00','20:00'),(5,'WED','08:00','20:00'),
            (5,'THU','08:00','20:00'),(5,'FRI','08:00','20:00'),(5,'SAT','08:00','20:00'),(5,'SUN','08:00','20:00'),
            (6,'MON','08:00','17:00'),(6,'WED','08:00','17:00'),(6,'FRI','08:00','17:00'),
            (7,'TUE','09:00','17:00'),(7,'THU','09:00','17:00'),
            (8,'MON','10:00','18:00'),(8,'FRI','10:00','18:00');
            (9,'MON','20:00','08:00'),(9,'TUE','20:00','08:00'),(9,'WED','20:00','08:00'),
            (9,'THU','20:00','08:00'),(9,'FRI','20:00','08:00'),(9,'SAT','20:00','08:00'),(9,'SUN','20:00','08:00');

            INSERT INTO SERVICE (service_name,description,duration_minutes,price) VALUES
            ('General Checkup','Routine health examination',30,500.00),
            ('Vaccination','Standard vaccine administration',20,350.00),
            ('Dental Cleaning','Teeth cleaning and oral inspection',60,1500.00),
            ('Grooming','Full bath, trim, and styling',90,800.00),
            ('Deworming','Oral deworming treatment',15,250.00),
            ('Surgical Consult','Pre/post-operative consultation',45,1000.00),
            ('Emergency Care','Immediate treatment for life-threatening conditions',60,2000.00),
            ('Internal Medicine Consult','Diagnosis and treatment of complex internal diseases',45,1200.00),
            ('Oncology Consult','Cancer diagnosis and treatment planning',60,1500.00),
            ('Eye Examination','Comprehensive eye check and disease treatment',30,800.00);

            INSERT INTO PET (client_id,pet_name,species,breed,age,weight_kg) VALUES
            (1,'Doggo','Dog','Labrador',3,25.50),
            (1,'Buddy','Dog','Aspin',2,12.00),
            (2,'Whiskers','Cat','Persian',5,4.20),
            (3,'Rocky','Dog','Shih Tzu',1,5.80),
            (4,'Nemo','Fish','Goldfish',1,0.10),
            (5,'Tweety','Bird','Budgerigar',2,0.08);

            INSERT INTO APPOINTMENT (client_id,pet_id,vet_id,service_id,appointment_date,appointment_time,status) VALUES
            (1,1,1,1,'2024-06-03','09:00','Confirmed'),
            (2,3,2,3,'2024-06-04','10:00','Pending'),
            (3,4,1,2,'2024-06-05','11:00','Confirmed'),
            (1,2,3,6,'2024-06-08','10:00','Pending'),
            (4,5,1,1,'2024-06-10','09:00','Completed'),
            (5,6,4,4,'2024-06-12','14:00','Pending'),
            (2,3,2,5,'2024-06-14','10:00','Confirmed'),
            (3,4,1,4,'2024-06-17','13:00','Cancelled');
            """)

#DASHBOARD 
@app.route("/")
def dashboard():
    db = get_db()
    today = date.today().isoformat()
    stats = {
        "total":     db.execute("SELECT COUNT(*) FROM APPOINTMENT").fetchone()[0],
        "today":     db.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE appointment_date=?", (today,)).fetchone()[0],
        "pending":   db.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE status='Pending'").fetchone()[0],
        "confirmed": db.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE status='Confirmed'").fetchone()[0],
        "completed": db.execute("SELECT COUNT(*) FROM APPOINTMENT WHERE status='Completed'").fetchone()[0],
        "clients":   db.execute("SELECT COUNT(*) FROM CLIENT").fetchone()[0],
        "vets":      db.execute("SELECT COUNT(*) FROM VETERINARIAN WHERE is_active=1").fetchone()[0],
    }
    upcoming = db.execute("""
        SELECT a.appointment_id, a.appointment_date, a.appointment_time,
               c.first_name||' '||c.last_name AS client_name,
               p.pet_name, v.first_name||' '||v.last_name AS vet_name,
               s.service_name, a.status
        FROM APPOINTMENT a
        JOIN CLIENT c ON a.client_id=c.client_id
        JOIN PET p ON a.pet_id=p.pet_id
        JOIN VETERINARIAN v ON a.vet_id=v.vet_id
        JOIN SERVICE s ON a.service_id=s.service_id
        ORDER BY a.appointment_date DESC, a.appointment_time
        LIMIT 8
    """).fetchall()
    return render_template("dashboard.html", stats=stats, upcoming=upcoming, today=today)

@app.route("/appointments")
def appointments():
    db = get_db()
    status_filter = request.args.get("status", "")
    date_filter   = request.args.get("date", "")
    month_str     = request.args.get("month", date.today().strftime("%Y-%m"))

    from calendar import monthrange
    year, month = map(int, month_str.split("-"))
    days_in_month = monthrange(year, month)[1]

    appt_counts = {}
    rows = db.execute("""
        SELECT appointment_date, COUNT(*) as cnt
        FROM APPOINTMENT
        WHERE strftime('%Y-%m', appointment_date) = ?
        AND vet_id NOT IN (5, 9)
        GROUP BY appointment_date
    """, (month_str,)).fetchall()
    for r in rows:
        appt_counts[r["appointment_date"]] = r["cnt"]

    vet_schedules = db.execute("""
        SELECT vs.day_of_week, vs.vet_id, vs.start_time, vs.end_time
        FROM VET_SCHEDULE vs
        WHERE vs.vet_id NOT IN (5, 9)
    """).fetchall()

    def calc_slots(start, end):
        fmt = "%H:%M"
        s = datetime.strptime(start, fmt)
        e = datetime.strptime(end, fmt)
        mins = (e - s).seconds // 60
        working_mins = max(0, mins - 60)
        return max(0, working_mins // 60)

    vets_per_dow = {}
    for s in vet_schedules:
        dow = s["day_of_week"]
        slots = calc_slots(s["start_time"], s["end_time"])
        vets_per_dow[dow] = vets_per_dow.get(dow, 0) + slots

    cal_days = []
    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        dow = ["MON","TUE","WED","THU","FRI","SAT","SUN"][d.weekday()]
        date_str = d.isoformat()
        booked = appt_counts.get(date_str, 0)
        total_slots = vets_per_dow.get(dow, 0)
        emergency_only = dow in ["SAT","SUN"] and total_slots == 0
        if emergency_only:
            status = "emergency"
        elif total_slots == 0:
            status = "none"
        elif booked >= total_slots:
            status = "full"
        elif booked >= total_slots * 0.5:
            status = "filling"
        else:
            status = "available"
        cal_days.append({
            "day": day,
            "date": date_str,
            "booked": booked,
            "total": total_slots,
            "status": status,
            "dow": dow,
            "emergency_only": emergency_only
        })

    day_detail = None
    if date_filter:
        selected = date(int(date_filter[:4]), int(date_filter[5:7]), int(date_filter[8:10]))
        selected_dow = ["MON","TUE","WED","THU","FRI","SAT","SUN"][selected.weekday()]

        booked_slots = db.execute("""
            SELECT vet_id, appointment_time
            FROM APPOINTMENT
            WHERE appointment_date = ?
        """, (date_filter,)).fetchall()
        booked_by_vet = {}
        for b in booked_slots:
            booked_by_vet.setdefault(b["vet_id"], set()).add(b["appointment_time"])

        regular_vets = db.execute("""
            SELECT v.vet_id, v.first_name, v.last_name, v.specialization,
                   vs.start_time, vs.end_time
            FROM VETERINARIAN v
            JOIN VET_SCHEDULE vs ON v.vet_id = vs.vet_id
            WHERE vs.day_of_week = ?
            AND v.vet_id NOT IN (5, 9)
            AND v.is_active = 1
        """, (selected_dow,)).fetchall()

        emergency_vets = db.execute("""
            SELECT v.vet_id, v.first_name, v.last_name, v.specialization,
                   vs.start_time, vs.end_time
            FROM VETERINARIAN v
            JOIN VET_SCHEDULE vs ON v.vet_id = vs.vet_id
            WHERE vs.day_of_week = ?
            AND v.vet_id IN (5, 9)
            AND v.is_active = 1
        """, (selected_dow,)).fetchall()

        def get_time_slots(start, end):
            fmt = "%H:%M"
            s = datetime.strptime(start, fmt)
            e = datetime.strptime(end, fmt)
            slots = []
            current = s
            lunch_start = datetime.strptime("12:00", fmt)
            lunch_end = datetime.strptime("13:00", fmt)
            while current < e:
                if not (lunch_start <= current < lunch_end):
                    slots.append(current.strftime("%H:%M"))
                current = datetime.strptime(current.strftime("%H:%M"), fmt)
                from datetime import timedelta
                current += timedelta(hours=1)
            return slots

        vet_details = []
        for v in regular_vets:
            all_slots = get_time_slots(v["start_time"], v["end_time"])
            booked = booked_by_vet.get(v["vet_id"], set())
            slot_info = [{"time": t, "booked": t in booked} for t in all_slots]
            vet_details.append({
                "name": f"Dr. {v['first_name']} {v['last_name']}",
                "specialization": v["specialization"],
                "start": v["start_time"],
                "end": v["end_time"],
                "slots": slot_info,
                "available": sum(1 for s in slot_info if not s["booked"]),
                "total": len(slot_info)
            })

        emergency_details = []
        for v in emergency_vets:
            emergency_details.append({
                "name": f"Dr. {v['first_name']} {v['last_name']}",
                "specialization": v["specialization"],
                "start": v["start_time"],
                "end": v["end_time"],
            })

        day_detail = {
            "date": date_filter,
            "dow": selected_dow,
            "vets": vet_details,
            "emergency": emergency_details
        }

    q = """
        SELECT a.appointment_id, a.appointment_date, a.appointment_time,
               c.first_name||' '||c.last_name AS client_name,
               p.pet_name, p.species,
               v.first_name||' '||v.last_name AS vet_name,
               s.service_name, s.price, a.status, a.notes
        FROM APPOINTMENT a
        JOIN CLIENT c ON a.client_id=c.client_id
        JOIN PET p ON a.pet_id=p.pet_id
        JOIN VETERINARIAN v ON a.vet_id=v.vet_id
        JOIN SERVICE s ON a.service_id=s.service_id
        WHERE 1=1
    """
    params = []
    if status_filter:
        q += " AND a.status=?"; params.append(status_filter)
    if date_filter:
        q += " AND a.appointment_date=?"; params.append(date_filter)
    q += " ORDER BY a.appointment_date DESC, a.appointment_time"
    rows = db.execute(q, params).fetchall()

    return render_template("appointments.html", appointments=rows,
                           status_filter=status_filter, date_filter=date_filter,
                           cal_days=cal_days, month_str=month_str,
                           first_dow=date(year, month, 1).weekday(),
                           month_label=date(year, month, 1).strftime("%B %Y"),
                           day_detail=day_detail)

@app.route("/appointments/new", methods=["GET","POST"])
def new_appointment():
    db = get_db()
    if request.method == "POST":
        f = request.form
        try:
            db.execute("""
                INSERT INTO APPOINTMENT (client_id,pet_id,vet_id,service_id,
                    appointment_date,appointment_time,status,notes)
                VALUES (?,?,?,?,?,?,?,?)
            """, (f["client_id"], f["pet_id"], f["vet_id"], f["service_id"],
                  f["appointment_date"], f["appointment_time"],
                  f.get("status","Pending"), f.get("notes","")))
            db.commit()
            flash("Appointment booked successfully!", "success")
            return redirect(url_for("appointments"))
        except sqlite3.IntegrityError:
            flash("That time slot is already taken for this vet. Please choose another.", "error")
    clients  = db.execute("SELECT * FROM CLIENT ORDER BY last_name").fetchall()
    vets     = db.execute("SELECT * FROM VETERINARIAN WHERE is_active=1 ORDER BY last_name").fetchall()
    services = db.execute("SELECT * FROM SERVICE ORDER BY service_name").fetchall()
    return render_template("appointment_form.html", clients=clients,
                           vets=vets, services=services, appt=None)

@app.route("/appointments/<int:id>/edit", methods=["GET","POST"])
def edit_appointment(id):
    db = get_db()
    if request.method == "POST":
        f = request.form
        db.execute("""
            UPDATE APPOINTMENT SET client_id=?,pet_id=?,vet_id=?,service_id=?,
                appointment_date=?,appointment_time=?,status=?,notes=?
            WHERE appointment_id=?
        """, (f["client_id"], f["pet_id"], f["vet_id"], f["service_id"],
              f["appointment_date"], f["appointment_time"],
              f["status"], f.get("notes",""), id))
        db.commit()
        flash("Appointment updated.", "success")
        return redirect(url_for("appointments"))
    appt     = db.execute("SELECT * FROM APPOINTMENT WHERE appointment_id=?", (id,)).fetchone()
    clients  = db.execute("SELECT * FROM CLIENT ORDER BY last_name").fetchall()
    vets     = db.execute("SELECT * FROM VETERINARIAN WHERE is_active=1 ORDER BY last_name").fetchall()
    services = db.execute("SELECT * FROM SERVICE ORDER BY service_name").fetchall()
    pets     = db.execute("SELECT * FROM PET WHERE client_id=?", (appt["client_id"],)).fetchall()
    return render_template("appointment_form.html", clients=clients, vets=vets,
                           services=services, appt=appt, pets=pets)

@app.route("/appointments/<int:id>/status", methods=["POST"])
def update_status(id):
    status = request.form["status"]
    db = get_db()
    db.execute("UPDATE APPOINTMENT SET status=? WHERE appointment_id=?", (status, id))
    db.commit()
    flash(f"Status updated to {status}.", "success")
    return redirect(url_for("appointments"))

@app.route("/appointments/<int:id>/delete", methods=["POST"])
def delete_appointment(id):
    db = get_db()
    db.execute("DELETE FROM APPOINTMENT WHERE appointment_id=?", (id,))
    db.commit()
    flash("Appointment deleted.", "success")
    return redirect(url_for("appointments"))

#  CLIENTS 
@app.route("/clients")
def clients():
    db = get_db()
    rows = db.execute("""
        SELECT c.*, COUNT(p.pet_id) AS pet_count,
               COUNT(a.appointment_id) AS appt_count
        FROM CLIENT c
        LEFT JOIN PET p ON c.client_id=p.client_id
        LEFT JOIN APPOINTMENT a ON c.client_id=a.client_id
        GROUP BY c.client_id ORDER BY c.last_name
    """).fetchall()
    return render_template("clients.html", clients=rows)

@app.route("/clients/new", methods=["GET","POST"])
def new_client():
    if request.method == "POST":
        f = request.form
        db = get_db()
        try:
            db.execute("INSERT INTO CLIENT (first_name,last_name,contact_number,email,address) VALUES (?,?,?,?,?)",
                       (f["first_name"],f["last_name"],f["contact_number"],f["email"],f.get("address","")))
            db.commit()
            flash("Client added.", "success")
            return redirect(url_for("clients"))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
    return render_template("client_form.html", client=None)

@app.route("/clients/<int:id>/delete", methods=["POST"])
def delete_client(id):
    db = get_db()
    db.execute("DELETE FROM CLIENT WHERE client_id=?", (id,))
    db.commit()
    flash("Client deleted.", "success")
    return redirect(url_for("clients"))

@app.route("/clients/<int:id>/edit", methods=["GET","POST"])
def edit_client(id):
    db = get_db()
    if request.method == "POST":
        f = request.form
        db.execute("UPDATE CLIENT SET first_name=?,last_name=?,contact_number=?,email=?,address=? WHERE client_id=?",
                   (f["first_name"],f["last_name"],f["contact_number"],f["email"],f.get("address",""),id))
        db.commit()
        flash("Client updated.", "success")
        return redirect(url_for("clients"))
    client = db.execute("SELECT * FROM CLIENT WHERE client_id=?", (id,)).fetchone()
    return render_template("client_form.html", client=client)

# VETS 
@app.route("/vets")
def vets():
    db = get_db()
    rows = db.execute("""
        SELECT v.*, COUNT(a.appointment_id) AS appt_count
        FROM VETERINARIAN v
        LEFT JOIN APPOINTMENT a ON v.vet_id=a.vet_id
        GROUP BY v.vet_id ORDER BY v.last_name
    """).fetchall()
    schedules = db.execute("SELECT * FROM VET_SCHEDULE ORDER BY vet_id, day_of_week").fetchall()
    return render_template("vets.html", vets=rows, schedules=schedules)

# SERVICES
@app.route("/services")
def services():
    db = get_db()
    rows = db.execute("SELECT * FROM SERVICE ORDER BY service_name").fetchall()
    return render_template("services.html", services=rows)


@app.route("/api/pets/<int:client_id>")
def api_pets(client_id):
    db = get_db()
    pets = db.execute("SELECT pet_id, pet_name, species FROM PET WHERE client_id=?", (client_id,)).fetchall()
    return jsonify([dict(p) for p in pets])

@app.template_filter('prev_month')
def prev_month_filter(month_str):
    year, month = map(int, month_str.split("-"))
    month -= 1
    if month == 0:
        month = 12
        year -= 1
    return f"{year}-{month:02d}"

@app.template_filter('next_month')
def next_month_filter(month_str):
    year, month = map(int, month_str.split("-"))
    month += 1
    if month == 13:
        month = 1
        year += 1
    return f"{year}-{month:02d}"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
