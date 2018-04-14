from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask.ext.jsonpify import jsonify
from flask_restful import reqparse
from flask_cors import CORS
from jose import jwt
import pymysql
import uuid
import pyotp

host='127.0.0.1' #input("Enter host :")
u_name='root' #input("Enter database admin username :")
u_pwd='czxcz' #input("Enter databse admin password :")
db_name='db' #input("Enter databse name :")


app = Flask(__name__)
api = Api(app)
CORS(app)


c = ['coin1','coin2','coin3','coin4','coin5']

admin='admin@nds.com'

b_comm=0.25
s_comm=0.25


class Register(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, help='Username to create user')
            parser.add_argument('password', type=str, help='Password to create user')
            parser.add_argument('mobile', type=str, help='Email address of user')
            
            args = parser.parse_args()
            
            uname = args['username']
            upassword = args['password']
            umobile = args['mobile']
            
            conn=pymysql.connect(host,u_name,u_pwd,db_name) # connect to database
            cur = conn.cursor()
            cur.execute("insert into user(username,password,mobile,auth_st) values (%s,%s,%s,'N')" ,(uname,upassword,umobile))
            conn.commit()
            cur.execute("insert into balance values(%s,0,0,0,0,0,0)",(uname))
            conn.commit()
            
            return {'Username': uname, 'Password': upassword, 'Mobile': umobile}
        
            conn.close()

        except Exception as e:
            return {'error': str(e)}

        
class Login(Resource):
    def post(self):
        try:
            
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, help='Username to create user')
            parser.add_argument('password', type=str, help='Password to create user')
            
            args = parser.parse_args()
            
            uname = args['username']
            upassword = args['password']
            
            conn=pymysql.connect(host,u_name,u_pwd,db_name) # connect to database
            cur = conn.cursor()
            
            cur.execute("select password from user where username='%s'"%(uname))
            p=cur.fetchone()
            passwd=''.join(ch for ch in p)
            
#            cur.execute("select email from user where username=%s",(uname))
#            e=cur.fetchone()
#            email=''.join(ch for ch in e)
            
            if upassword==passwd:
                usession = str(uuid.uuid1())
                token = jwt.encode({'key':usession}, 'nds@nds', algorithm='HS256')
                print(token)
                cur.execute("update user set session=%s where username=%s" ,(usession,uname))
                conn.commit()
                return {'token': token}
            else:
                return {'error': 'Invalid Login details'}
            
            conn.close()

        except Exception as e:
            return {'error': str(e)}
        
class Auth_Status(Resource):
    def post(self):
        try:
            # Parse the arguments
            tok = request.headers["auth"]
            
            t=jwt.decode(tok, 'nds@nds', algorithms=['HS256'])
            sess=t['key']
            
            conn=pymysql.connect(host,u_name,u_pwd,db_name) # connect to database
            cur = conn.cursor()
            
            cur.execute("select auth_st from user where session='%s'"%(sess))
            p=cur.fetchone()
            stat=''.join(ch for ch in p)
    
            if stat=='Y':
                return {"Status" : "Enabled"}
            else:
                secret=pyotp.random_base32()
                
                cur.execute("select username from user where session='%s'"%(sess))
                p=cur.fetchone()
                user=''.join(ch for ch in p)
                
                cur.execute("update user set secret='%s' where username='%s'" %(secret,user))
                conn.commit()
                return {'qr': pyotp.totp.TOTP(secret).provisioning_uri(user, issuer_name="Secure App")}

            conn.close()
        except Exception as e:
            return {'error': str(e)}
        
class Auth_Enable(Resource):
    def post(self):
        try:
            tok = request.headers["auth"]
            t=jwt.decode(tok, 'nds@nds', algorithms=['HS256'])
            sess=t['key']
            
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('otp', type=int, help='OTP for auth')
            args = parser.parse_args()
            otps = args['otp']
           
            conn=pymysql.connect(host,u_name,u_pwd,db_name) # connect to database
            cur = conn.cursor()
            
            cur.execute("select auth_st from user where session='%s'"%(sess))
            p=cur.fetchone()
            stat=''.join(ch for ch in p)
    
            if stat=='Y':
                secret=pyotp.random_base32()

                cur.execute("select username from user where session='%s'"%(sess))
                p=cur.fetchone()
                user=''.join(ch for ch in p)

                cur.execute("select secret from user where username='%s'"%(user))
                q=cur.fetchone()
                secret=''.join(ch for ch in q)
                
                totp = pyotp.TOTP(secret)
                iotp=int(totp.now())
                
                if otps == iotp:
                    cur.execute("update user set auth_st='N' where username='%s'" %(user))
                    conn.commit()
                    return {"Status" : "Disabled Now!"}
                else:
                    return {"Status" : "Invalid otp!"}
            
            else:
                secret=pyotp.random_base32()

                cur.execute("select username from user where session='%s'"%(sess))
                p=cur.fetchone()
                user=''.join(ch for ch in p)

                cur.execute("select secret from user where username='%s'"%(user))
                q=cur.fetchone()
                secret=''.join(ch for ch in q)
                
                totp = pyotp.TOTP(secret)
                iotp=int(totp.now())
                
                if otps == iotp:
                    cur.execute("update user set auth_st='Y' where username='%s'" %(user))
                    conn.commit()
                    return {"Status" : "Enabled Now!"}
                else:
                    return {"Status" : "Invalid otp!"}
            conn.close()
        except Exception as e:
            return {'error': str(e)}

class Balance(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, help='Username to create user')
            parser.add_argument('token', type=str, help='Current token')
            parser.add_argument('coin_type', type=str, help='Type of Coin')
            parser.add_argument('balance', type=float, help='balance to add')
            
            args = parser.parse_args()
            
            uname = args['username']
            tok = args['token']
            ctype = args['coin_type']
            bal = args['balance']            
            
            t=jwt.decode(tok, 'nds@nds', algorithms=['HS256'])
            sess=t['key']
            
            conn=pymysql.connect(host,u_name,u_pwd,db_name) # connect to database
            cur = conn.cursor()
            
            resu = cur.execute("select username from user where session=%s",(sess))
            if resu > 0:
            
                cur.execute("select username from user where session=%s",(sess))
                p=cur.fetchone()
                user=''.join(ch for ch in p)
                
                
                if user==uname:
                    if ctype in c:
                        cur.execute("update balance set %s=%f where username='%s'" %(ctype,bal,user))
                        conn.commit()
                        return {'Balance': bal}
                    elif ctype=='inr':
                        cur.execute("update balance set inr=%f where username='%s'" %(bal,user))
                        conn.commit()
                        return {'INR bal': bal}
                    else:
                        return {'error': 'Invalid coin type'}
                else:
                    return {'error': 'Invalid Login details'}
            else:
                return {'error': 'Invalid Login details'}
            
            
            conn.close()
        except Exception as e:
            return {'error': str(e)}
        


class Sell(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, help='Username to create user')
            parser.add_argument('token', type=str, help='Current token')
            parser.add_argument('coin_type', type=str, help='Type of Coin to sell')
            parser.add_argument('volume', type=int, help='Volume of Coin')
            parser.add_argument('price', type=int, help='Price of Coin')
            
            args = parser.parse_args()
            
            uname = args['username']
            tok = args['token']
            ctype = args['coin_type']
            vol = args['volume']
            price = args['price']
            
            t=jwt.decode(tok, 'nds@nds', algorithms=['HS256'])
            sess=t['key']
            
            conn=pymysql.connect(host,u_name,u_pwd,db_name) # connect to database
            cur = conn.cursor()
            
            res = cur.execute("select username from user where session=%s",(sess))
            if res > 0:
            
                cur.execute("select username from user where session=%s",(sess))
                p=cur.fetchone()
                user=''.join(ch for ch in p)
                
                
                if uname==user:
                    if ctype in c:
                        
                        cur.execute("select %s from balance where username='%s'" %(ctype,uname))
                        usr_v = cur.fetchone()
                        usr_vol=usr_v[0]
                        
                        
                        comm=(vol*price*s_comm/100)
                        
                        if vol <= usr_vol:
                            resu=cur.execute("select * from %s_buy;" %(ctype))
                            if resu > 0 :
                            
                                cur.execute("select price,volume,username,date from %s_buy;"%(ctype))
                                for i in range(cur.rowcount):
                                    row = cur.fetchone()
                                    if price == row[0]:
                                        cur_p=row[0]
                                        cur_v=row[1]
                                        cur_u=row[2]
                                        cur_d=row[3]
                                        if vol < cur_v:
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((vol*cur_p)-comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,vol,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,vol,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((vol*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(comm*2,admin))
                                            conn.commit()
                                            cur.execute("update %s_buy set volume=(volume-%d) where username='%s' && price=%d && date='%s'" %(ctype,vol,cur_u,cur_p,cur_d))
                                            conn.commit()
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)" %(vol,cur_p))
                                            conn.commit()
                                            return {'Sell Statement Added for': ctype}
                                            break
                                        elif vol == cur_v:
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((vol*cur_p)-comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,vol,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,cur_v,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((cur_v*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(comm*2,admin))
                                            conn.commit()
                                            cur.execute("delete from %s_buy where username='%s' && volume=%d && price=%d && date='%s'" %(ctype,cur_u,cur_v,cur_p,cur_d))
                                            conn.commit()
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)" %(cur_v,cur_p))
                                            conn.commit()
                                            return {'Sell Statement Added for': ctype}   
                                            break
                                        elif vol > cur_v:
                                            diff=vol-cur_v
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((cur_v*cur_p)-comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,cur_v,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,cur_v,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((cur_v*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(comm*2,admin))
                                            conn.commit()                                 
                                            cur.execute("delete from %s_buy where username='%s' && volume=%d && price=%d && date='%s'" %(ctype,cur_u,cur_v,cur_p,cur_d))
                                            conn.commit()
                                            cur.execute("insert into %s_sell values(%s,CURTIME(),%d,%d)"%(ctype,cur_u,diff,cur_p))
                                            conn.commit()                                    
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)"%(cur_v,cur_p))
                                            conn.commit()
                                            return {'Sell Statement Added for': ctype}
                                            break
                                        
                                    elif price < row[0]:
                                        cur_p=row[0]
                                        cur_v=row[1]
                                        cur_u=row[2]
                                        cur_d=row[3]
                                        diff_p=(cur_p-price)
                                        if vol < cur_v:
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((vol*price)-comm),uname))
                                            conn.commit()                                  
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,vol,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,vol,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((vol*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %((diff_p+(comm*2)),admin))
                                            conn.commit()
                                            cur.execute("update %s_buy set volume=(volume-%d) where username='%s' && price=%d && date='%s'" %(ctype,vol,cur_u,cur_p,cur_d))
                                            conn.commit() 
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)" %(vol,cur_p))
                                            conn.commit()
                                            return {'Sell Statement Added for': ctype}
                                            break
                                        elif vol == cur_v:
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((vol*price)-comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,vol,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,cur_v,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((cur_v*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %((diff_p+(comm*2)),admin))
                                            conn.commit()                                    
                                            cur.execute("delete from %s_buy where username='%s' && volume=%d && price=%d && date='%s'" %(ctype,cur_u,cur_v,cur_p,cur_d))
                                            conn.commit()                                   
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)"%(cur_v,cur_p))
                                            conn.commit()
                                            return {'Sell Statement Added for': ctype}   
                                            break
                                        elif vol > cur_v:
                                            diff=vol-cur_v
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((cur_v*price)-comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,cur_v,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,cur_v,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((cur_v*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %((diff_p+(comm*2)),admin))
                                            conn.commit()                                    
                                            cur.execute("delete from %s_buy where username='%s' && volume=%d && price=%d && date='%s'" %(ctype,cur_u,cur_v,cur_p,cur_d))
                                            conn.commit()
                                            cur.execute("insert into %s_sell values(%s,CURTIME(),%d,%d)" %(ctype,cur_u,diff,cur_p))
                                            conn.commit()                                    
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)" %(cur_v,cur_p))
                                            conn.commit()
                                            return {'Sell Statement Added for': ctype}
                                            break
                                    else:
                                        cur.execute("insert into %s_sell values('%s',CURTIME(),%d,%d)" %(ctype,user,vol,price))
                                        conn.commit()
                                        return {'Sell Statement Added for': ctype}
                                        break
                            else:
                                cur.execute("insert into %s_sell values('%s',CURTIME(),%d,%d)" %(ctype,user,vol,price))
                                conn.commit()
                                return {'Sell Statement Added for': ctype}                                
                        else:
                            return {'error': 'Insufficient volume for transaction!'}
                    else:
                        return {'error': 'Invalid coin type'}
                else:
                    return {'error': 'Invalid Login details'}
            else:
                return {'error': 'Invalid Login details'}
            
            conn.close()
        except Exception as e:
            return {'error': str(e)}
       

class Buy(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, help='Username to create user')
            parser.add_argument('token', type=str, help='Current token')
            parser.add_argument('coin_type', type=str, help='Type of Coin to sell')
            parser.add_argument('volume', type=int, help='Volume of Coin')
            parser.add_argument('price', type=int, help='Price of Coin')
            
            args = parser.parse_args()
            
            uname = args['username']
            tok = args['token']
            ctype = args['coin_type']
            vol = args['volume']
            price = args['price']
            
            t=jwt.decode(tok, 'nds@nds', algorithms=['HS256'])
            sess=t['key']
            
            conn=pymysql.connect(host,u_name,u_pwd,db_name) # connect to database
            cur = conn.cursor()
            
            res = cur.execute("select username from user where session=%s",(sess))
            if res > 0:
            
                cur.execute("select username from user where session=%s",(sess))
                p=cur.fetchone()
                user=''.join(ch for ch in p)
                
                
                if uname==user:
                    if ctype in c:
                        
                        cur.execute("select inr from balance where username='%s'"%(uname))
                        inr_b = cur.fetchone()
                        inr_bal=inr_b[0]
                        
                        comm=(vol*price*b_comm/100)
    
                        if ((vol*price)+comm) <= inr_bal:
                            
                        
                            resu=cur.execute("select * from %s_sell;" %(ctype))
                            if resu > 0 :
                                cur.execute("select price,volume,username,date from %s_sell;" %(ctype))
                                for i in range(cur.rowcount):
                                    row = cur.fetchone()
                                    if price == row[0]:
                                        cur_p=row[0]
                                        cur_v=row[1]
                                        cur_u=row[2]
                                        cur_d=row[3]
                                        if vol < cur_v:
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((vol*cur_p)+comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,vol,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,vol,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((vol*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(comm*2,admin))
                                            conn.commit()                                    
                                            cur.execute("update %s_sell set volume=(volume-%d) where username='%s' && price=%d && date='%s'" %(ctype,vol,cur_u,cur_p,cur_d))
                                            conn.commit()                                   
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)"%(vol,cur_p))
                                            conn.commit()
                                            return {'Buy Statement Added for': ctype}
                                            break
                                        elif vol == cur_v:
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((vol*cur_p)+comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,vol,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,cur_v,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((cur_v*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(comm*2,admin))
                                            conn.commit()                                 
                                            cur.execute("delete from %s_sell where username='%s' && volume=%d && price=%d && date='%s'" %(ctype,cur_u,cur_v,cur_p,cur_d))
                                            conn.commit()                                   
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)"%(cur_v,cur_p))
                                            conn.commit()
                                            return {'Buy Statement Added for': ctype} 
                                            break
                                        elif vol > cur_v:
                                            diff=vol-cur_v
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((cur_v*cur_p)+comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,cur_v,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,cur_v,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((cur_v*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(comm*2,admin))
                                            conn.commit()                                 
                                            cur.execute("delete from %s_sell where username='%s' && volume=%d && price=%d && date='%s'" %(ctype,cur_u,cur_v,cur_p,cur_d))
                                            conn.commit()
                                            cur.execute("insert into %s_buy values(%s,CURTIME(),%d,%d)"%(ctype,cur_u,diff,cur_p))
                                            conn.commit()                                    
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)"%(cur_v,cur_p))
                                            conn.commit()
                                            return {'Buy Statement Added for': ctype}
                                            break
                                    elif price > row[0]:
                                        cur_p=row[0]
                                        cur_v=row[1]
                                        cur_u=row[2]
                                        cur_d=row[3]
                                        ext_p=(price-cur_p)
                                        if vol < cur_v:
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((vol*price)+comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,vol,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,vol,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((vol*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %((ext_p+(comm*2)),admin))
                                            conn.commit()
                                            cur.execute("update %s_sell set volume=(volume-%d) where username='%s' && price=%d && date='%s'" %(ctype,vol,cur_u,cur_p,cur_d))
                                            conn.commit()                                   
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)"%(vol,cur_p))
                                            conn.commit()
                                            return {'Buy Statement Added for': ctype}
                                            break
                                        elif vol == cur_v:
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((vol*price)+comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,vol,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,cur_v,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((cur_v*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %((ext_p+(comm*2)),admin))
                                            conn.commit()                                    
                                            cur.execute("delete from %s_sell where username='%s' && volume=%d && price=%d && date='%s'" %(ctype,cur_u,cur_v,cur_p,cur_d))
                                            conn.commit()                                   
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)"%(cur_v,cur_p))
                                            conn.commit()
                                            return {'Buy Statement Added for': ctype}  
                                            break
                                        elif vol > cur_v:
                                            diff=vol-cur_v
                                            cur.execute("update balance set inr= (inr-%d) where username='%s'" %(((cur_v*price)+comm),uname))
                                            conn.commit()                                    
                                            cur.execute("update balance set %s=(%s+%d) where username='%s'" %(ctype,ctype,cur_v,uname))
                                            conn.commit()
                                            cur.execute("update balance set %s=(%s-%d) where username='%s'" %(ctype,ctype,cur_v,cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %(((cur_v*cur_p)-comm),cur_u))
                                            conn.commit()
                                            cur.execute("update balance set inr= (inr+%d) where username='%s'" %((ext_p+(comm*2)),admin))
                                            conn.commit()                                    
                                            cur.execute("delete from %s_sell where username='%s' && volume=%d && price=%d && date='%s'" %(ctype,cur_u,cur_v,cur_p,cur_d))
                                            conn.commit()
                                            cur.execute("insert into %s_buy values('%s',CURTIME(),%d,%d)"%(ctype,cur_u,diff,cur_p))
                                            conn.commit()                                    
                                            cur.execute("insert into trade values(CURTIME(),%d,%d)"%(cur_v,cur_p))
                                            conn.commit()
                                            return {'Buy Statement Added for': ctype}
                                            break
                                    else:
                                        cur.execute("insert into %s_buy values('%s',CURTIME(),%d,%d)"%(ctype,user,vol,price))
                                        conn.commit()
                                        return {'Buy Statement Added for': ctype}
                                        break
                            else:
                                cur.execute("insert into %s_buy values('%s',CURTIME(),%d,%d)"%(ctype,user,vol,price))
                                conn.commit()
                                return{'Buy Statement Added for ': ctype}                          
                        else:
                            return {'error': 'Insufficient Balance for transaction!'}
                    else:
                        return {'error': 'Invalid coin type'}
                else:
                    return {'error': 'Invalid Login details'}
            else:
                return {'error': 'Invalid Login details'}            
            
            conn.close()
        except Exception as e:
            return {'error': str(e)}
        
api.add_resource(Register, '/reg')
api.add_resource(Login, '/log')
api.add_resource(Balance, '/bal')
api.add_resource(Auth_Status, '/stat')
api.add_resource(Auth_Enable, '/switch')
api.add_resource(Buy, '/buy')
api.add_resource(Sell, '/sell')

if __name__ == '__main__':
     app.run(port=5555,host='0.0.0.0')
