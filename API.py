from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask.ext.jsonpify import jsonify
from flask_restful import reqparse
from flask_cors import CORS
import pymysql
import uuid


#import database

host='127.0.0.1' #input("Enter host :")
u_name='root' #input("Enter database admin username :")
u_pwd='czxcz' #input("Enter databse admin password :")
db_name='db' #input("Enter databse name :")

app = Flask(__name__)
CORS(app)
api = Api(app)



class Register(Resource):
    def post(self):
        try:
            # Parse the arguments
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, help='Username to create user')
            parser.add_argument('password', type=str, help='Password to create user')
            parser.add_argument('email', type=str, help='Email address of user')
            
            args = parser.parse_args()
            
            uname = args['username']
            upassword = args['password']
            uemail = args['email']
            
            conn=pymysql.connect(host,u_name,u_pwd,db_name) # connect to database
            cur = conn.cursor()
            cur.execute("insert into user(username,password,email) values (%s,%s,%s)" ,(uname,upassword,uemail))
            conn.commit()
            
            return {'Username': uname, 'Password': upassword, 'Email': uemail}
        
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
            
            cur.execute("select password from user where username=%s",(uname))
            p=cur.fetchone()
            passwd=''.join(ch for ch in p)
            
            cur.execute("select email from user where username=%s",(uname))
            e=cur.fetchone()
            email=''.join(ch for ch in e)
            
            if upassword==passwd:
                usession = str(uuid.uuid1())
                cur.execute("update user set session=%s where username=%s" ,(usession,uname))
                conn.commit()
                return {'Email': email, 'Session': usession}
            else:
                return {'error': 'Invalid Login details'}
            
            conn.close()

        except Exception as e:
            return {'error': str(e)}

#class Tracks(Resource):
#    def get(self):
#        try:
#            conn=pymysql.connect(host,u_name,u_pwd,db_name) # connect to database
#            cur = conn.cursor()
#            cur.execute("select trackid, name, composer, unitprice from tracks;")
#            
#            result = {'data': [dict(zip(map(lambda x:x[0], cur.description),row)) for row in cur]}
#            return jsonify(result)
#        except Exception as e:
#            return {'error': str(e)}
#
#class Employees_Name(Resource):
#    def get(self, employee_id):
#        try: 
#            conn=pymysql.connect(host,u_name,u_pwd,db_name) # connect to database
#            cur = conn.cursor()
#            cur.execute("select * from employees where EmployeeId =%d "  %int(employee_id))
#            
#            result = {'data': [dict(zip(map(lambda x:x[0], cur.description),row)) for row in cur]}
#            return jsonify(result)
#        except Exception as e:
#            return {'error': str(e)}
        

        
api.add_resource(Register, '/reg')
api.add_resource(Login, '/log')
#api.add_resource(Tracks, '/tracks') # Route_2
#api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3


if __name__ == '__main__':
     app.run(port=5002,host='0.0.0.0')
