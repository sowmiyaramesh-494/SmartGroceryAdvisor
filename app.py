from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "smartgroceryadvisor"
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

    if "user" in session:
        return redirect("/admin")

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

    return render_template("login.html")
@app.route("/admin")
def admin():


    if "user" not in session:
        return redirect("/login")

    cursor.execute("SELECT COUNT(*) FROM stores")
    total_stores = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM product_prices")
    total_prices = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM quality_ratings")
    total_quality = cursor.fetchone()[0]

    return render_template(
        "admin.html",
        total_stores=total_stores,
        total_products=total_products,
        total_prices=total_prices,
        total_quality=total_quality
    )
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
    if "user" not in session:
        return redirect("/login")

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

        flash("Store added successfully!", "success")

        return redirect("/admin")   

    return render_template("add_store.html")
@app.route("/view_stores")
def view_stores():

    if "user" not in session:
        return redirect("/login")

    search = request.args.get("search", "")

    if search:

        sql = """
        SELECT * FROM stores
        WHERE store_name LIKE %s
        OR location LIKE %s
        OR contact LIKE %s
        """

        value = "%" + search + "%"

        cursor.execute(sql, (value, value, value))

    else:

        cursor.execute("SELECT * FROM stores")

    stores = cursor.fetchall()

    return render_template(
        "view_stores.html",
        stores=stores,
        search=search
    )
@app.route("/delete_store/<int:store_id>")
def delete_store(store_id):

    if "user" not in session:
        return redirect("/login")

    cursor.execute(
        "DELETE FROM stores WHERE store_id=%s",
        (store_id,)
    )

    db.commit()

    flash("Store deleted successfully!", "success")

    return redirect("/view_stores")
@app.route("/edit_store/<int:store_id>", methods=["GET", "POST"])
def edit_store(store_id):

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        store_name = request.form["store_name"]
        location = request.form["location"]
        contact = request.form["contact"]

        sql = """
        UPDATE stores
        SET store_name=%s,
            location=%s,
            contact=%s
        WHERE store_id=%s
        """

        cursor.execute(sql, (store_name, location, contact, store_id))
        db.commit()

        flash("Store updated successfully!", "success")

        return redirect("/view_stores")

    cursor.execute(
        "SELECT * FROM stores WHERE store_id=%s",
        (store_id,)
    )

    store = cursor.fetchone()

    return render_template("edit_store.html", store=store)
@app.route("/view_products")
def view_products():

    if "user" not in session:
        return redirect("/login")

    search = request.args.get("search", "")

    if search:

        sql = """
        SELECT * FROM products
        WHERE product_name LIKE %s
        OR category LIKE %s
        OR brand LIKE %s
        """

        value = "%" + search + "%"

        cursor.execute(sql, (value, value, value))

    else:

        cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    return render_template(
        "view_products.html",
        products=products,
        search=search
    )

@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        product_name = request.form["product_name"]
        category = request.form["category"]
        brand = request.form["brand"]

        sql = """
        UPDATE products
        SET
            product_name=%s,
            category=%s,
            brand=%s
        WHERE product_id=%s
        """

        cursor.execute(sql, (product_name, category, brand, product_id))
        db.commit()

        flash("Product updated successfully!", "success")

        return redirect("/view_products")

    cursor.execute(
        "SELECT * FROM products WHERE product_id=%s",
        (product_id,)
    )

    product = cursor.fetchone()

    return render_template(
        "edit_product.html",
        product=product
    )
@app.route("/delete_product/<int:id>")
def delete_product(id):

    if "user" not in session:
        return redirect("/login")

    # Delete related prices
    cursor.execute(
        "DELETE FROM product_prices WHERE product_id=%s",
        (id,)
    )

    # Delete related quality ratings
    cursor.execute(
        "DELETE FROM quality_ratings WHERE product_id=%s",
        (id,)
    )

    # Delete the product
    cursor.execute(
        "DELETE FROM products WHERE product_id=%s",
        (id,)
    )

    db.commit()

    flash("Product deleted successfully!", "success")

    return redirect("/view_products")
@app.route("/view_prices")
def view_prices():

    if "user" not in session:
        return redirect("/login")

    search = request.args.get("search", "")

    if search:

        sql = """
        SELECT
            products.product_name,
            stores.store_name,
            product_prices.price,
            product_prices.price_id
        FROM product_prices
        JOIN products
            ON product_prices.product_id = products.product_id
        JOIN stores
            ON product_prices.store_id = stores.store_id
        WHERE products.product_name LIKE %s
           OR stores.store_name LIKE %s
           OR product_prices.price LIKE %s
        ORDER BY products.product_name
        """

        value = "%" + search + "%"

        cursor.execute(sql, (value, value, value))

    else:

        sql = """
        SELECT
            products.product_name,
            stores.store_name,
            product_prices.price,
            product_prices.price_id
        FROM product_prices
        JOIN products
            ON product_prices.product_id = products.product_id
        JOIN stores
            ON product_prices.store_id = stores.store_id
        ORDER BY products.product_name
        """

        cursor.execute(sql)

    prices = cursor.fetchall()

    return render_template(
        "view_prices.html",
        prices=prices,
        search=search
    )
@app.route("/edit_price/<int:id>", methods=["GET", "POST"])
def edit_price(id):

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        price = request.form["price"]

        cursor.execute(
            "UPDATE product_prices SET price=%s WHERE price_id=%s",
            (price, id)
        )

        db.commit()

        flash("Price updated successfully!", "success")

        return redirect("/view_prices")

    cursor.execute("""
        SELECT
            product_prices.price_id,
            products.product_name,
            stores.store_name,
            product_prices.price
        FROM product_prices
        JOIN products
            ON product_prices.product_id = products.product_id
        JOIN stores
            ON product_prices.store_id = stores.store_id
        WHERE product_prices.price_id=%s
    """, (id,))

    price = cursor.fetchone()

    return render_template("edit_price.html", price=price)
@app.route("/delete_price/<int:id>")
def delete_price(id):

    if "user" not in session:
        return redirect("/login")

    cursor.execute(
        "DELETE FROM product_prices WHERE price_id=%s",
        (id,)
    )

    db.commit()

    flash("Price deleted successfully!", "success")

    return redirect("/view_prices")
@app.route("/view_quality")
def view_quality():

    if "user" not in session:
        return redirect("/login")

    search = request.args.get("search", "")

    if search:

        sql = """
        SELECT
            products.product_name,
            quality_ratings.quality_score,
            quality_ratings.remarks,
            quality_ratings.rating_id
        FROM quality_ratings
        JOIN products
        ON quality_ratings.product_id = products.product_id
        WHERE products.product_name LIKE %s
           OR quality_ratings.remarks LIKE %s
        ORDER BY products.product_name
        """

        value = "%" + search + "%"

        cursor.execute(sql, (value, value))

    else:

        sql = """
        SELECT
            products.product_name,
            quality_ratings.quality_score,
            quality_ratings.remarks,
            quality_ratings.rating_id
        FROM quality_ratings
        JOIN products
        ON quality_ratings.product_id = products.product_id
        ORDER BY products.product_name
        """

        cursor.execute(sql)

    quality = cursor.fetchall()

    return render_template(
        "view_quality.html",
        quality=quality,
        search=search
    )
@app.route("/edit_quality/<int:id>", methods=["GET", "POST"])
def edit_quality(id):

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        quality_score = request.form["quality_score"]
        remarks = request.form["remarks"]

        cursor.execute(
            """
            UPDATE quality_ratings
            SET quality_score=%s,
                remarks=%s
            WHERE rating_id=%s
            """,
            (quality_score, remarks, id)
        )

        db.commit()

        flash("Quality rating updated successfully!", "success")

        return redirect("/view_quality")

    cursor.execute(
        """
        SELECT
            rating_id,
            product_id,
            quality_score,
            remarks
        FROM quality_ratings
        WHERE rating_id=%s
        """,
        (id,)
    )

    quality = cursor.fetchone()

    return render_template(
        "edit_quality.html",
        quality=quality
    )
@app.route("/delete_quality/<int:id>")
def delete_quality(id):

    if "user" not in session:
        return redirect("/login")

    cursor.execute(
        "DELETE FROM quality_ratings WHERE rating_id=%s",
        (id,)
    )

    db.commit()

    flash("Quality rating deleted successfully!", "success")

    return redirect("/view_quality")
@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if "user" not in session:
        return redirect("/login")

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

        flash("Product added successfully!", "success")

        return redirect("/admin")
    return render_template("add_product.html")
@app.route("/add_price", methods=["GET", "POST"])
def add_price():

    if "user" not in session:
        return redirect("/login")

    # Fetch products
    cursor.execute("SELECT product_id, product_name FROM products")
    products = cursor.fetchall()

    # Fetch stores
    cursor.execute("SELECT store_id, store_name FROM stores")
    stores = cursor.fetchall()

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

        flash("Price added successfully!", "success")

        return redirect("/admin")

    return render_template(
        "add_price.html",
        products=products,
        stores=stores
    )
@app.route("/quality", methods=["GET", "POST"])
def quality():

    if "user" not in session:
        return redirect("/login")

    # Fetch all products
    cursor.execute("SELECT product_id, product_name FROM products")
    products = cursor.fetchall()

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

        flash("Quality rating added successfully!", "success")

        return redirect("/admin")
    return render_template(
        "quality.html",
        products=products
    )
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