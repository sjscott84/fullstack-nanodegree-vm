from flask import Flask, render_template
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def RestaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).first()
	items = session.query(MenuItem).filter_by(restaurant_id = 
		restaurant.id)
	return render_template('menu.html', restaurant=restaurant, items = items)

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/')
def EditMenu(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).first()
	items = session.query(MenuItem).filter_by(restaurant_id = 
		restaurant.id)
	return render_template('menu.html', restaurant=restaurant, items = items)

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)