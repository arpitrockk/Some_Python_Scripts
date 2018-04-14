import pyotp
import time
import pymysql


def otp(host,u_name,u_pwd,db_name,user):
    conn=pymysql.connect(host,u_name,u_pwd) #Enter host,username,password respectively
    try:
        cursor = conn.cursor()
        
    #    cursor.execute("""DROP DATABASE IF EXISTS auth""")
    #    conn.commit()
    #    cursor.execute("create database auth")
    #    conn.commit()
        cursor.execute("use "+ db_name)  #Enter database name, current databse "auth"
    #    cursor.execute("create table data(user varchar(32),secret varchar(16))")
    #    conn.commit()
        
        # returns a 16 character base32 secret
        secret=pyotp.random_base32()
#        
        print("For user '%s' secret key is : %s \n\n"%(user,secret))
        
        cursor.execute("insert into data values(%s,%s)" ,(user,secret))
        conn.commit()
        
        totp = pyotp.TOTP(secret)
        
        print("For generating QR Code use the below url\n")            
        print(pyotp.totp.TOTP(secret).provisioning_uri(user, issuer_name="Secure App"))
        print("\n\n")
        
        while True:
            time.sleep(5)
            print("Current OTP:", totp.now())
    finally:
        conn.close()

host=input("Enter host :")
u_name=input("Enter database admin username :")
u_pwd=input("Enter databse admin password :")
db_name=input("Enter databse name :")
user=input("Enter a unique username :\n")
otp(host,u_name,u_pwd,db_name,user)
