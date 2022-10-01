# /usr/bin/env python3
# -*- coding: UTF-8 -*-
from flask import Flask, request
import MySQLdb

# 建立資料庫連線
conn = MySQLdb.connect(host="127.0.0.1",
                       user="Wanda",
                       passwd="Database4021",
                       db="course_registrations")

def add_course(NID, course_id):  # 加選課程
    query_add_course = "INSERT INTO selection VALUES('{}',{})".format(NID, course_id)
    cursor = conn.cursor()
    conn.commit()
    cursor.execute(query_add_course)
    count_now_credits(NID)

def add_quota(course_id):  # 加選課程
    query_update_stu_quota = "update student set now_cred = '{}'".format(now_cred)
    conn.commit()
    cursor.execute(query_update_stu_quota)

    get_quota = "select count_quota from course where course_id = {};".format(course_id)
    conn.commit()
    cursor.execute(get_quota)
    fetch = cursor.fetchall()
    for gq in fetch:
        quota = gq[0]

    query = "update course set count_quota = '{}'".format(quota+1)
    conn.commit()
    cursor.execute(quary)

def withdraw_course(NID,course_id): # 退選課程
    query_del_course = "delete from selection where NID = '{}' and course_id = '{}'".format(NID, course_id)
    cursor = conn.cursor()
    conn.commit()
    cursor.execute(query_del_course)

def withdraw_quota(course_id):  # 課程名額更新
    query_update_stu_quota = "update student set now_cred = '{}'".format(now_cred)
    cursor = conn.cursor()
    conn.commit()
    cursor.execute(query_update_stu_quota)

    get_quota = "select count_quota from course where course_id = {};".format(course_id)
    conn.commit()
    cursor.execute(get_quota)
    fetch = cursor.fetchall()
    for gq in fetch:
        quota = gq[0]

    query = "update course set count_quota = '{}'".format(quota-1)
    conn.commit()
    cursor.execute(quary)


###=====加選失敗可能=====###

def check_quota(course_id):  # 課程人數是否額滿
    query = "SELECT quota , count_quota FROM course WHERE course_id = {};".format(course_id)
    cursor = conn.cursor()
    cursor.execute(query)
    quota = cursor.fetchall()
    if (quota[0][1] >= quota[0][0]):  # 目前人數>=開放人數 回傳TRUE
        return True
    else:
        return False

def course_crash(NID, course_id):  # 檢查是否衝堂
    query = "SELECT day,start,end FROM time NATURAL JOIN selection WHERE selection.NID='{}';".format(
        NID)
    cursor = conn.cursor()
    cursor.execute(query)
    cur_time = cursor.fetchall()
    
    query = "SELECT day,start,end FROM time NATURAL JOIN course WHERE course.course_id={};".format(
        course_id)
    cursor = conn.cursor()
    cursor.execute(query)
    add_time = cursor.fetchall()
    for (r1, r2, r3) in cur_time:
        if (r1 == add_time[0][0] and r2 == add_time[0][1]):  # 如果加選後衝堂 回傳TRUE
            return True
    return False

def check_course_name(NID, course_id):  # 檢查是否有同樣的課
    query = "SELECT course_name FROM course NATURAL JOIN selection where selection.NID = '{}';".format(
        NID) #目前的課程 
    cursor = conn.cursor()
    cursor.execute(query)
    current = cursor.fetchall()

    query = "SELECT course_name from course where course_id = '{}';".format(course_id)
    cursor = conn.cursor()
    cursor.execute(query)
    add = cursor.fetchall()

    for (r1) in current:
        if (r1 == add[0]):  # 如果有重複回傳 TRUE
            return True
    return False

def check_credit(course_id):  # 檢查再加選課程會不會超過學分數
    query = "SELECT course_cred FROM course WHERE course_id={}".format(course_id)
    cursor = conn.cursor()
    cursor.execute(query)
    add_cred = cursor.fetchall()
    
    if (now_cred[0][0] + add_cred[0][0] > 30):
        return True
    else:
        return False

def count_now_credits(NID): # 計算目前為止的學分數
    global now_cred
    # 查詢目前課表內學分數
    query = """SELECT SUM(course_cred) FROM course
        NATURAL JOIN selection WHERE selection.NID = '{}';""".format(
        NID)
    # 執行查詢
    cursor = conn.cursor()
    cursor.execute(query)
    # 計算課程的學分數
    now_cred = cursor.fetchall()
    # print(now_cred)

def check_required(require):  # 0,1 轉換 必選修
    global requirement
    if require == 1:
        requirement = "必修"
    else:
        requirement = "選修"
    return requirement

def get_selectionID(course_id,NID):
    global getclass
    query = "select course_id from selection where course_id = '{}' and NID = '{}'".format(
        course_id,NID)
    cursor = conn.cursor()
    cursor.execute(query)
    fetch = cursor.fetchall()
    print(fetch)
    for gc in fetch:
        getclass = '{}'.format(gc[0])
    
    return getclass

def get_time(time_id):  # 取得課程的時間
    global time_slot
    query = "SELECT day,start,end from time where time_slot = '{}';".format(
        time_id)
    cursor = conn.cursor()
    cursor.execute(query)
    time = cursor.fetchall()
    for t in time:
        time_slot = "{}<br>{}-{}".format(t[0],t[1],t[2])
    return time_slot

def get_teacherName(course_id):
    global TName
    query = "select name from teacher natural join teach where teach.course_id = {};".format(course_id)
    cursor = conn.cursor()
    cursor.execute(query)
    fetch = cursor.fetchall()
    for f in fetch:
        TName = "{}".format(f[0])
    return TName

app = Flask(__name__)

@app.route('/')
def login():
    signin = """
    <form method="post" action="/action" >
        <h1><font color="#1A3487"><b>《歡迎來到選課系統》</h1></b></font><br>
        <font color="black"><b>請輸入NID：<input name="NID"></b></font><br>
        <font><b>請輸入Password：<input type="password" name="pass"></b></font><br>
        <input type="submit" value="登入">
    </form>
    """
    
    return signin


@app.route('/action', methods=['POST'])
def action():
    # 取得輸入的文字
    global NID
    NID = request.form.get("NID")
    # password = request.form.get("pass")
    
    # 欲查詢的 query 指令
    query = "SELECT * FROM student where NID = '{}';".format(NID)
    # 執行查詢
    cursor = conn.cursor()
    conn.commit()
    cursor.execute(query)
    data = cursor.fetchall() #取出所有資料

    #建立table 顯示學生基本資料
    stu = []

    table = "<tr><td>NID</td><td>Name</td><td>Now_Credit</td><td>Department</td></tr>"
    stu.append(table)
    
    #迴圈個別寫入 學生資訊
    for row in data:
        a = "<tr><td>%s</td>"%row[0]
        stu.append(a)
        b = "<td>%s</td>"%row[1]
        stu.append(b)
        c = "<td>%s</td>"%row[2]
        stu.append(c)
        d = "<td>%s</td></tr>"%row[3]
        stu.append(d)

    stu.insert(0,"<table  style='border:3px solid;padding:5px;' rules='all' cellpadding='5';>")
    stu.append("</table>")

    #結果
    results = """<font color="Black"><b>目前登入的身分是：</b><br>"""
    
    # 取得並列出所有查詢結果
    for description in stu:
        results += "{}".format(description)
    
    time = {'Mon.': 1, 'Tue.': 2, 'Wed.': 3, 'Thr.': 4, 'Fri.': 5, 'Sat.': 6}

    # 登入者的必修課表
    results += """
		<br><br>
        <table style='border:4px solid;padding:3px;' rules='all' cellpadding='5'>
			<tr>
				<th align='center' valign="middle"></th>
				<th align='center' valign="middle">Mon.</th>
				<th align='center' valign="middle">Tue.</th>
				<th align='center' valign="middle">Wed.</th>
				<th align='center' valign="middle">Thr.</th>
				<th align='center' valign="middle">Fri.</th>
				<th align='center' valign="middle">Sat.</th>
			</tr>
	"""

    # 找出使用者的必修課的學號、選課代碼、課程名稱、課程星期數、節次 >> 查詢課程的時間
    query = """SELECT DISTINCT selection.NID, selection.course_id, course.course_name, time.day, time.start, time.end, course.course_cred
        FROM course,time,selection WHERE course.time_slot = time.time_slot
        AND selection.course_id = course.course_id AND selection.NID = '{}';""".format(
        NID)
    cursor = conn.cursor()
    conn.commit()
    cursor.execute(query)
    fetchresult = cursor.fetchall()
    classcounter = 0

    # 比對星期數和節次將課程名稱填進去課表
    for i in range(1, 9):
        results += "<tr>"
        results += "<th align='center' valign='middle'>{}</th>".format(i)
        for j in range(1, 7):
            classcounter = 0
            results += "<td align='center' valign='middle'>"
            for (r1, r2, r3, r4, r5, r6,r7) in fetchresult:
                if (i >= (r5%8) and i <= (r6%8)) and j == time[r4]:
                    if classcounter == 0:
                        results += "{}".format(r3)
                        classcounter += 1
                    else:
                        results += "<br>{}".format(r3)
                        classcounter += 1
            results += "</td>"
        results += "</tr>"

    results += "</table>"

    results += """
		</body>
		</html> 
	"""
    
    choice = """
        <form method="post" action="/action/allcourse" >
            <b><input type="submit" value="加選課程"></b><br>
        </form>

        <form method="post" action="/all_selection">
            <input type="submit" value="退選課程">
        </form>
        <p><a href="/">Back to login</a></p>
    """

    results += choice

    return results

@app.route('/action/allcourse', methods=['POST'])
def allcourse():

    timetable = []
    
    all_class = """
    <tr>
        <td align='center' valign='middle'><b>選課鈕<td align='center' valign='middle'><b>選課代號</td>
        <td align='center' valign='middle'><b>課程名稱</td><td align='center' valign='middle'><b>學分數</td>
        <td align='center' valign='middle'><b>課程時間</td><td align='center' valign='middle'><b>開課系所</td>
        <td align='center' valign='middle'><b>必or選修</td><td align='center' valign='middle'><b>授課老師</td>
        <td align='center' valign='middle'><b>目前選課人數</td>
        <td align='center' valign='middle'><b>課程名額</td><td align='center' valign='middle'><b>課程介紹</td>
    </tr>"""
    
    timetable.append(all_class)

    query = "select * from course;"
    cursor = conn.cursor()
    conn.commit()
    cursor.execute(query)
    course = cursor.fetchall()
    
    for r in course: #r9 == remark 僅為註記 可不可以線上選課
        timetable += "<tr>"
        timetable += "<th align='center' valign='middle'><input type='radio' name='add_classID' value={}><label><br>{}</label>".format(r[0],r[1])
        timetable += "<th align='center' valign='middle'>{}</th>".format(r[0])

        for i in range(1,10):
            if i == 9:
                timetable += "<td>" 
                timetable += "{}".format(r[i-1])
            else:
                timetable += "<td align='center' valign='middle'>"
                if i == 1:
                    timetable += "{}".format(r[i])
                elif i == 2:
                    timetable += "{}".format(r[i])
                elif i == 3:
                    time_slot = get_time(r[0])
                    timetable += "{}".format(time_slot)
                elif i == 4:
                    timetable += "{}".format(r[i])
                elif i == 5:
                    requirement = check_required(r[i])
                    timetable += "{}".format(requirement)
                elif i == 6:
                    teacher = get_teacherName(r[0])
                    timetable += "{}".format(teacher)
                elif i == 7:
                    timetable += "{}".format(r[i-1])
                elif i == 8:
                    timetable += "{}".format(r[i-1])

        timetable += "</td>"
    timetable += "</tr>"

    timetable.insert(0,"<table style='border:4px solid;padding:3px;' rules='all' cellpadding='5'>")
    timetable.append("</table>")

    #結果
    results = """
    <h1> 所有課程檢視 </h1>
        <form method="post" action="/registered">
    """
    
    # 取得並列出所有查詢結果
    for description in timetable:
        results += "{}".format(description)

    results += """
        <input type='submit' value='加選'></form>

        <form method="post" action="/all_selection">
            <input type="submit" value="退選課程">
        </form>
        <p><a href="/">Back to login</a></p>"""

    return results
    

@app.route('/registered', methods=['POST'])
def registered():
    course_id = request.form.get("add_classID")
    count_now_credits(NID)

    if (check_quota(course_id)):
        view = """
        <html>
            <body>
                <h1>加選失敗，人數已滿</h1>
                <input type ="button" onclick="history.back()" value="重新選課"></input><br>
            </body>
        </html>
    """
    elif (check_course_name(NID, course_id)):
        view = """
        <html>
            <body>
                <h1>加選失敗，已有相同課程在課表中</h1>
                <input type ="button" onclick="history.back()" value="重新選課"></input><br>
            </body>
        </html>
    """
    elif (course_crash(NID, course_id)):
        view = """
        <html>
            <body>
                <h1>加選失敗，課程衝堂</h1>
                <input type ="button" onclick="history.back()" value="重新選課"></input><br>
            </body>
        </html>
    """
    elif (check_credit(course_id)):
        view = """
        <html>
            <body>
                <h1>加選失敗，學分已達上限</h1>
                <input type ="button" onclick="history.back()" value="重新選課"></input><br>
            </body>
        </html>
    """
    else:
        add_course(NID, course_id)
        view = """
        <html>
            <body>
                <h1>加選成功</h1>
                <input type ="button" onclick="history.back()" value="重新選課"></input><br>
            </body>
        </html>
    """
    
    return view

@app.route('/all_selection', methods=['POST'])
def all_selection():

    selectiontable = """
        <table style='border:4px solid;padding:3px;' rules='all' cellpadding='5'>
            <tr>
                <td align='center' valign='middle'><b>退選鈕<td align='center' valign='middle'><b>選課代號</td>
                <td align='center' valign='middle'><b>課程名稱</td>
                <td align='center' valign='middle'><b>課程時間</td><td align='center' valign='middle'><b>開課系所</td>
                <td align='center' valign='middle'><b>必or選修</td><td align='center' valign='middle'><b>授課老師</td>
                <td align='center' valign='middle'><b>目前選課人數</td><td align='center' valign='middle'><b>課程名額</td>
            </tr>
    """
    
    query = "SELECT * FROM course NATURAL JOIN selection WHERE selection.NID = '{}';".format(
        NID)
    cursor = conn.cursor()
    conn.commit()
    cursor.execute(query)
    fetch = cursor.fetchall()
    
    for r in fetch:
        selectiontable += "<tr>"
        selectiontable += "<th align='center' valign='middle'><input type='radio' name='del_classID' value={}><label><br>{}</label>".format(r[1],r[2])

        for i in range(1,10):
            if i != 9:
                selectiontable += "<td align='center' valign='middle'>"
                if i == 1:
                    selectiontable += "{}".format(r[i])
                elif i == 2:
                    selectiontable += "{}".format(r[i])
                elif i == 3:
                    time_slot = get_time(r[0])
                    selectiontable += "{}".format(time_slot)
                elif i == 4:
                    selectiontable += "{}".format(r[i])
                elif i == 5:
                    requirement = check_required(r[i])
                    selectiontable += "{}".format(requirement)
                elif i == 6:
                    teacher = get_teacherName(r[0])
                    selectiontable += "{}".format(teacher)
                elif i == 7:
                    selectiontable += "{}".format(r[i-1])
                elif i == 8:
                    selectiontable += "{}".format(r[i-1])
        selectiontable += "</td>"
    selectiontable += "</tr>"

    selectiontable += "</table>"

    results = """
    <h1> 退選檢視 </h1>
        <form method="post" action="/withdraw">
    """

    for description in selectiontable:
         results+= "{}".format(description)

    results +=  """
        <input type='submit' value='退選'></form>
        <p><a href="/">Back to login</a></p>
    """

    return results

@app.route('/withdraw', methods=['POST'])
def withdraw():
    
    course_id = request.form.get('del_classID')
    print(course_id,NID)

    my_course_id = get_selectionID(course_id,NID)
    print(my_course_id)

    query_sum_of_course_credits = """
        select course_cred from course JOIN selection on course.course_id = selection.course_id
        where selection.NID = '{}' and selection.course_id = '{}' group by course_cred""".format(
    NID, my_course_id)
    
    cursor = conn.cursor()
    cursor.execute(query_sum_of_course_credits)
    fetch = cursor.fetchall()
    for f in fetch:
        my_class_credits = f[0]
    print(my_class_credits)

    query_sum_my_credits = """select sum(course_cred) from course join selection
        on course.course_id = selection.course_id where NID = '{}';""".format(
        NID)
    cursor.execute(query_sum_my_credits)
    fetch = cursor.fetchall()
    for f in fetch:
        my_class_credits_sum = f[0]
    print(my_class_credits_sum)

    if int(my_class_credits_sum) - int(my_class_credits) >= 9:
        cursor.execute(
            "delete from registered where student_ID = '{}' and class_ID = '{}'".format(NID, my_course_id))
        conn.commit()
        success_view = """
                    <html>
                    <meta http-equiv="refresh">
                    <body>
                        <h1>退選成功</h1>
                        <input type="button" onclick="history.back()" value="返回課程清單"></input>
                    </body>
                    </html>
                """

        return success_view
    else:
        failed_view = """
                    <html>
                    <body>
                        <h1>退選失敗，不符合最低9學分</h1>
                        <input type="button" onclick="history.back()" value="返回課程清單"></input>
                    </body>
                    </html>
                """
        return failed_view