from bs4 import BeautifulSoup
import urllib
import webbrowser
import sqlite3

WIKI_RANDOM = "https://en.wikipedia.org/w/api.php?action=query&list=random&rnnamespace=0&rnlimit=10&format=xml"


def show_db_data(your_cursor): #prints all db data
	for row in your_cursor.execute("SELECT * FROM wikisubs"):
		print " you have visitid " + str(row)

def connect_db(): #makes a connection to db and returns connection object and cursor object
	sql_conn    = sqlite3.connect('wiki_read_subjects.db')
	sql_cursor  = sql_conn.cursor()
	sql_cursor.execute('''create table if not exists wikisubs(subject text, id text)''')
	return sql_cursor , sql_conn

def insert_values_into_db (cursor, title, id): #inserts data to db
	cursor.execute("INSERT INTO wikisubs VALUES (?, ?);", (title, id))


def browse_wiki_random_articles(): #makes decision to browse and store subjects title and links
	cursor, sql_connection = connect_db() #opens db
	txt_file = open("wiki_links.txt", 'a') #opens a text file to store data and links
	links = get_random_articles() #gets random articles
	links_count = 0 
	for line in links :
		title = line.get('title') #gets subject title from the link line
		title_id = line.get('id') #gets the id
		choice = raw_input('Would you like to read about '+title+'?'+'\n>>write y to browse OR stop to exit<< ' )
		if choice  == 'y' :
			subject_link = 'http://en.wikipedia.org/wiki?curid='+title_id #make subject link
			webbrowser.open_new_tab(subject_link) #opens the subject wiki page
			txt_file.write("\n"+title + "\t : \t" + subject_link ) #insert to the txt file
			cursor.execute("PRAGMA busy_timeout = 2000") #gives db enough time to store data 
			insert_values_into_db(cursor, title, title_id) #inserts data to the db
			raw_input("press any key to go next ! ")

		elif choice == "stop" : 
			
			break
		links_count += 1
		if links_count >= 12 :
			links = get_random_articles()
	sql_connection.commit() #commits all data 
	show_db_data(cursor)  #prints all db data
	cursor.close() #close cursor
	sql_connection.close() #close connection
	txt_file.close() #close file
def get_random_articles(): #gets random articles
	connection = urllib.urlopen(WIKI_RANDOM)
	response =  connection.read()
	connection.close()
	soup = BeautifulSoup(response, "html.parser") #arrange response
	links = soup.findAll('page') # gets all 'page' data 
	return links


def main():
	browse_wiki_random_articles()

if __name__ == '__main__':
	main()

