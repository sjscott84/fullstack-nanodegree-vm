from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantMenu.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/edit"):
				restaurantID = self.path.split("/")[1]
				print restaurantID
				self.send_response(200)
				self.send_header('Content_type', 'text/html')
				self.end_headers()
				restaurant = session.query(Restaurant).filter_by(id = restaurantID).one()

				output = ""
				output += "<html><body>"
				output += "<h1>Edit %s</h1>" % restaurant.name
				output += "<form method='POST' enctype='multipart/form-data' action='/%s/edit'>\
				<input type='text' name='new_name' value='%s'>\
				<input type='hidden' name='id' value = '%s'>\
				<input type='submit'></form>" % (restaurant.id, restaurant.name, restaurant.id)
				output += "</body></html>"

				self.wfile.write(output)

			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content_type', 'text/html')
				self.end_headers()
				restaurants = session.query(Restaurant).all()

				output = ""
				output += "<html><body>"
				for restaurant in restaurants:
					output += "<p>%s</p><br>" % restaurant.name
					output += "<a href=/%s/edit>Edit</a><br>" % restaurant.id
					output += "<a href=#>Delete</a>"
				output += "</ul><a href=/add_restaurant>Add a restaurant</a> "
				output += "</body></html>"

				self.wfile.write(output)

			if self.path.endswith("/add_restaurant"):
				self.send_response(200)
				self.send_header('Content_type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "<form method='POST' enctype='multipart/form-data' action='/add_restaurant'>\
				<h2>Name of restaurant?</h2><input type='text' name='restaurant_name'><input type=submit></form>"
				output += "</body></html>"

				self.wfile.write(output)

			"""
			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content_type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "Hello!"
				output += "<form method='POST' enctype='multipart/form-data' action='/hello'>\
				<h2>What would you like me to say?</h2><input name='message' type='text'>\
				<input type='submit' value='Submit'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				#print output
				return
			if self.path.endswith("/hola"):
				self.send_response(200)
				self.send_header('Content_type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "Hola! <a href=/hello>Back to Hello</a>"
				output += "<form method='POST' enctype='multipart/form-data' action='/hello'>\
				<h2>What would you like me to say?</h2><input name='message' type='text'>\
				<input type='submit' value='Submit'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				#print output
				return
			"""

		except IOError:
			self.send_error(404, "FIle Not Fount %s" % self.path)

	def do_POST(self):
		try:
			if self.path.endswith("/edit"):

				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('new_name')
					restaurant_id = fields.get('id')

				restaurant = session.query(Restaurant).filter_by(id = restaurant_id[0]).one()
				restaurant.name = messagecontent[0]
				session.add(restaurant)
				session.commit()

				self.send_response(301)
				self.send_header('Location', '/restaurants')
				self.end_headers()


			if self.path.endswith("/add_restaurant"):
				self.send_response(301)
				self.end_headers()

				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('restaurant_name')

				newRestaurant = Restaurant(name = "%s" % messagecontent[0])
				session.add(newRestaurant)
				session.commit()

				output = ""
				output += "<html><body><h1>You added %s!</h1></body></html>" % messagecontent[0]

				self.wfile.write(output)

			"""
			self.send_response(301)
			self.end_headers()

			#ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				fields = cgi.parse_multipart(self.rfile, pdict)
				messagecontent = fields.get('message')

			output = ""
			output += "<html><body>"
			output += "<h2>Okay, how about this: </h2>"
			output += "<h1> %s </h1>" % messagecontent[0]
			output += "<form method='POST' enctype='multipart/form-data' action='/hello'>\
			<h2>What would you like me to say?</h2><input name='message' type='text'>\
			<input type='submit' value='Submit'></form>"
			output += "</body></html>"
			self.wfile.write(output)
			print output
			"""
		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webserverHandler)
		print "Webserver running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()

if __name__ == '__main__':
	main()