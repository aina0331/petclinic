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
            ('Juan','Dela Cruz','09171234567','juan@mail.com','Quezon City'),
            ('Maria','Reyes','09281234567','maria@mail.com','Makati City'),
            ('Carlos','Santos','09391234567','carlo@mail.com','Pasig City'),
            ('Ana','Garcia','09451234567','ana@mail.com','Taguig City'),
            ('Pedro','Lim','09561234567','pedro@mail.com','Manila City');

            INSERT INTO VETERINARIAN (first_name,last_name,specialization,contact_number) VALUES
            ('Ricardo','Santos','General Practice','09171110001'),
            ('Elena','Cruz','Dental Care','09171110002'),
            ('Marco','Bautista','Surgery','09171110003'),
            ('Lisa','Torres','Dermatology','09171110004'),
            ('Jose','Ramos','Emergency & Critical Care','09171110005'),
            ('Anna','Villanueva','Internal Medicine','09171110006'),
            ('Miguel','Flores','Oncology','09171110007'),
            ('Sofia','Reyes','Ophthalmology','09171110008'),
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

# APPOINTMENTS 
@app.route("/appointments")
def appointments():
    db = get_db()
    status_filter = request.args.get("status", "")
    date_filter   = request.args.get("date", "")
    month_str     = request.args.get("month", date.today().strftime("%Y-%m"))

    # Calendar data
    from calendar import monthrange
    year, month = map(int, month_str.split("-"))
    days_in_month = monthrange(year, month)[1]

    # Count appointments per day (excluding emergency vets 5 and 9)
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

    # Count how many regular vets are scheduled each day of week
    day_map = {"MON":0,"TUE":1,"WED":2,"THU":3,"FRI":4,"SAT":5,"SUN":6}
    import calendar
    vet_schedules = db.execute("""
        SELECT vs.day_of_week, vs.vet_id, vs.start_time, vs.end_time
        FROM VET_SCHEDULE vs
        WHERE vs.vet_id NOT IN (5, 9)
    """).fetchall()

    def calc_slots(start, end):
        from datetime import datetime
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

    for dow in ["SAT","SUN"]:
        if vets_per_dow.get(dow, 0) == 0:
            vets_per_dow[dow] = 1

    # Build calendar days
    cal_days = []
    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        dow = ["MON","TUE","WED","THU","FRI","SAT","SUN"][d.weekday()]
        date_str = d.isoformat()
        booked = appt_counts.get(date_str, 0)
        total_slots = vets_per_dow.get(dow, 0)
        if total_slots == 0:
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
            "dow": dow
        })

    # First day of month offset for calendar grid
    first_dow = date(year, month, 1).weekday()  # 0=Mon

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
                           first_dow=first_dow,
                           month_label=date(year, month, 1).strftime("%B %Y"))

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
    SELECT c.*,
           (SELECT COUNT(*) FROM PET p WHERE p.client_id = c.client_id) AS pet_count,
           (SELECT COUNT(*) FROM APPOINTMENT a WHERE a.client_id = c.client_id) AS appt_count
    FROM CLIENT c
    ORDER BY c.last_name
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
            new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            flash("Client added! Now add their pet.", "success")
            return redirect(url_for("new_pet", client_id=new_id))
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

# PETS
@app.route("/pets")
def pets():
    db = get_db()
    search        = request.args.get("search", "").strip()
    species_filter = request.args.get("species", "").strip()
    client_id_filter = request.args.get("client_id", "").strip()

    q = """
        SELECT p.*,
               c.first_name||' '||c.last_name AS owner_name,
               c.email, c.client_id,
               COUNT(a.appointment_id) AS appt_count
        FROM PET p
        JOIN CLIENT c ON p.client_id = c.client_id
        LEFT JOIN APPOINTMENT a ON p.pet_id = a.pet_id
        WHERE 1=1
    """
    params = []
    if search:
        q += " AND p.pet_name LIKE ?"; params.append(f"%{search}%")
    if species_filter:
        q += " AND p.species = ?"; params.append(species_filter)
    if client_id_filter:
        q += " AND p.client_id = ?"; params.append(client_id_filter)
    q += " GROUP BY p.pet_id ORDER BY p.pet_name"
    rows = db.execute(q, params).fetchall()

    species_list = [r[0] for r in db.execute(
        "SELECT DISTINCT species FROM PET ORDER BY species").fetchall()]

    # If filtering by client, pass owner name for breadcrumb
    owner = None
    if client_id_filter:
        owner = db.execute(
            "SELECT first_name||' '||last_name AS name FROM CLIENT WHERE client_id=?",
            (client_id_filter,)).fetchone()

    return render_template("pets.html", pets=rows,
                           search=search, species_filter=species_filter,
                           species_list=species_list, owner=owner,
                           client_id_filter=client_id_filter)

@app.route("/pets/new", methods=["GET", "POST"])
def new_pet():
    db = get_db()
    preselect_client = request.args.get("client_id", type=int)
    if request.method == "POST":
        f = request.form
        db.execute(
            "INSERT INTO PET (client_id,pet_name,species,breed,age,weight_kg) VALUES (?,?,?,?,?,?)",
            (f["client_id"], f["pet_name"], f["species"],
             f.get("breed") or None,
             f.get("age") or None,
             f.get("weight_kg") or None))
        db.commit()
        flash("Pet added successfully!", "success")
        return redirect(url_for("pets"))
    clients = db.execute("SELECT * FROM CLIENT ORDER BY last_name").fetchall()
    return render_template("pet_form.html", pet=None, clients=clients,
                           preselect_client=preselect_client)

@app.route("/pets/<int:id>/edit", methods=["GET", "POST"])
def edit_pet(id):
    db = get_db()
    if request.method == "POST":
        f = request.form
        db.execute(
            """UPDATE PET SET client_id=?,pet_name=?,species=?,breed=?,age=?,weight_kg=?
               WHERE pet_id=?""",
            (f["client_id"], f["pet_name"], f["species"],
             f.get("breed") or None,
             f.get("age") or None,
             f.get("weight_kg") or None, id))
        db.commit()
        flash("Pet updated.", "success")
        return redirect(url_for("pets"))
    pet     = db.execute("SELECT * FROM PET WHERE pet_id=?", (id,)).fetchone()
    clients = db.execute("SELECT * FROM CLIENT ORDER BY last_name").fetchall()
    return render_template("pet_form.html", pet=pet, clients=clients,
                           preselect_client=None)

@app.route("/pets/<int:id>/delete", methods=["POST"])
def delete_pet(id):
    db = get_db()
    db.execute("DELETE FROM PET WHERE pet_id=?", (id,))
    db.commit()
    flash("Pet deleted.", "success")
    return redirect(url_for("pets"))

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

@app.route("/api/vet/<int:vet_id>/services")
def api_vet_services(vet_id):
    db = get_db()
    vet = db.execute("SELECT specialization FROM VETERINARIAN WHERE vet_id=?", (vet_id,)).fetchone()
    if not vet:
        return jsonify([])
    
    spec = vet["specialization"]
    mapping = {
        "General Practice":         ["General Checkup", "Vaccination", "Deworming"],
        "Dental Care":              ["Dental Cleaning"],
        "Surgery":                  ["Surgical Consult"],
        "Dermatology":              ["General Checkup"],
        "Emergency & Critical Care":["Emergency Care"],
        "Internal Medicine":        ["Internal Medicine Consult"],
        "Oncology":                 ["Oncology Consult"],
        "Ophthalmology":            ["Eye Examination"],
    }
    allowed = mapping.get(spec, [])
    services = db.execute(
        "SELECT * FROM SERVICE WHERE service_name IN ({})".format(
            ",".join("?" * len(allowed))), allowed).fetchall()
    return jsonify([dict(s) for s in services])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)