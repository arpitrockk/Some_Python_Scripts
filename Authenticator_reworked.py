import pyotp
import time
import pymysql

conn=pymysql.connect("127.0.0.1","root","czxcz") #Enter host,username,password respectively

try:
    cursor = conn.cursor()
    
#    cursor.execute("""DROP DATABASE IF EXISTS auth""")
#    conn.commit()
#    cursor.execute("create database auth")
#    conn.commit()
    cursor.execute("use auth")  #Enter database name, current databse "auth"
#    cursor.execute("create table data(user varchar(32),secret varchar(16))")
#    conn.commit()
    
    print("Select from the option below")
    print("1.Add a new user")
    print("2.Get auth key")
    print("3.Regenerate key")
    ch=int(input("Enter a choice :"))
    
    if ch==1:
        user=input("Enter a unique username :")
        secret=pyotp.random_base32()   # returns a 16 character base32 secret
        
        cursor.execute("insert into data values(%s,%s)" ,(user,secret))
        conn.commit()
        
        print("For user '%s' secret key is : %s"%(user,secret))
        totp = pyotp.TOTP(secret)
        
        while True:
            time.sleep(5)
            print("Current OTP:", totp.now())
            
    elif ch==2:
        user=input("Enter the username :")
        
        cursor.execute("select secret from data where user=%s",(user))
        r=cursor.fetchone()
        
        secret=''.join(ch for ch in r if ch.isalnum())
        print("For user '%s' secret key is : %s"%(user,secret))
        totp = pyotp.TOTP(secret)
        
        while True:
            time.sleep(5)
            print("Current OTP:", totp.now())
            
    elif ch==3:
        user=input("Enter the username :")
        secret=pyotp.random_base32()
        
        cursor.execute("update data set secret=%s where user=%s" ,(secret,user))
        conn.commit()
        
        print("For user '%s' new secret key is : %s"%(user,secret))
        totp = pyotp.TOTP(secret)
        
        while True:
            time.sleep(5)
            print("Current OTP:", totp.now())
finally:
    conn.close()

