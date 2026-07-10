import os
import dbconn
from flask import Flask,render_template,request,jsonify,flash
import smtplib
from email.mime.text import MIMEText
import pandas as pd
import Sentiment as st
from deep_translator import GoogleTranslator
import langid
from find_nearest import find_nearest_sentence
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

suggester = 1
isGuest = 0
hi="no"
file2 = open(os.path.join(BASE_DIR, "common_drugs.dat"),"rb")
import pickle
x = pickle.load(file2)
diabetes_medications_lower,bp_medications_lower,heart_disease_medications_lower = x
foo = ""
def detect_language(text):
    return langid.classify(text)[0]
def translate_to_english(text):
    return GoogleTranslator(source='auto', target='en').translate(text)
def translate_to_hi(text):
    caa = []
    for i in text:
        caa.append(GoogleTranslator(source='auto', target='hi').translate(i))
    return caa
def translate_to_hindi(text):
    translated_text = ''
    chunk_size = 500  # Adjust the chunk size as needed
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i+chunk_size]
        translation = GoogleTranslator(source='auto', target='hi').translate(chunk)
        translated_text += translation + ' '
    translated_text = translated_text.strip()
    return translated_text
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_APP_PASSWORD = os.environ["EMAIL_APP_PASSWORD"]

#initialize the app variable
app = Flask(__name__)

curr_email = ""
connection = dbconn.DBConnection()
conn = connection.createConnection(hostname= os.environ["DB_HOST"],
    u_name = os.environ["DB_USER"],
    passwd =  os.environ["DB_PASSWORD"],
    db =  os.environ["DB_NAME"])
cursor = connection.create_cursor(conn)
lst1 = []
cursor.execute("SELECT COND FROM DRUG3")
rs = cursor.fetchall()  
for i in rs:
    lst1.append(i[0])
#print(lst1)
@app.route('/')
#app route for main page
def home():
    #return render_template("result.html")
    return render_template("login.html")


@app.route("/forgot_password",methods=["GET"])
def forgot_password():
    return render_template('forget_password.html')
@app.route('/index',methods=['POST'])
def index():
    if request.method == 'POST':
        if request.form['clicked']=='Register':

            return render_template('index.html')
        global foo
        global email
        email=request.form['email']
        password=request.form['password']
        A = "SELECT * from login_Details where user_name = '{}' and password='{}'".format(email,password).upper()
        cursor.execute(A)  
        rs = cursor.fetchone()
        p,q,r = -1,-1,-1
        if(rs!=None):
            print("Hi:",rs)
            
            p = rs[0]
        # print(rs)
        B="SELECT name, email, phone_number FROM USER_DETAILS WHERE email = %s"
        cursor.execute(B, (email,))
        data = cursor.fetchone()
        print(data)
        try:
            name, email, phone_number = data
        except:
            return render_template("login.html",msg = "Invalid Login Credentials")
        print(name,email,phone_number)
        C="SELECT BP_DRUG,HEART_DRUG,DIABETES_DRUG,MEDICATIONS from SURVEY_REPORT where email=%s"
        cursor.execute(C,(email,))
        data1=cursor.fetchone()
        print(data1)
        try:
            bp,heart,diabetes,other = data1
        except:
            return render_template("login.html",msg = "Invalid Login Credentials")
        if bp == '':
            bp = "NIL"
        if heart =='':
            heart = "NIL"
        if diabetes == '':
            diabetes = "NIL"
        if other == 'NA' or other == 'NIL' or other == 'na' or other == 'nil' or other=='' or other=='Na' or other=='Nil':
            other = "NIL"
        print(bp,heart,diabetes)
        
        print(p,q,r)
        if(rs==[] or rs==None):
            return render_template("login.html",msg = "Invalid Login Credentials")
        P = "SELECT FEEDBACK FROM LOGIN_COUNT WHERE EMAIL = '{}'".format(email).upper()
        Q = "SELECT RECOMMEND FROM SURVEY_REPORT WHERE EMAIL = '{}'".format(email).upper()
        print(P)
        cursor.execute(P)
        D = cursor.fetchone()
        print(D)
        try:
            print(D[0])
        except ArithmeticError:
            return render_template("login.html",msg = "Invalid login credentials")
        cursor.execute(Q) 
        PQ = cursor.fetchone() 
        global suggester 
        suggester = int(PQ[0])
       
        if(D[0]=='Y' and rs!=None):
            return render_template("chatbot.html",name=name,email=email,phone_number=phone_number,bp=bp,heart=heart,diabetes=diabetes,other=other)
        foo = email
        cursor.execute("SELECT * FROM login_details where user_name='{}' and password='{}'".format(email,password).upper())
        account = cursor.fetchone()
        if account:
            A = "SELECT DOR FROM LOGIN_COUNT where email='{}'".format(email).upper()
            cursor.execute(A)
            print(A)
            rs = cursor.fetchall()
            print(rs[0][0])
            E = (type(rs[0][0]))
            F = "SELECT DATEDIFF(NOW(),'{}') from login_count".format(rs[0][0]).upper()
            print(F)
            cursor.execute(F)  
            rs = cursor.fetchall()
            if(rs[0][0]>=3):
                return render_template("result.html")
            #conn.commit()
            global isGuest 
            isGuest = 0
            global curr_email
            curr_email = email
            return render_template('chatbot.html',name=name,email=email,phone_number=phone_number,bp=bp,heart=heart,diabetes=diabetes,other=other)
        else:
            return render_template("login.html",msg = "Invalid login credentials")
    return render_template('login.html')





@app.route('/register',methods=['POST'])
def register():
    global curr_email
    data = request.get_json()
    curr_email = data['emailId']
    print(curr_email)
    print(curr_email)
    #insert username, password, email, phone number,gender,dob into database
    cursor.execute("SELECT * from login_details where user_name='{}'".format(curr_email,).upper())
    rs = cursor.fetchone()
    if(rs):
        return render_template("index.html",msg = "Email Id already Exists")
    
    
    
    F = ('''CALL ADD_USER('{}','{}',{},{},'{}','{}','{}')'''.format(data['fullName'],data['emailId'],data['phoneNumber'],data['age'],data['gender'],data['dob'],data['password']))
    
    cursor.execute(F)
    from datetime import datetime
# Get the current date and time
    current_date_time = datetime.now()
    G = ("INSERT INTO LOGIN_COUNT VALUES('{}','{}','{}')".format(curr_email,str(current_date_time.date()),'N')).upper()
    cursor.execute(G)
    conn.commit()
    return render_template("login.html")
@app.route('/guest',methods=["GET"])
def guest():
    global isGuest
    isGuest = 1
    return render_template("chatbot.html",is_guest=isGuest,is_check=1)

@app.route('/med', methods=["POST"])
def med():
    global email
    B="SELECT name, email, phone_number FROM USER_DETAILS WHERE email = %s"
    cursor.execute(B, (email,))
    data = cursor.fetchone()
    name, email, phone_number = data
    print(name,email,phone_number)
    C="SELECT BP_DRUG,HEART_DRUG,DIABETES_DRUG,MEDICATIONS from SURVEY_REPORT where email=%s"
    D="SELECT RECOMMEND from SURVEY_REPORT where email=%s"
    cursor.execute(C,(email,))
    data1=cursor.fetchone()
    bp,heart,diabetes,other = data1
    if bp == '':
        bp = "NIL"
    if heart =='':
        heart = "NIL"
    if diabetes == '':
        diabetes = "NIL"
    if other == 'NA' or other == 'NIL' or other == 'na' or other == 'nil' or other=='' or other=='Na' or other=='Nil':
        other = "NIL"
    print(bp,heart,diabetes)
    user_choice = request.form.get("clicked")
    print(user_choice)
    D = cursor.execute(D,(email,))
    PQ = cursor.fetchone()
    global suggester
    suggester = int(PQ[0])
    if user_choice == "Yes":
        return render_template("questions.html")
    elif user_choice == "No":
       return render_template('chatbot.html',is_guest=1,is_check=0,name=name,email=email,phone_number=phone_number,bp=bp,heart=heart,diabetes=diabetes,other=other,suggester=suggester)
    else:
        return "Invalid choice"



@app.route('/reset_password',methods=["POST"])
#function to reset password
def reset_password():
    A = request.form['email']
    B = request.form['password']
    if(A!=B):
        return render_template("reset_password.html",msg="Passwords do not match")
    else:
        A = "CALL UPDATE_PASSWORD('{}','{}')".format(curr_email,A).upper()
        print(A)
        cursor.execute(A)
        #cursor.execute("CALL UPDATE_PASSWORD('{}','{}')".format(curr_email,A))
        conn.commit()
        return render_template("login.html")
@app.route('/logout',methods=["GET"])
def logout():
    return render_template("login.html")
def otpSend(x,y):
    msg = MIMEText('OTP is {}'.format(x))
    msg['Subject'] = 'OTP for HeathVision'
    msg['To'] = y
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, y, msg.as_string())
comm = 0
@app.route('/gop',methods=["POST"])

def gop():
    A = request.form['email']
    rs = "select * from login_details where user_name = '{}'".format(A).upper()
    cursor.execute(rs)
    rs = cursor.fetchall()
    if(rs):
        global curr_email
        curr_email = A
        import random 
        x = random.randint(100000,999999)
        print(x)
        global comm
        comm = x
        otpSend(x,A)
        return render_template("otpSend.html")
    else:
        return render_template("forget_password.html")


@app.route('/v_otp',methods=["POST"])
def v_otp():
    B = request.form['email']
    print(B,comm)
    if(int(B)==comm):
        return render_template("reset_password.html")
    else:
        return render_template("otpSend.html",msg = "The Entered OTP is Invalid")
    
@app.route('/questions',methods=['POST'])
def questions():
    global curr_email
    data = request.get_json()
    email= curr_email
    print("email = ",email)
    print(data)
    L3 = []
    {'bp': 'yes', 'bpd': 'QQ', 'heart': 'yes', 'diabetes': 'no', 'dpd': '', 'hpd': 'BER', 'alcohol': 'no', 'disease': 'FGTG'}
    if(data['bp']!='no'):
        L3.append(int(data['bpd'].lower() in bp_medications_lower))
    if(data['heart']!='no'):
        L3.append(int(data['hpd'].lower() in heart_disease_medications_lower))
    if(data['diabetes']!='no'):
        L3.append(int(data['dpd'].lower() in diabetes_medications_lower))
    sumup = 0
    for e in L3:
        if(e==0):
            sumup = -1
            break
    A = "SELECT EMAIL FROM SURVEY_REPORT where email=%s"
    cursor.execute(A,(email,))
    rs = cursor.fetchall()
    if(rs!=None):
        B = "CALL DELETE_USER('{}')".format(email).upper()
        cursor.execute(B)
        conn.commit()    
    Q = "CALL ADD_SURVEY('{}','{}','{}','{}','{}','{}','{}','{}','{}',{})".format(email,data['bp'],data['alcohol'],data['heart'],data['diabetes'],data['bpd'],data['hpd'],data['dpd'],data['disease'],int(sumup!=-1))
    print(Q)
    cursor.execute(Q.upper())
    #cursor.execute("UPDATE user_info SET PhysicalActivity=?, fruitsAndVegetables=?, sleep=?, stress=?, tobacco=?, alcohol=?, work=?, screen=?, disease=? WHERE email='%s'" % curr_email,
    #(data['PhysicalActivity'], data['fruitsAndVegetables'], data['sleep'], data['stress'], data['tobacco'], data['alcohol'], data['work'], data['screen'], data['disease']))
    conn.commit()
    print("success")
    return [1]

@app.route('/doesExist',methods=["POST"])
def doesExist():
    if request.method == 'POST':
        # if request.form['clicked']=='Register Now':
        data = request.get_json()
        email = data.get('email')
        cursor.execute("select * from login_details where user_name = '{}'".format(email).upper())
        A = cursor.fetchone()
        #use edge
        if(A!=None):
            # return render_template("index.html",msg="Email exists")
            print("Found")
            return [1]
        else:
            return [0]
def translate_to_original_language(text, original_lang):
    return GoogleTranslator(source='en', target=original_lang).translate(text)
@app.route('/renderIndexPage',methods=['GET'])
def emailCheck():
    if request.method=='GET':
        print(100)
        return render_template('index.html',msg='Email already exists')
@app.route('/otpAuthentication', methods=['POST'])
def otpAuthentication():
    if request.method == 'POST':
        # if request.form['clicked']=='Register Now':
        data = request.get_json()
        email = data.get('email')
        #session['email']=email
        print(email)
        otp = data.get('otp')
        otpSend(otp,email)
        return [1]
    #     print(data)
    return [1]


@app.route('/update', methods=["POST"])
def update():
    name = request.form['name']
    email = request.form['email']
    phone_number = request.form['phone_number']
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"})

    A = "SELECT * from login_details where user_name = '{}' and password='{}'".format(email, old_password).upper()
    cursor.execute(A)
    rs = cursor.fetchall()
    print(rs)
    if old_password!='' and new_password=='' and confirm_password=='' and phone_number=='':
        if rs:
            return jsonify({"error": "Please enter new password or new phone number"})
        else:
            return jsonify({"error": "Invalid old password"})
    elif old_password!='' and new_password!='' and confirm_password!='' and phone_number=='':
        if rs:
            B="CALL UPDATE_PASSWORD('{}','{}')".format(email, new_password).upper()
            cursor.execute(B)
            conn.commit()
            return jsonify({"success": "Account updated successfully"})
        else:
            return jsonify({"error": "Invalid old password"})
    elif phone_number!='' and old_password!='' and new_password=='' and confirm_password=='':
        if rs:
            C="UPDATE user_details SET phone_number = '{}' WHERE email = '{}'".format(phone_number, email).upper()
            cursor.execute(C)
            conn.commit()
            return jsonify({"success": "Account updated successfully"})
        else:
            return jsonify({"error": "Invalid old password"})
    elif phone_number!='' and old_password!='' and new_password!='' and confirm_password!='': 
        if rs:
            B = "CALL UPDATE_PASSWORD('{}','{}')".format(email, new_password).upper()
            C = "UPDATE user_details SET name = '{}', phone_number = '{}' WHERE email = '{}'".format(name, phone_number, email).upper()
            cursor.execute(B)
            conn.commit()
            cursor.execute(C)
            conn.commit()
        else:
            return jsonify({"error": "Invalid old password"})
            

        # C = "SELECT BP_DRUG,HEART_DRUG,DIABETES_DRUG,MEDICATIONS from survey_report where email=%s"
        # cursor.execute(C, (email,))
        # datac = cursor.fetchone()
        # bp, heart, diabetes, other = datac

        # # Handle cases where the data might be empty or missing
        # bp = bp if bp else "NIL"
        # heart = heart if heart else "NIL"
        # diabetes = diabetes if diabetes else "NIL"
        # other = other if other and other.lower() not in ['na', 'nil'] else "NIL"
        return jsonify({"success": "Account updated successfully"})
    else:
        return jsonify({"error": "Invalid old password"})
        
@app.route('/questionsOpen',methods=['GET'])
def questionsOpen():
    return render_template('questions.html')

@app.route('/predict',methods=["POST"])
def predict():
    global hi
    dd = request.get_json()
    symptoms = dd.get('symptoms').lower()
    print(symptoms)
    # tr = translate_to_english(symptoms)
    A = detect_language(symptoms)
    #print(A)
   # print(symptoms)
   # print(suggester)
    hi = "no"
    if A!='en':
        hi = "yes"
        try:
            translated = translate_to_english(symptoms)
        except Exception:
            translated = None
        if not translated:
            return ["we couldn't understand that, please try rephrasing"]
        symptoms = translated.strip().lower()
    dup = find_nearest_sentence(symptoms)
    dup=symptoms
    # print(dup)
    #print(symptoms)
    if(dup.startswith("i have") or dup.startswith("recommend me") or dup.startswith("suggest me") or symptoms.startswith("i am suffering") or symptoms.startswith("i'm suffering")):
        xx = []
        d = 0
        #print(symptoms)
        for i in lst1:
            #print(i)
            if(i.lower() in symptoms.lower()):
                xx.append(i)
                break
                
        print(xx)
        try:
            P = "SELECT drugname from drug3 where cond='{}' and rating>7 and sentiment='pos' order by rating desc".format(xx[0]).upper()
            print(P)
            #print(P)
            cursor.execute(P)
        except:
            print("heee")
            return ["we don't have information for this condition"]  
        rs = cursor.fetchall()
        L2 = []
        for i in rs:
            L2.append(i[0])
        print(L2)
        return [L2,hi]
    elif(dup.startswith("i am") or symptoms.startswith("i'm") or dup.startswith("can") or symptoms.startswith("what") or symptoms.startswith("tell")):
        print(symptoms)
        print(dup)
        global isGuest
        import pickle
       # file = open("pqpq.kpm","rb")
        file = open(os.path.join(BASE_DIR, "drug_details2.nsk"),"rb")
        xx = pickle.load(file)
        for i in xx:
            if(i[-1]=='/'):
                continue
            
            if(i.strip().lower() in symptoms.lower()):
                #print(i)
                #print(xx[i])
                #A = detect_language(i)
                #print(A)
                #print(xx[i])
                if(str(A) in ('mr','hi')):
                    xx[i]['description'] = translate_to_hi(xx[i]['description'])
                    xx[i]['dosage'] = translate_to_hi(xx[i]['dosage'])
                    xx[i]['side_effects'] = translate_to_hi(xx[i]['side_effects'])
                    return [xx[i],suggester,isGuest,dup,1]
                
                return [[xx[i]],suggester,isGuest,dup,0]
        return ["we don't have information about this drug"]
    else:
        if hi == "yes":
            # symptoms was already translated to English above; avoid re-translating
            # already-English text, which the translation API can't handle.
            return ['hi']
        try:
            tr = translate_to_english(symptoms)
        except Exception:
            tr = None
        if not tr:
            return ['hi']
        A = detect_language(tr)
        if(A!="en"):
            return [translate_to_original_language(tr)]
        print(A)
        return ['hi']
    
    return symptoms
@app.route('/loginOpen',methods=['GET'])
def loginOpen():
    return render_template('login.html')

@app.route('/go_to_chatbot',methods=["POST"])
def go_to_chatbot():
    B="SELECT name, email, phone_number FROM USER_DETAILS WHERE email = %s"
    global email
    cursor.execute(B, (email,))
    data = cursor.fetchone()
    name, email, phone_number = data
    print(name,email,phone_number)
    C="SELECT BP_DRUG,HEART_DRUG,DIABETES_DRUG,MEDICATIONS from SURVEY_REPORT where email=%s"
    cursor.execute(C,(email,))
    datac=cursor.fetchone()
    bp,heart,diabetes,other = datac
    if bp == '':
        bp = "NIL"
    if heart =='':
        heart = "NIL"
    if diabetes == '':
        diabetes = "NIL"
    if other == 'NA' or other == 'NIL' or other == 'na' or other == 'nil' or other=='' or other=='Na' or other=='Nil':
        other = "NIL"
    print(bp,heart,diabetes)    
    data1 = request.form['dg']
    data2 = request.form['cd']
    data3 = request.form['fb']
    data4 = request.form['rate']
    obj = st.Sentiment()
    cleaned_review = obj.clean_and_truncate_text(data3)
    sentiment_me = obj.analyze_sentiment_berttweet(cleaned_review)
    query = "CALL INSERT_DRUGS('{}','{}','{}','{}')".format(data1,data2,sentiment_me['label'],int(data4)*2).upper()
    cursor.execute(query)
    PT = "UPDATE LOGIN_COUNT SET FEEDBACK = 'Y' WHERE EMAIL = '{}'".format(foo).upper()
    cursor.execute(PT)
    conn.commit()
    global isGuest 
    isGuest = 0
    return render_template("chatbot.html",is_guest=1,name=name,email=email,phone_number=phone_number,bp=bp,heart=heart,diabetes=diabetes,other=other)
if(__name__ == '__main__'):
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))