import re, urllib, urllib2, MySQLdb


uri = 'http://www.nyaa.se/?page=rss&cats=1_37'	# Feed file
sourceOpen = urllib2.urlopen(uri) # Open url
source = sourceOpen.read()	# Read data
source = source.replace('&#40;','[').replace('&#41;',']').replace('&#39;',"'").replace('&#38;','&')	# Replace html code
items = re.findall(r'<item>(.*?)</item>',source) # Find <item> tags

db = MySQLdb.connect(host = '', user = 'danpee', passwd = '', db = 'test') # Connect to database
cur = db.cursor() # Create cursor for query execution

def main():


	cur.execute('''CREATE TABLE temptable (title text, subgroup text, link text, guid text, description text, pubdate text, id int AUTO_INCREMENT, PRIMARY KEY (id))''')
	cur.execute('''INSERT INTO temptable( title, subgroup, link, guid, description, pubdate ) (SELECT * FROM items)''')

	for item in items:
		titles = re.findall(r'<title>(.*?)</title>', item) # Find <title> tags
		links = re.findall(r'<link>(.*?)</link>', item) # Find <link> tags
		guids = re.findall(r'<guid>(.*?)</guid>', item) # Find <guid> tags
		pubdates = re.findall(r'<pubDate>(.*?)</pubDate>', item) # Find <pubDate> tags
		descriptions = re.findall(r'<description>(.*?)</description>', item) # Find <description> tags

		for title in titles:

			if '[' in title and ']' in title:
				if title.index('[') == 0:
					subgroup = re.search(r'\[(.*?)\]', title).group(1)
				else:
					subgroup = 'Anonymous'
			else:
				subgroup = 'Anonymous'

			for link in links:

				for guid in guids:

					for description in descriptions:

						for pubdate in pubdates:
							
							insertQuery = '''INSERT INTO temptable (title,subgroup,link,guid,description,pubdate) VALUES ('%s','%s','%s','%s','%s','%s')''' % (
								title.replace("'","\\'"),subgroup.replace("'","\\'"),link.replace("'","\\'"),guid.replace("'","\\'"),description.replace("'","\\'"),
								pubdate.replace("'","\\'"))
							cur.execute(insertQuery)
		

							db.commit()

	cur.execute('''DELETE FROM items''')
	cur.execute('''INSERT INTO items SELECT title, subgroup, link, guid, description, pubdate FROM temptable WHERE id IN (SELECT MAX( id ) FROM temptable GROUP BY title, subgroup, link, guid, pubdate)''')
	cur.execute('''DROP TABLE temptable''')

	db.commit()
main()