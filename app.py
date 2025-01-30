from flask import Flask, redirect, url_for, request, flash, session, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = '0c03969c43eecf41b62f80ba59250e43'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\lllBB\\PycharmProjects\\pythonProject3\\b_store.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    profile_picture = db.Column(db.String(150), nullable=True)
    first_name = db.Column(db.String(150), nullable=True)
    last_name = db.Column(db.String(150), nullable=True)
    patronymic = db.Column(db.String(150), nullable=True)
    address = db.Column(db.String(250), nullable=True)
    phone_number = db.Column(db.String(50), nullable=True)
    about_me = db.Column(db.Text, nullable=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(150), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('products'))
        flash('Неверное имя пользователя или пароль!')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/products')
def products():
    products_list = Product.query.all()
    return render_template('products.html', products=products_list)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.files.get('image')

        if image:
            image_name = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))

            new_product = Product(name=name, description=description, price=price, image=image_name)
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for('products'))
        else:
            flash('Выберите изображение!')

    return render_template('add_product.html')

@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    quantity = int(request.args.get('quantity', 1))
    product = Product.query.get_or_404(product_id)

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']

    for item in cart:
        if item['id'] == product.id:
            item['quantity'] += quantity
            session.modified = True
            flash(f'Количество товара "{product.name}" увеличено до {item["quantity"]}.')
            return redirect(url_for('view_cart'))

    cart.append({'id': product.id, 'name': product.name, 'price': product.price, 'quantity': quantity})
    session.modified = True
    flash(f'Товар "{product.name}" добавлен в корзину в количестве {quantity}.')
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart=cart, total_amount=total_amount)

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    flash('Корзина успешно очищена.')
    return redirect(url_for('view_cart'))

@app.route('/checkout')
def checkout():
    return render_template('checkout.html', cart=session.get('cart', []))

@app.route('/confirm_purchase')
def confirm_purchase():
    session.pop('cart', None)
    flash('Товар куплен!')
    return redirect(url_for('products'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if request.method == 'POST':
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar:
                avatar_name = secure_filename(avatar.filename)
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], avatar_name))
                user.profile_picture = avatar_name

        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.patronymic = request.form['patronymic']
        user.address = request.form['address']
        user.phone_number = request.form['phone_number']
        user.about_me = request.form['about_me']

        db.session.commit()
        flash('Данные сохранены!')

    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)