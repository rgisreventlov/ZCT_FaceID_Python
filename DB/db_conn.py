import mysql.connector

hostname = "zctdatabase123.cxlbzmlhujsn.eu-central-1.rds.amazonaws.com"
username = "admin"
password = "XGcuP1YfAp8V0DgEH588"
database = "ZCT"

class Database():
    def __enter__(self):
        self.conn = mysql.connector.connect(host=hostname, user=username, passwd=password, db=database)
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, exception_type, exception_value, traceback):
        self.conn.commit()
        self.cur.close()
        self.conn.close()


createTables = 'CREATE TABLE IF NOT EXISTS face_data(id INT AUTO_INCREMENT PRIMARY KEY, face_id varchar(255), age int(6), ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'

with Database() as db:
    db.execute(createTables)
    print("Row added")



def add_row(db, face_id, age):
    db.execute(f'INSERT INTO face_data(face_id, age) VALUES("{face_id}","{age}")')