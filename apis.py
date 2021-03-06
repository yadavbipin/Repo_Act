import sqlite3
import json
import datetime
import hackerrank_and_github_response
from flask import Flask, redirect, url_for, request,current_app
from flask_cors import CORS
app = Flask(__name__)
CORS(app,resources=r'/students_status_display')
CORS(app,resources=r'/get_details')

@app.route('/')
def root():
    return current_app.send_static_file('register.html')

@app.route('/login',methods = ['POST'])
def login():
    conn = sqlite3.connect('userdatabase.db')
    emailnumber = request.form['emailormobile']
    pswd = request.form['password']
    details = (pswd,emailnumber,emailnumber)
    cursor = conn.execute("SELECT PASSWORD,EMAIL,MOBILE FROM STUDENTREGISTRATION WHERE PASSWORD= ? AND (EMAIL = ? OR MOBILE= ?) ",details)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    #print(len(data))
    if(len(data)):
        return "Successfully Loggedin"
    else:
        return "Invalid Credentials"
#redirect("/static/updation_page.html")

@app.route('/success/<name>')
def success(name):
   return 'welcome %s' % name

#This module is to store data from the registration form.
@app.route('/register',methods = ['POST'])
def register():
    database_connection = sqlite3.connect('userdatabase.db')
    batch = request.form['batch']
    location = request.form['location']
    gender = request.form['gender']
    username = request.form['name']
    password = request.form['password']
    collegename = request.form['collegename']
    email = request.form['email']
    mobile = request.form['mobile']
    if(username =='' or password =='' or collegename=='' or email=='' or mobile=='' or gender=='' or gender=='select' or batch =='' or location==''):
        return "All Fields are Mandatory"
    else:
        email_validation = hackerrank_and_github_response.check_mail(email)
        if(len(email_validation)):
            database_connection.close()
            return "Email already exist"
        else:
            user_details = (username,password,email,mobile,collegename,gender,batch,location)
            insertion_query = '''INSERT INTO STUDENTREGISTRATION(NAME,PASSWORD,EMAIL,MOBILE,COLLEGENAME,GENDER,BATCH,LOCATION) VALUES(?,?,?,?,?,?,?,?)'''
            database_connection.execute(insertion_query,user_details)
            database_connection.commit()
            student_info = hackerrank_and_github_response.check_mail(email)
            #print(student_info['studentinfo'])
            value = student_info['userid']
            database_connection.execute("INSERT INTO STUDENTPERFORMANCE(USERID) VALUES (%s)"% value)
            database_connection.commit()
            database_connection.close()
            return "Successfully Registred"

    
@app.route('/updateuserperformance/<userid>')
def update_user_performance(userid):
    result = hackerrank_and_github_response.update_user_performance_data(userid)
    json_string = json.dumps(result)
    return json_string

@app.route('/updateall')
def update_all_status():
    result = hackerrank_and_github_response.update_all_users_status()
    return result
    
@app.route('/update_ids',methods = ['POST'])
def update_ids():
    email = request.form['email']
    hackerrankid=request.form['hackerrankid']
    githubid=request.form['githubid']
    if(hackerrankid=='' or githubid==''):
        return "All Fields are Mandatory"
    else:
        ids = {}
        ids['email_id']=email
        ids['hackerrank_id']=hackerrankid
        ids['github_id']=githubid
        result = hackerrank_and_github_response.update_all_ids(ids)
        #to update all students status
        #hackerrank_and_github_response.update_all_users_status()
        return result

@app.route('/dashboard')
def dashboard():
    mail = request.args.get('email')
    user_id = hackerrank_and_github_response.get_id_for_email(mail)
    #print("In side dashboard--",user_id)
    result = hackerrank_and_github_response.get_status_data(user_id)
    #print("In side Dashboard result--",result)
    return result

#method to display students data
@app.route('/students_data')
def students_data():
    result = hackerrank_and_github_response.get_students_data()
    return json.dumps(result)

#method to get single user total performance in hackerrank 
@app.route('/get_hack_data/<hackerrank_id>')
def get_hack_data(hackerrank_id):
    sum_data = 0
    data=hackerrank_and_github_response.get_hackerrank_data(hackerrank_id)
    #print(type(data))
    try:
        dict_data =json.loads(data)
        if(type(dict_data) is dict):
            for key in dict_data.keys():
                sum_data = sum_data + int(dict_data[key])
            #print(type(int(dict_data['2016-07-22'])))
            return str(sum_data)
    except Exception as exc:
        return "no data"

#print(get_hack_data('yandanagamani52'))    
#method to get single user weekly performance in hackerrank except final day
#@app.route('/get_weekly_hack_data/<hackerrank_id>')
def get_weekly_hack_data(hackerrank_id):
    sum_data = 0
    data=hackerrank_and_github_response.get_hackerrank_data_from_database(hackerrank_id)
    try:
        dict_data =json.loads(data)
        if(type(dict_data) is dict):
            result ={}
            weekly_count = 0
            for i in range(7):
                day = str(datetime.date.today()-datetime.timedelta(days=i))
                if(day in dict_data.keys()):
                    weekly_count = weekly_count + int(dict_data[day]) 
            #print(weekly_count)
            result['weekly_count'] = weekly_count
            if(str(datetime.date.today()) == list(dict_data.keys())[-1]):
                result['tday_count'] = dict_data[list(dict_data.keys())[-1]]
            else:
                result['tday_count'] = 0
            return result
    except Exception as exc:
        #print(hackerrank_id)
        return "no data"
    
#print(get_weekly_hack_data('sivagembali'))
    

#method to get single user performance in github
@app.route('/get_git_data/<git_id>')
def get_git_data(git_id):
    result = hackerrank_and_github_response.get_github_data(git_id)
    #print(result)
    try:
        dict_data = json.loads(result)
        if(type(dict_data) is dict):
            return str(dict_data)
    except Exception as exp:
        return "no data"

    
#method to generate dynamic student details
#result will be in this format{1:{'student_name':'g siva prasad','gender':'male','hackerrankid':'sivagembali','githubid':'sivagembali','linkedinid':'sivagembali','problems_count':157,'repo_count':8}}

@app.route('/get_details')
def get_details():
    database_connection = sqlite3.connect('userdatabase.db')
    data_cursor = database_connection.cursor()
    result_cursor = data_cursor.execute('select studentregistration.userid,studentregistration.name,studentregistration.gender,studentperformance.hackerrankid,studentperformance.githubid,studentperformance.linkedinid,studentperformance.hackerrank_problems,studentregistration.batch,studentperformance.github_status,studentregistration.job_status from studentregistration INNER JOIN studentperformance ON  studentregistration.userid=studentperformance.userid')
    result_data_set={}
    result_data = result_cursor.fetchall()
    for row in result_data:
        hack_data = json.loads(row[6])
        git_data = json.loads(row[8])
        job_data = json.loads(row[9])
        # and row[5]!='null' and row[5]!=None and row[7]!='Sept2017'
        if(hack_data['problems_count']>=66):
            row_id = row[0]
            result_data_set[row_id]={}
            result_data_set[row_id]['student_name']= row[1].title()
            result_data_set[row_id]['gender']= row[2]
            result_data_set[row_id]['hackerrankid']= row[3]
            result_data_set[row_id]['githubid']= row[4]
            result_data_set[row_id]['linkedinid']= row[5]
            result_data_set[row_id]['problems_count'] = hack_data['problems_count']
            result_data_set[row_id]['repo_count'] = git_data['repo_count']
            result_data_set[row_id]['job_status'] = job_data['job_status']
            result_data_set[row_id]['batch'] = row[7]
    #print(result_data_set)
    return json.dumps(result_data_set)
#print(get_details())
#method to read data from csv and store it in a database
@app.route('/store_students_data')    
def store_csv_data_to_database():
    result = hackerrank_and_github_response.store_data_to_database()
    return result   


#method to show students current status
@app.route('/students_status_display')
def students_status_display():
    database_connection = sqlite3.connect('userdatabase.db')
    data_cursor = database_connection.cursor()
    result_cursor = data_cursor.execute('select studentregistration.userid,studentregistration.name,studentregistration.batch,studentregistration.location,studentperformance.hackerrank_submissions,studentperformance.hackerrankid,studentperformance.hackerrank_status,studentperformance.github_status,studentperformance.hackerrank_problems,studentperformance.linkedinid from studentregistration INNER JOIN studentperformance ON  studentregistration.userid=studentperformance.userid')
    result_data_set={}
    result_data = result_cursor.fetchall()
    for row in result_data:
        row_id = row[0]
        result_data_set[row_id]={}
        result_data_set[row_id]['name'] = row[1].lower()
        result_data_set[row_id]['batch'] = row[2]
        result_data_set[row_id]['location'] = row[3]
        result_data_set[row_id]['hackerrank_submissions'] = row[4]
        result_from_weekly_hack_data = get_weekly_hack_data(row[5])
        if(result_from_weekly_hack_data!="no data"):
            result_data_set[row_id]['weekly_count'] = result_from_weekly_hack_data['weekly_count']
            result_data_set[row_id]['tday_count'] = result_from_weekly_hack_data['tday_count']
        else:
            result_data_set[row_id]['weekly_count'] =0
            result_data_set[row_id]['tday_count'] = 0
        hackerank_problems_data = json.loads(row[8])
        result_data_set[row_id]['hackerrank_problems'] = hackerank_problems_data['problems_count']
        #print(result_data_set)
    return json.dumps(result_data_set)

#method to store student data into csv
@app.route('/create_csv')
def create_csv():
    file_name = str(datetime.date.today())+".csv"
    file_access = open(file_name,'a')
    file_write = file_access.write("Name,Number of Problems\n")
    database_connection = sqlite3.connect('userdatabase.db')
    data_cursor = database_connection.cursor()
    result_cursor = data_cursor.execute('select studentregistration.userid,studentregistration.name,studentregistration.batch,studentregistration.location,studentperformance.hackerrank_submissions,studentperformance.hackerrankid,studentperformance.hackerrank_status,studentperformance.github_status,studentperformance.hackerrank_problems,studentperformance.linkedinid from studentregistration INNER JOIN studentperformance ON  studentregistration.userid=studentperformance.userid')
    result_data_set={}
    result_data = result_cursor.fetchall()
    for row in result_data:
        row_id = row[0]
        result_data_set[row_id]={}
        result_data_set[row_id]['name'] = row[1].lower()
        result_data_set[row_id]['batch'] = row[2]
        result_data_set[row_id]['location'] = row[3]
        result_data_set[row_id]['hackerrank_submissions'] = row[4]
        result_from_weekly_hack_data = get_weekly_hack_data(row[5])
        if(result_from_weekly_hack_data!="no data"):
            result_data_set[row_id]['weekly_count'] = result_from_weekly_hack_data['weekly_count']
            result_data_set[row_id]['tday_count'] = result_from_weekly_hack_data['tday_count']
        else:
            result_data_set[row_id]['weekly_count'] =0
            result_data_set[row_id]['tday_count'] = 0
        hackerank_problems_data = json.loads(row[8])
        result_data_set[row_id]['hackerrank_problems'] = hackerank_problems_data['problems_count']
        if(hackerank_problems_data['problems_count'] < 66):
            file_access.write(row[1]+","+str(hackerank_problems_data['problems_count'])+"\n")
    file_access.close()
    return "success"

if __name__ == '__main__':
    app.run(debug=True)