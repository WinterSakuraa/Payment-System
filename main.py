from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from os import path
from cloudipsp import Api, Checkout


DB_NAME = 'shop.db'

app = Flask(__name__)
app.config['SECRET_KEY'] = "sjfss dfs"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
db = SQLAlchemy(app)


def create_db(app):
    if not path.exists('.' + DB_NAME):
        db.create_all(app=app)
        print('DataBase is created')


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=True)
    isActive = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return self.title


create_db(app)


@app.route('/')
@app.route('/home')
def home():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', items=items)


@app.route('/buy/<int:id>')
def item_buy(id):
    item = Item.query.get(id)

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": str(item.price) + '00'
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@app.route('/remove/<int:id>')
def remove(id):
    item = Item.query.get_or_404(id)

    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/')
    except:
        return "An error occurred while removing the Item"


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']

        item = Item(title=title, price=price)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Error while adding item"
    else:
        return render_template('create.html')


if __name__ == '__main__':
    app.run(debug=True)
