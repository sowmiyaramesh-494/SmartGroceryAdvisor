from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "smart_grocery_secret"
# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@123",
    database="smart_grocery_advisor"
)

cursor = db.cursor()

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# About Page
@app.route("/about")
def about():
    return render_template("about.html")

# Contact Page
@app.route("/contact")
def contact():
    return render_template("contact.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        sql = "SELECT * FROM users WHERE email=%s AND password=%s"

        cursor.execute(sql, (email, password))

        user = cursor.fetchone()

        if user:

        session["user"] = email

         return redirect("/admin")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect("/login")

    return render_template("admin.html")
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]

        sql = """
        INSERT INTO users(full_name,email,password,phone)
        VALUES(%s,%s,%s,%s)
        """

        values = (full_name, email, password, phone)

        cursor.execute(sql, values)
        db.commit()

        return redirect("/login")

    return render_template("register.html")
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")
@app.route("/add_store", methods=["GET", "POST"])
def add_store():

    if request.method == "POST":

        store_name = request.form["store_name"]
        location = request.form["location"]
        contact = request.form["contact"]

        sql = """
        INSERT INTO stores(store_name,location,contact)
        VALUES(%s,%s,%s)
        """

        values = (store_name, location, contact)

        cursor.execute(sql, values)
        db.commit()

        return redirect("/admin")

    return render_template("add_store.html")

@app.route("/add_product", methods=["GET", "POST"])
def add_product():

    if request.method == "POST":

        product_name = request.form["product_name"]
        category = request.form["category"]
        brand = request.form["brand"]

        sql = """
        INSERT INTO products(product_name,category,brand)
        VALUES(%s,%s,%s)
        """

        values = (product_name, category, brand)

        cursor.execute(sql, values)
        db.commit()

        return redirect("/admin")

    return render_template("add_product.html")
@app.route("/add_price", methods=["GET", "POST"])
def add_price():

    if request.method == "POST":

        product_id = request.form["product_id"]
        store_id = request.form["store_id"]
        price = request.form["price"]

        sql = """
        INSERT INTO product_prices(product_id,store_id,price)
        VALUES(%s,%s,%s)
        """

        cursor.execute(sql, (product_id, store_id, price))
        db.commit()

        return redirect("/admin")

    return render_template("add_price.html")
@app.route("/quality", methods=["GET", "POST"])
def quality():

    if request.method == "POST":

        product_id = request.form["product_id"]
        quality_score = request.form["quality_score"]
        remarks = request.form["remarks"]

        sql = """
        INSERT INTO quality_ratings(product_id, quality_score, remarks)
        VALUES(%s, %s, %s)
        """

        cursor.execute(sql, (product_id, quality_score, remarks))
        db.commit()

        return redirect("/admin")

    return render_template("quality.html")
@app.route("/compare", methods=["GET", "POST"])
def compare():

    cursor.execute("SELECT product_id, product_name FROM products")
    products = cursor.fetchall()

    prices = []
    lowest_price = None
    recommended_store = ""
    product_name = ""
    selected_product_id = None

    if request.method == "POST":

        product_id = request.form["product_id"]
        selected_product_id = int(product_id)

        cursor.execute(
            "SELECT product_name FROM products WHERE product_id=%s",
            (product_id,)
        )

        product_name = cursor.fetchone()[0]

        sql = """
        SELECT
            stores.store_name,
            product_prices.price,
            quality_ratings.quality_score

        FROM product_prices

        JOIN stores
            ON product_prices.store_id = stores.store_id

        JOIN quality_ratings
            ON product_prices.product_id = quality_ratings.product_id

        WHERE product_prices.product_id=%s

        ORDER BY product_prices.price ASC
        """

        cursor.execute(sql, (product_id,))
        prices = cursor.fetchall()

        if prices:
            lowest_price = prices[0][1]
            recommended_store = prices[0][0]

    return render_template(
        "compare.html",
        products=products,
        prices=prices,
        lowest_price=lowest_price,
        recommended_store=recommended_store,
        product_name=product_name,
        selected_product_id=selected_product_id
    )

if __name__ == "__main__":
    app.run(debug=True)