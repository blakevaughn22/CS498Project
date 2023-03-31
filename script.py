from flask import Flask, render_template, request, redirect, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'my-secret-key'

# SQLite Configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connect to the customer database
app.config['SQLALCHEMY_BINDS'] = {
    'customers': 'sqlite:///customers.db',
    'menu': 'sqlite:///menu_database.db'
}

db = SQLAlchemy(app)

class MenuItem(db.Model):
    __bind_key__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    __bind_key__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    order_items = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    done = db.Column(db.Boolean, default=False)

# Create all tables
db.create_all(bind='customers')
db.create_all(bind='menu')

@app.route("/")
def home():
    # Fetch menu items from the database
    menu_items = MenuItem.query.all()
    menu = {item.name: item.price for item in menu_items}
    return render_template("index.html", menu=menu)

@app.route("/order", methods=["POST"])
def order():
    # Get user's order from the form
    order = request.form.getlist("item")
    customer_name = request.form["customer_name"]
    total = 0
    items = []

    # Calculate the total price of the order
    for item in order:
        menu_item = MenuItem.query.filter_by(name=item).first()
        total += menu_item.price
        items.append({"name": item, "price": menu_item.price})

    # Save the order to the customers.db database
    order_items = ", ".join([item["name"] for item in items])
    new_order = Order(customer_name=customer_name, order_items=order_items, timestamp=datetime.now())
    db.session.add(new_order)
    db.session.commit()

    return render_template("order.html", items=items, total=total)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'password':
        session['logged_in'] = True
        return redirect('/dashboard')
    else:
        flash('Invalid login. Please try again.', 'error')
        return redirect('/login')

@app.route("/dashboard")
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')

    orders = Order.query.filter_by(done=False).all()
    menu_items = MenuItem.query.all()

    order_list = ''
    for order in orders:
        items = order.order_items.split(', ')

        # Calculate total cost for each order
        total_cost = 0
        for item in items:
            menu_item = next((x for x in menu_items if x.name == item), None)
            if menu_item is not None:
                total_cost += menu_item.price

        order_list += '<li>{} - {} - Total Cost: ${:.2f} - Timestamp: {} <a href="/mark_done/{}">Mark as done</a></li>'.format(
            order.customer_name, order.order_items, total_cost, order.timestamp, order.id)

    response = make_response('<h1>Order List</h1><ul>{}</ul><br><a href="/logout">Logout</a>'.format(order_list))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

@app.route("/mark_done/<int:order_id>")
def mark_done(order_id):
    if not session.get('logged_in'):
        return redirect('/login')

    order = Order.query.get(order_id)
    if order:
        order.done = True
        db.session.commit()
        flash('Order marked as done.', 'success')
    else:
        flash('Order not found.', 'error')

    return redirect('/dashboard')

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
