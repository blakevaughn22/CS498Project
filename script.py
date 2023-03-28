from flask import Flask, render_template, request

app = Flask(__name__)

# sample menu items with prices
menu = {
    "Latte": 3.50,
    "Cappuccino": 3.75,
    "Espresso": 2.50,
    "Mocha": 4.00,
    "Americano": 2.75
}

@app.route("/")
def home():
    return render_template("index.html", menu=menu)

@app.route("/order", methods=["POST"])
def order():
    # get user's order from the form
    order = request.form.getlist("item")
    total = 0
    items = []

    # calculate the total price of the order
    for item in order:
        price = menu.get(item)
        total += price
        items.append({"name": item, "price": price})

    return render_template("order.html", items=items, total=total)

if __name__ == "__main__":
    app.run(debug=True)