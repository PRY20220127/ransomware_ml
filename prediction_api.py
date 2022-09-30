from datetime import datetime
import os
from flask import Flask, request, jsonify
import pickle
import pandas as pd
from flask_cors import CORS, cross_origin
import mysql.connector
import json
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
cors = CORS(app)
db=mysql.connector.connect(host="localhost", user="ramsonware",password="server77VM",database="data_source")

@app.route('/about')
def about():
    return 'The about page'

@app.route("/logs", methods=['GET'])
def logsroute():
    query = f'''
        SELECT * FROM
        results re
        INNER JOIN data da ON re.DATA_SOURCE_ID = da.ID
        ORDER BY re.ID DESC
        '''
    cursor = db.cursor()
    cursor.execute(query)
    row_headers=[x[0] for x in cursor.description] 
    result = cursor.fetchall()
    json_data = []
    for value in result:
        json_data.append(dict(zip(row_headers, value)))
    
    return jsonify(results=json_data)
    return json.dumps(result, default=str)

@app.route("/", methods=['POST', 'GET'])
def score():
    if(request.files):
        uploaded_file = request.files['csv']
        data_frame = pd.read_csv(uploaded_file, sep=";")
        data_frame.fillna(value=0, inplace=True)
        data_frame.replace('N/A', 0, inplace=True)
        data_frame.replace('', 0, inplace=True)

        loaded_model = pickle.load(open('model.sav', 'rb'))

        X = data_frame.drop(["FAMILIA"], axis = 1)
        result = loaded_model.predict(X)
        
        email_message = "Se generó un reporte de análisis de ransomware con el siguiente detalle: \n\n"

        for index, row in data_frame.iterrows():
            query=f"""INSERT INTO data
                    (ARTEFACTO, 
                    REGWRITE, 
                    REGOPEN, 
                    REGREAD, 
                    PROC, 
                    PMFILES, 
                    PMURLS, 
                    NETHOSTS, 
                    NETREQUESTS, 
                    FILECREATED, 
                    DLLLOADED, 
                    COMMANDLINE, 
                    DOMAIN, 
                    TCP, 
                    UDP, 
                    FAMILIA, 
                    DATE_ADDED) VALUES
                    ({row['ARTEFACTO']},
                    {row['REGWRITE']},
                    {row['REGOPEN']},
                    {row['REGREAD']},
                    {row['PROC']},
                    {row['PMFILES']},
                    {row['PMURLS']},
                    {row['NETHOSTS']},
                    {row['NETREQUESTS']},
                    {row['FILECREATED']},
                    {row['DLLLOADED']},
                    {row['COMMANDLINE']},
                    {row['DOMAIN']},
                    {row['TCP']},
                    {row['UDP']},
                    {row['FAMILIA']},
                    NOW()
                    )"""
            
            cursor = db.cursor()
            cursor.execute(query)
            db.commit()
            data_id = cursor.lastrowid
            result_detail = generateMessage(result[index])
            query2 = f'''INSERT INTO results (DATA_SOURCE_ID,
                    SCORE,
                    DESCRIPTION,
                    SCORE_DATE)
                    VALUES
                    (
                        {data_id},
                        {result[index]},
                        "{result_detail}",
                        NOW()
                    )'''
            cursor.execute(query2)
            db.commit()
            email_message = email_message + f"\n{row['ARTEFACTO']} {result_detail}"
        #for index, row in data_frame.iterrows():
        #    X = row.drop(["FAMILIA"])
        #    #print(X)
        #    result = loaded_model.predict(X)
        #    print(result)
         
        #result = loaded_model.score()
        db2=mysql.connector.connect(host="localhost", user="ramsonware",password="server77VM",database="ramsonware_db")
        query3 = f'''
        SELECT * FROM
        alerts WHERE enabled = 1
        '''
        cursor2 = db2.cursor()
        cursor2.execute(query3)
        headers_alerts=[x[0] for x in cursor2.description] 
        result_alerts = cursor2.fetchall()
        alerts_data = []
        for value in result_alerts:
            alerts_data.append(dict(zip(headers_alerts, value)))
        for value in alerts_data:
            print(value["email"])
            sendEmail(value["email"], email_message)

        db2.close()
    
    return "Success"

app.config['FILE_UPLOADS'] = '/uploads'
app.config['UPLOAD_FOLDER'] = '/uploads'

def sendEmail(emailTo, emailMessage):
    emailFrom = "caghp94@outlook.com"
    message = emailMessage

    email = EmailMessage()
    email["From"] = emailFrom
    email["To"] = emailTo
    email["Subject"] = f"RansoML - Reporte de posibles amenazas {datetime.now()}"
    email.set_content(message)

    smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
    smtp.starttls()
    smtp.login(emailFrom, "server77VM")
    smtp.sendmail(emailFrom, emailTo, email.as_string())
    smtp.quit()


def generateMessage(score):
    ransomware_ids = [2,3,4]

    rounded = round(score)
    
    if(rounded == 1 or rounded == 0):
        return "Este artefacto no representa una amenaza"
    if(rounded == 2):
        value = abs(score) - rounded
        percentage = str(round(100 - abs(value) * 100, 2))
        if(1 - abs(value) > .5):
            return f"El artefacto puede representar una amenaza malware de tipo 2. Prob {percentage}%"
        else:
            return f"Es muy probable que el artefacto no contenga ransomwares. Prob {percentage}%"
    if(rounded == 3):
        value = abs(score) - rounded
        percentage = str(round(100 - abs(value) * 100, 2))
        if(1 - abs(value) > .5):
            return f"El artefacto puede representar una amenaza malware de tipo 3. Prob {percentage}%"
        else:
            return f"Es muy probable que el artefacto no contenga ransomwares. Prob {percentage}%"
    if(rounded == 4):
        value = abs(score) - rounded
        percentage = str(round(100 - abs(value) * 100, 2))
        if(1 - abs(value) > .5):
            return f"El artefacto puede representar una amenaza malware de tipo 4. Prob {percentage}%"
        else:
            return f"Es muy probable que el artefacto no contenga ransomwares. Prob {percentage}%"
    else:
        return f"El análisis de ransomware no arrojó un resultado confiable sobre este artefacto"