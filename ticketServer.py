import MySQLdb

conn = MySQLdb.connect(	host="localhost",
						user="ehsm",
						passwd="exceptional",
						db="ehsmTickets")
cursor = conn.cursor()
cursor.execute("SELECT * FROM tickets")
row = cursor.fetchall()
print row[0]
cursor.close()
quit()
