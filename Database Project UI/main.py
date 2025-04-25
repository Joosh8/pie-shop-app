from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from waitress import serve

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pie_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'replace-with-your-secret-key'

db = SQLAlchemy(app)

# ----------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------
class Product(db.Model):
    ProductID   = db.Column(db.Integer, primary_key=True)
    Name        = db.Column(db.String(255), nullable=False, unique=True)
    Category    = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text,    nullable=False)
    Price       = db.Column(db.Numeric(10, 2), nullable=False)
    Stock       = db.Column(db.Integer, nullable=False)

class Customer(db.Model):
    CustomerID       = db.Column(db.Integer, primary_key=True)
    FirstName        = db.Column(db.String(255), nullable=False)
    LastName         = db.Column(db.String(255), nullable=False)
    Email            = db.Column(db.String(255), nullable=False, unique=True)
    Password         = db.Column(db.String(255), nullable=False)
    Phone            = db.Column(db.String(20), nullable=False, unique=True)
    RegistrationDate = db.Column(db.Date, nullable=False, default=date.today)

class Order(db.Model):
    OrderID    = db.Column(db.Integer, primary_key=True)
    CustomerID = db.Column(db.Integer, db.ForeignKey('customer.CustomerID'), nullable=False)
    OrderDate  = db.Column(db.Date,    nullable=False, default=date.today)
    TotalPrice = db.Column(db.Numeric(10,2), nullable=False)
    customer   = db.relationship('Customer', backref='orders')

class Review(db.Model):
    ProductID  = db.Column(db.Integer, db.ForeignKey('product.ProductID'),  primary_key=True)
    CustomerID = db.Column(db.Integer, db.ForeignKey('customer.CustomerID'), primary_key=True)
    Review     = db.Column(db.Text,    nullable=False)
    product    = db.relationship('Product',  backref='reviews')
    customer   = db.relationship('Customer', backref='reviews')

class OrderProduct(db.Model):
    OrderID   = db.Column(db.Integer, db.ForeignKey('order.OrderID'),   primary_key=True)
    ProductID = db.Column(db.Integer, db.ForeignKey('product.ProductID'), primary_key=True)
    Quantity  = db.Column(db.Integer, nullable=False)
    order     = db.relationship('Order',   backref='order_items')
    product   = db.relationship('Product')

# ----------------------------------------------------------------------
# Seeder
# ----------------------------------------------------------------------
def _populate_sample_data():
    Product.query.delete()
    Customer.query.delete()
    Order.query.delete()
    OrderProduct.query.delete()
    Review.query.delete()
    db.session.commit()

    products = [
        (1, 'Apple pie', 'Fruit', 9.99, 50, 'Pie made with home grown apples.'),
        (2, 'Pumpkin pie', 'Fruit', 12.99, 40, 'Delicious pumpkin pie for the entire family.'),
        (3, 'Pecan pie', 'Nut', 14.99, 30, 'Rich pecan pie with a caramelized filling.'),
        (4, 'Cherry pie', 'Fruit', 11.99, 45, 'A sweet and tasty cherry pie.'),
        (5, 'Lemon pie', 'Citrus', 13.99, 35, 'A yummy pie filled with lemon.'),
        (6, 'Banana Cream pie', 'Dairy', 15.99, 32, 'Banana lovers will enjoy this tasty pie.'),
        (7, 'Coconut Cream pie', 'Dairy', 16.99, 24, 'Delicious, creamy pie with a nice tropical flavor.'),
        (8, 'Key Lime pie', 'Citrus', 14.99, 18, 'Scrumptious lime pie, makes you feel like you are in Florida.'),
        (9, 'Peanut Butter pie', 'Nut', 10.99, 25, 'A pie so delicious that Mr. Peanut would be proud.'),
        (10, 'Chocolate Chess pie', 'Dairy', 12.99, 31, 'A wonderful pie for chocolate lovers.')
    ]
    for pid,name,cat,price,stock,desc in products:
        db.session.add(Product(ProductID=pid, Name=name, Category=cat, Price=price, Stock=stock, Description=desc))

    customers = [
        (1, 'John', 'Doe', 'johndoe@example.com','password1','555-1234','2024-01-15'),
        (2, 'Jane', 'Smith','janesmith@example.com','password2','555-5678','2024-02-10'),
        (3, 'Matt', 'Watts','mattwatts@example.com','password3','555-8765','2024-03-05'),
        (4, 'Michael','Brown','michaelbrown@example.com','password4','555-4321','2024-04-01'),
        (5, 'Sophia','Wilson','sophiawilson@example.com','password5','555-6789','2024-03-20'),
        (6, 'Adam','West','adamwest@example.com','password6','555-1357','2024-04-05'),
        (7, 'Bob','Villa','bobvilla@example.com','password7','555-2468','2024-03-23'),
        (8, 'Claire','Dunphey','clairedunphey@example.com','password8','555-8888','2024-10-30'),
        (9, 'Daria','Morgandorfer','dariamorgandorfer@example.com','password9','555-9999','2024-11-18'),
        (10,'Eddard','Stark','eddardstark@example.com','password0','555-0000','2024-12-20')
    ]
    for cid,fn,ln,email,pw,phone,reg in customers:
        db.session.add(Customer(CustomerID=cid, FirstName=fn, LastName=ln, Email=email, Password=pw, Phone=phone, RegistrationDate=date.fromisoformat(reg)))

    reviews = [
        (1,1,'This pie is amazing! The apple filling is sweet.'),
        (2,2,'A wonderful pumpkin pie. It’s the perfect dessert for sharing around the dinner table!'),
        (3,3,'Could have been better. The pecans were a bit too crunchy.'),
        (4,4,'Love this cherry pie! The filling melts in your mouth and each bite is heavenly.'),
        (5,5,'The lemon pie was good, but it lacks in lemon flavor.'),
        (6,6,'The banana flavor was out of this world. I will definitely return for this pie!'),
        (7,7,'This pie tasted like sunscreen. Do NOT order this pie.'),
        (8,8,'This is an average key lime pie, not the best or worst I have had.'),
        (9,9,'So good! I ate it with chocolate ice cream and it tasted like a Reeses cup.'),
        (10,10,'Checkmate! Best chocolate chess pie I have ever had.'),
        (7,1,'I have ordered every pie here and the Coconut Cream is the BEST!'),
        (9,4,'After tasting every pie I can say that the Peanut Butter pie is the WORST!')
    ]
    for pid,cid,text in reviews:
        db.session.add(Review(ProductID=pid, CustomerID=cid, Review=text))

    orders = [
        (1,1,'2024-04-02',29.98),(2,2,'2024-04-03',25.98),(3,3,'2024-04-04',28.97),
        (4,4,'2024-04-05',41.97),(5,5,'2024-04-06',37.98),(6,6,'2024-04-07',25.98),
        (7,7,'2024-04-08',30.98),(8,8,'2024-11-09',14.99),(9,9,'2024-12-10',10.99),
        (10,10,'2024-12-21',12.99),(11,4,'2025-01-01',41.97),(12,1,'2025-02-28',135.90),
        (13,2,'2025-03-01',149.90),(14,4,'2025-03-02',135.09),(15,3,'2025-03-03',9.99),
        (16,3,'2025-03-04',12.99),(17,3,'2025-03-05',14.99),(18,3,'2025-03-06',11.99),
        (19,3,'2025-03-07',13.99),(20,3,'2025-03-08',15.99),(21,3,'2025-03-09',16.99),
        (22,3,'2025-03-10',14.99),(23,3,'2025-03-11',10.99),(24,3,'2025-03-12',12.99),
        (25,10,'2025-03-13',47.96),(26,9,'2025-03-14',78.95),(27,8,'2025-03-14',69.94),
        (28,7,'2025-03-14',77.94),(29,6,'2025-03-14',9.99),(30,5,'2025-03-14',86.94),
        (31,4,'2025-03-14',91.94),(32,3,'2025-03-14',9.99),(33,2,'2025-03-14',9.99),
        (34,1,'2025-03-14',99.90)
    ]
    for oid,cid,od,total in orders:
        db.session.add(Order(OrderID=oid, CustomerID=cid, OrderDate=date.fromisoformat(od), TotalPrice=total))

    items = [
        (1,1,2),(2,2,2),(3,3,1),(3,5,1),(4,4,3),(5,1,1),(5,2,1),(6,1,1),
        (6,6,1),(7,5,1),(7,7,1),(8,8,1),(9,9,1),(10,10,1),(11,4,3),(12,1,1),
        (12,2,1),(12,3,1),(12,4,1),(12,5,1),(12,6,1),(12,7,1),(12,8,1),(12,9,1),
        (12,10,1),(13,3,10),(14,1,1),(14,2,1),(14,3,1),(14,4,1),(14,5,1),(14,6,1),
        (14,7,1),(14,8,1),(14,9,1),(14,10,1),(15,1,1),(16,2,1),(17,3,1),(18,4,1),
        (19,5,1),(20,6,1),(21,7,1),(22,8,1),(23,9,1),(24,10,1),(25,9,2),(25,10,2),
        (26,8,3),(26,7,2),(27,1,2),(27,2,2),(27,4,2),(28,3,3),(28,9,3),(29,1,1),
        (30,5,3),(30,8,3),(31,6,2),(31,7,2),(31,10,2),(32,1,1),(33,1,1),(34,1,10)
    ]
    for oid,pid,qty in items:
        db.session.add(OrderProduct(OrderID=oid, ProductID=pid, Quantity=qty))

    db.session.commit()
    print("✅ Sample data seeded.")

# =======================
# Product Routes
# =======================

@app.route('/')
def home():
    return redirect(url_for('list_products'))

@app.route('/products')
def list_products():
    q = request.args.get('search', '')
    if q:
        products = Product.query.filter(Product.Name.contains(q)).all()
    else:
        products = Product.query.all()
    return render_template('list_products.html', products=products)

@app.route('/product/add', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':
        p = Product(
            Name        = request.form['name'],
            Category    = request.form['category'],
            Description = request.form['description'],
            Price       = request.form['price'],
            Stock       = request.form['stock']
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('list_products'))
    return render_template('add_edit.html', entity='Product', record=None)

@app.route('/product/edit/<int:id>', methods=['GET','POST'])
def edit_product(id):
    p = Product.query.get_or_404(id)
    if request.method == 'POST':
        p.Name        = request.form['name']
        p.Category    = request.form['category']
        p.Description = request.form['description']
        p.Price       = request.form['price']
        p.Stock       = request.form['stock']
        db.session.commit()
        return redirect(url_for('list_products'))
    return render_template('add_edit.html', entity='Product', record=p)

@app.route('/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    p = Product.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('list_products'))

# =======================
# Customer Routes
# =======================
@app.route('/customers')
def list_customers():
    q = request.args.get('search', '')
    if q:
        customers = Customer.query.filter(
            (Customer.FirstName.contains(q)) | (Customer.LastName.contains(q))
        ).all()
    else:
        customers = Customer.query.all()
    return render_template('list_customers.html', customers=customers)

@app.route('/customer/add', methods=['GET','POST'])
def add_customer():
    if request.method == 'POST':
        c = Customer(
            FirstName        = request.form['first_name'],
            LastName         = request.form['last_name'],
            Email            = request.form['email'],
            Password         = request.form['password'],
            Phone            = request.form['phone'],
            RegistrationDate = request.form['registration_date']
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('list_customers'))
    return render_template('add_edit.html', entity='Customer', record=None)

@app.route('/customer/edit/<int:id>', methods=['GET','POST'])
def edit_customer(id):
    c = Customer.query.get_or_404(id)
    if request.method == 'POST':
        c.FirstName = request.form['first_name']
        c.LastName  = request.form['last_name']
        c.Email     = request.form['email']
        if request.form['password']:
            c.Password = request.form['password']
        c.Phone            = request.form['phone']
        c.RegistrationDate = request.form['registration_date']
        db.session.commit()
        return redirect(url_for('list_customers'))
    return render_template('add_edit.html', entity='Customer', record=c)

@app.route('/customer/delete/<int:id>', methods=['POST'])
def delete_customer(id):
    c = Customer.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('list_customers'))

# =======================
# Order Routes
# =======================
@app.route('/orders')
def list_orders():
    q = request.args.get('search', '')
    if q:
        orders = Order.query.filter_by(CustomerID=q).all()
    else:
        orders = Order.query.all()
    return render_template('list_orders.html', orders=orders)

@app.route('/order/add', methods=['GET','POST'])
def add_order():
    if request.method == 'POST':
        o = Order(
            CustomerID = request.form['customer_id'],
            OrderDate  = request.form['order_date'],
            TotalPrice = request.form['total_price']
        )
        db.session.add(o)
        db.session.commit()
        return redirect(url_for('list_orders'))
    return render_template('add_edit.html', entity='Order', record=None)

@app.route('/order/edit/<int:id>', methods=['GET','POST'])
def edit_order(id):
    o = Order.query.get_or_404(id)
    if request.method == 'POST':
        o.CustomerID = request.form['customer_id']
        o.OrderDate  = request.form['order_date']
        o.TotalPrice = request.form['total_price']
        db.session.commit()
        return redirect(url_for('list_orders'))
    return render_template('add_edit.html', entity='Order', record=o)

@app.route('/order/delete/<int:id>', methods=['POST'])
def delete_order(id):
    o = Order.query.get_or_404(id)
    db.session.delete(o)
    db.session.commit()
    return redirect(url_for('list_orders'))

# =======================
# OrderProduct Routes
# =======================
@app.route('/order_items')
def list_order_products():
    q = request.args.get('search', '')
    if q:
        items = OrderProduct.query.filter(
            (OrderProduct.OrderID == q) | (OrderProduct.ProductID == q)
        ).all()
    else:
        items = OrderProduct.query.all()
    return render_template('list_order_products.html', order_products=items)

@app.route('/order_item/add', methods=['GET','POST'])
def add_order_product():
    if request.method == 'POST':
        op = OrderProduct(
            OrderID   = request.form['order_id'],
            ProductID = request.form['product_id'],
            Quantity  = request.form['quantity']
        )
        db.session.add(op)
        db.session.commit()
        return redirect(url_for('list_order_products'))
    return render_template('add_edit.html', entity='Order_Product', record=None)

@app.route('/order_item/edit/<int:order_id>/<int:product_id>', methods=['GET','POST'])
def edit_order_product(order_id, product_id):
    op = OrderProduct.query.get_or_404((order_id, product_id))
    if request.method == 'POST':
        op.Quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('list_order_products'))
    return render_template('add_edit.html', entity='Order_Product', record=op)

@app.route('/order_item/delete/<int:order_id>/<int:product_id>', methods=['POST'])
def delete_order_product(order_id, product_id):
    op = OrderProduct.query.get_or_404((order_id, product_id))
    db.session.delete(op)
    db.session.commit()
    return redirect(url_for('list_order_products'))

# =======================
# Review Routes
# =======================
@app.route('/reviews')
def list_reviews():
    q = request.args.get('search', '')
    if q:
        reviews = Review.query.filter(
            (Review.ProductID == q) | (Review.CustomerID == q)
        ).all()
    else:
        reviews = Review.query.all()
    return render_template('list_reviews.html', reviews=reviews)

@app.route('/review/add', methods=['GET','POST'])
def add_review():
    if request.method == 'POST':
        r = Review(
            ProductID  = request.form['product_id'],
            CustomerID = request.form['customer_id'],
            Review     = request.form['review']
        )
        db.session.add(r)
        db.session.commit()
        return redirect(url_for('list_reviews'))
    return render_template('add_edit.html', entity='Review', record=None)

@app.route('/review/edit/<int:product_id>/<int:customer_id>', methods=['GET','POST'])
def edit_review(product_id, customer_id):
    r = Review.query.get_or_404((product_id, customer_id))
    if request.method == 'POST':
        r.Review = request.form['review']
        db.session.commit()
        return redirect(url_for('list_reviews'))
    return render_template('add_edit.html', entity='Review', record=r)

@app.route('/review/delete/<int:product_id>/<int:customer_id>', methods=['POST'])
def delete_review(product_id, customer_id):
    r = Review.query.get_or_404((product_id, customer_id))
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for('list_reviews'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        _populate_sample_data()
    serve(app, host='0.0.0.0', port=5000)