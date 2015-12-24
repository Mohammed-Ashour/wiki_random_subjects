from bs4 import BeautifulSoup
import urllib
import webbrowser
import sqlite3

WIKI_RANDOM = "https://en.wikipedia.org/w/api.php?action=query&list=random&rnnamespace=0&rnlimit=10&format=xml"


def show_db_data(your_cursor): #prints all db data
    for row in your_cursor.execute("SELECT * FROM wikisubs"):
        print " you have visitid " + str(row)


def connect_base_db(): #makes a connection to db and returns connection object and cursor object
    sql_conn    = sqlite3.connect('wiki_read_subjects.db')
    sql_cursor  = sql_conn.cursor()
    sql_cursor.execute('''create table if not exists wikisubs(subject text,  id text primary key, link text)''')
    sql_cursor.execute('''create table if not exists favourite( id text primary key, someinfo text)''')
    return sql_cursor , sql_conn



def insert_values_into_db (cursor, title, id, link): #inserts data to db
    cursor.execute("INSERT INTO wikisubs VALUES (?, ?, ?);", (title, id, link))


def ask_if_fav(cursor, id):
    opinion = raw_input("Did you like the subject ! (y for yes , n for no) ")
    if opinion.lower() == "y" :
        info = raw_input("what's your impression about the subject !")
        cursor.execute("INSERT INTO favourite VALUES (?, ?);", (id, info))

def show_detailed_data(cursor):
    cursor.execute('''select subject, link, someinfo from wikisubs inner join favourite 
    where wikisubs.id = favourite.id ''')
    all_rows = cursor.fetchall()
    for row in all_rows:
    # row[0] returns the first column in the query (name), row[1] returns email column.
        print('{0} : {1}, {2}'.format(row[0], row[1], row[2]))

    



def browse_wiki_random_articles(): #makes decision to browse and store subjects title and links
    cursor, sql_connection = connect_base_db() #opens db
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
            insert_values_into_db(cursor, title, title_id, subject_link) #inserts data to the db

            ask_if_fav(cursor, title_id)
            c = raw_input("press any key to go next or write (fav) to get details of your favourite subjects  ! ")
            if c.lower() == "fav" : 
                show_detailed_data(cursor)

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
    try_to_connect = 0

    try :
        connection = urllib.urlopen(WIKI_RANDOM)
    except Exception as e:
        if try_to_connect > 3 :
            raise e
        try_to_connect +=1
    else :

        response =  connection.read()
        connection.close()
        soup = BeautifulSoup(response, "html.parser") #arrange response
        links = soup.findAll('page') # gets all 'page' data 
        return links

    


def main():
    browse_wiki_random_articles()

if __name__ == '__main__':
    main()

