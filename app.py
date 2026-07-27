from flask import Flask, render_template, request, redirect, url_for
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from config import Config
from models import db, User, Customer, Outreach

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# -----------------------
# Flask Login
# -----------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


# -----------------------
# Login
# -----------------------
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:

            login_user(user)

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# -----------------------
# Dashboard
# -----------------------
@app.route("/dashboard")
@login_required
def dashboard():

    customer_count = Customer.query.count()

    outreach_count = Outreach.query.count()

    draft_count = Outreach.query.filter_by(
        status="Draft"
    ).count()

    approved_count = Outreach.query.filter_by(
        status="Approved"
    ).count()

    sent_count = Outreach.query.filter_by(
        status="Sent"
    ).count()

    recent_outreach = (
        Outreach.query
        .order_by(Outreach.id.desc())
        .limit(5)
        .all()
    )

    recent_customers = (
        Customer.query
        .order_by(Customer.id.desc())
        .limit(5)
        .all()
    )

    upcoming_followups = (
        Outreach.query
        .filter(
            Outreach.follow_up.isnot(None),
            Outreach.follow_up != ""
        )
        .order_by(Outreach.follow_up.asc())
        .limit(5)
        .all()
    )

# -----------------------
# Activity Timeline
# -----------------------
    activities = []

    # Recent Customers
    for customer in recent_customers:
        activities.append({
            "icon": "person-plus",
            "title": "New Customer",
            "description": f"{customer.first_name} {customer.last_name}",
            "time": customer.last_contact if customer.last_contact else "Recently"
        })

# Recent Outreach
    for outreach in recent_outreach:
        activities.append({
            "icon": "chat-dots",
            "title": "Outreach Created",
            "description": f"{outreach.customer.first_name} {outreach.customer.last_name}",
            "time": outreach.follow_up if outreach.follow_up else "Pending"
        })

# -----------------------
# Notifications
# -----------------------
    notifications = []

    if draft_count > 0:
        notifications.append(
            f"{draft_count} draft message(s) awaiting approval."
        )

    if len(upcoming_followups) > 0:
        notifications.append(
            f"{len(upcoming_followups)} follow-up(s) scheduled."
        )

    if customer_count == 0:
        notifications.append(
            "No customers have been added yet."
        )

    if outreach_count == 0:
        notifications.append(
            "No outreach campaigns have been created."
        )
    
    activities = []

# Customer Activities
    for customer in recent_customers:
        activities.append({
        "icon": "person-plus",
        "title": "New Customer",
        "description": f"{customer.first_name} {customer.last_name}",
        "time": customer.last_contact if customer.last_contact else "Recently"
    })

# Outreach Activities
    for outreach in recent_outreach:
         activities.append({
        "icon": "chat-dots",
        "title": "Outreach Created",
        "description": outreach.customer.first_name + " " + outreach.customer.last_name,
        "time": outreach.follow_up if outreach.follow_up else "Pending"
    })

    upcoming_followups = (
        Outreach.query
        .filter(
            Outreach.follow_up.isnot(None),
            Outreach.follow_up != ""
        )
        .order_by(Outreach.follow_up.asc())
        .limit(5)
        .all()
    )

# -----------------------
# Notifications
 # -----------------------

    notifications = []

    if draft_count > 0:
        notifications.append(
            f"{draft_count} draft message(s) awaiting approval."
        )

    if len(upcoming_followups) > 0:
        notifications.append(
            f"{len(upcoming_followups)} follow-up(s) scheduled."
        )

    if customer_count == 0:
        notifications.append(
            "No customers have been added yet."
        )

    if outreach_count == 0:
        notifications.append(
            "No outreach campaigns have been created."
        )

    return render_template(
    "dashboard.html",
        customer_count=customer_count,
        outreach_count=outreach_count,
        draft_count=draft_count,
        approved_count=approved_count,
        sent_count=sent_count,
        recent_outreach=recent_outreach,
        recent_customers=recent_customers,
        upcoming_followups=upcoming_followups,
        notifications=notifications,
        activities=activities
)


# -----------------------
# Customer List
# -----------------------
@app.route("/customers")
@login_required
def customers():

    search = request.args.get("search", "")

    if search:
        customers = Customer.query.filter(
            Customer.first_name.contains(search) |
            Customer.last_name.contains(search) |
            Customer.company.contains(search)
        ).all()
    else:
        customers = Customer.query.all()

    return render_template(
        "customers.html",
        customers=customers
    )


# -----------------------
# Customer Profile
# -----------------------
@app.route("/customers/<int:id>")
@login_required
def customer_profile(id):

    customer = Customer.query.get_or_404(id)

    return render_template(
        "customer_profile.html",
        customer=customer
    )


# -----------------------
# Add Customer
# -----------------------
@app.route("/customers/add", methods=["GET", "POST"])
@login_required
def add_customer():

    if request.method == "POST":

        customer = Customer(
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            company=request.form["company"],
            email=request.form["email"],
            phone=request.form["phone"],
            segment=request.form["segment"],
            status=request.form["status"],
            last_contact=request.form["last_contact"],
            notes=request.form["notes"]
        )

        db.session.add(customer)
        db.session.commit()

        return redirect(url_for("customers"))

    return render_template("add_customer.html")
# -----------------------
# Edit Customer
# -----------------------
@app.route("/customers/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_customer(id):

    customer = Customer.query.get_or_404(id)

    if request.method == "POST":

        customer.first_name = request.form["first_name"]
        customer.last_name = request.form["last_name"]
        customer.company = request.form["company"]
        customer.email = request.form["email"]
        customer.phone = request.form["phone"]
        customer.segment = request.form["segment"]
        customer.status = request.form["status"]
        customer.last_contact = request.form["last_contact"]
        customer.notes = request.form["notes"]

        db.session.commit()

        return redirect(url_for("customers"))

    return render_template(
        "edit_customer.html",
        customer=customer
    )


# -----------------------
# Delete Customer
# -----------------------
@app.route("/customers/delete/<int:id>")
@login_required
def delete_customer(id):

    customer = Customer.query.get_or_404(id)

    db.session.delete(customer)
    db.session.commit()

    return redirect(url_for("customers"))


# -----------------------
# Outreach Management
# -----------------------
@app.route("/outreach")
@login_required
def outreach():

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = Outreach.query

    if search:

        query = query.join(Customer).filter(

            (Customer.first_name.ilike(f"%{search}%")) |
            (Customer.last_name.ilike(f"%{search}%")) |
            (Outreach.message.ilike(f"%{search}%")) |
            (Outreach.channel.ilike(f"%{search}%"))

        )

    if status:

        query = query.filter(Outreach.status == status)

    records = query.order_by(Outreach.id.desc()).all()

    return render_template(
        "outreach.html",
        records=records
    )


# -----------------------
# Add Outreach
# -----------------------
@app.route("/outreach/add", methods=["GET", "POST"])
@login_required
def add_outreach():

    customers = Customer.query.all()

    if request.method == "POST":

        outreach = Outreach(
            customer_id=request.form["customer_id"],
            channel=request.form["channel"],
            message=request.form["message"],
            status=request.form["status"],
            follow_up=request.form["follow_up"],
            response=""
        )

        db.session.add(outreach)
        db.session.commit()

        return redirect(url_for("outreach"))

    return render_template(
        "add_outreach.html",
        customers=customers
    )


# -----------------------
# View Outreach
# -----------------------
@app.route("/outreach/view/<int:id>")
@login_required
def view_outreach(id):

    record = Outreach.query.get_or_404(id)

    return render_template(
        "view_outreach.html",
        record=record
    )


# -----------------------
# Edit Outreach
# -----------------------
@app.route("/outreach/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_outreach(id):

    record = Outreach.query.get_or_404(id)

    customers = Customer.query.all()

    if request.method == "POST":

        record.customer_id = request.form["customer_id"]
        record.channel = request.form["channel"]
        record.message = request.form["message"]
        record.status = request.form["status"]
        record.follow_up = request.form["follow_up"]

        db.session.commit()

        return redirect(url_for("outreach"))

    return render_template(
        "edit_outreach.html",
        record=record,
        customers=customers
    )


# -----------------------
# Delete Outreach
# -----------------------
@app.route("/outreach/delete/<int:id>")
@login_required
def delete_outreach(id):

    record = Outreach.query.get_or_404(id)

    db.session.delete(record)
    db.session.commit()

    return redirect(url_for("outreach"))

@app.route("/customers/segment/<int:id>")
@login_required
def segment_customer(id):

    customer = Customer.query.get_or_404(id)

    # Simple AI rules
    if customer.status == "Active":
        customer.segment = "🟢 Active"

    elif customer.status == "Inactive":
        customer.segment = "🔴 Dormant"

    elif customer.company and "Construction" in customer.company:
        customer.segment = "🔵 VIP"

    else:
        customer.segment = "🟡 Follow-up Needed"

    db.session.commit()

    return redirect(url_for("customer_profile", id=id))

# -----------------------
# Reports
# -----------------------
@app.route("/reports")
@login_required
def reports():

    customer_count = Customer.query.count()
    outreach_count = Outreach.query.count()

    draft_count = Outreach.query.filter_by(status="Draft").count()
    approved_count = Outreach.query.filter_by(status="Approved").count()
    sent_count = Outreach.query.filter_by(status="Sent").count()

    recent_outreach = (
        Outreach.query
        .order_by(Outreach.id.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "reports.html",
        customer_count=customer_count,
        outreach_count=outreach_count,
        draft_count=draft_count,
        approved_count=approved_count,
        sent_count=sent_count,
        recent_outreach=recent_outreach
    )


# -----------------------
# Settings
# -----------------------
@app.route("/settings")
@login_required
def settings():

    return render_template("settings.html")


# -----------------------
# Register Admin
# -----------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=request.form["password"]
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# -----------------------
# Logout
# -----------------------
@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


# -----------------------
# AI Message Generator
# -----------------------
@app.route("/generate-message/<int:id>")
@login_required
def generate_message(id):

    customer = Customer.query.get_or_404(id)

    message = f"""Hello {customer.first_name},

We hope you're doing well!

Thank you for being a valued customer of {customer.company}.

We wanted to reach out and see if there's anything we can help you with.
If you have any questions or would like to learn about our latest services,
we're happy to assist.

Looking forward to hearing from you.

Best regards,

CustomerPulse AI Team
"""

    return {
        "message": message
    }


# -----------------------
# Run Application
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)