import pymysql

host='127.0.0.1' #input("Enter host :")
u_name='root' #input("Enter database admin username :")
u_pwd='czxcz' #input("Enter databse admin password :")
db_name='db' #input("Enter databse name :")
clist = ['coin1','coin2','coin3','coin4','coin5']


def create_db(host,u_name,u_pwd,db_name,clist):
    conn=pymysql.connect(host,u_name,u_pwd) #Enter host,username,password respectively
    try:
        cur = conn.cursor()
        
        cur.execute("""DROP DATABASE IF EXISTS """+ db_name)
        conn.commit()
        cur.execute("create database "+ db_name)
        conn.commit()
        cur.execute("use "+ db_name)  #Enter database name, current databse "auth"
        cur.execute("create table user(session VARCHAR(36), username VARCHAR(50) NOT NULL PRIMARY KEY, password VARCHAR(50) NOT NULL, mobile VARCHAR(20) NOT NULL, secret VARCHAR(16),auth_st VARCHAR(1));")
        conn.commit()
        cur.execute("insert into user (username, password,mobile,auth_st) values ('admin@nds.com','admin@nds','+918890861118','N');")
        conn.commit()        
        cur.execute("create table balance(username VARCHAR(100) NOT NULL PRIMARY KEY, coin1 DOUBLE NOT NULL, coin2 DOUBLE NOT NULL, coin3 DOUBLE NOT NULL, coin4 DOUBLE NOT NULL, coin5 DOUBLE NOT NULL, inr DOUBLE NOT NULL, FOREIGN KEY (username) REFERENCES user(username));")
        conn.commit()
        cur.execute("insert into balance values ('admin@nds.com',0,0,0,0,0,0);")
        conn.commit()

        for i in clist:
            cur.execute("create table "+i+"_buy(username VARCHAR(100) NOT NULL, date DATETIME NOT NULL, volume DOUBLE NOT NULL, price DOUBLE NOT NULL, FOREIGN KEY (username) REFERENCES user(username));")
            conn.commit()
            cur.execute("create table "+i+"_sell(username VARCHAR(100) NOT NULL, date DATETIME NOT NULL, volume DOUBLE NOT NULL, price DOUBLE NOT NULL, FOREIGN KEY (username) REFERENCES user(username));")
            conn.commit()
            
        cur.execute("create table trade(date DATETIME NOT NULL, volume DOUBLE NOT NULL, price DOUBLE NOT NULL);")                       
        conn.commit()
    finally:
        conn.close()
        
        
create_db(host,u_name,u_pwd,db_name,clist)