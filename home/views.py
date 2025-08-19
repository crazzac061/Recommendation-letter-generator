import datetime
from django.db.models.fields import DateTimeField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session

# check old password and new password
from django.contrib.auth.hashers import make_password, check_password

from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from .forms import TeacherInfoForm
from django.contrib import messages
import random
import json
from collections import OrderedDict


# imports from xhtml
from django.http import HttpResponse
from django.template.loader import get_template
#from xhtml2pdf import pisa


# serializers helps to convert queryset into json strings
from django.core import serializers

# sending email
from django.core.mail import send_mail

# to send mail to admin
from django.core.mail import mail_admins


# to create random number for OTP
from random import randint
from pdf2docx import Converter
# Create your views here.
#import os
#os.environ["SSL_CERT_FILE"] = r"C:\\Users\\lovel\\Desktop\\Recommendation-Letter-Generator\\venv\\Lib\\site-packages\\certifi\\cacert.pem"




def index(request):

    #if the user is logged in then index will not be their respective home page after login
    
    #check if the user is logged in or not
    if request.method == "GET":                                                     #if logged in 
        naam = request.COOKIES.get('student')      
        
        if StudentLoginInfo.objects.filter(username__exact=naam).exists():
            student = StudentLoginInfo.objects.get(username__exact=naam)

            teachers = TeacherInfo.objects.filter(department=student.department)
            if Application.objects.filter(std__username=naam).exists():                 #std is foreign key for StudentLoginInfo
                appli = Application.objects.filter(std__username=naam)
            else:
                appli = {}
            response = render(
                        request,
                        "student_success.html",
                        {
                            "naam": student.username,
                            "roll": student.roll_number,
                            "letter": True,
                            'applications': appli
                        },
                    )
                    
            return response
                                         #if exist
        # if StudentLoginInfo.objects.filter(username__exact=naam).exists():
        #     student = StudentLoginInfo.objects.get(username__exact=naam)
        #     teachers = TeacherInfo.objects.filter(department=student.department)
        #     response =  render(                                                     #render student home page
        #             request,
        #             "Studentform1.html",
        #             {
        #                 "naam": student.username,
        #                 "teachers": teachers,
        #                 "roll": student.roll_number,
        #             },
        #         )
            # return response
        uid = request.COOKIES.get('unique')            
        print("teacher " + str(uid))                         #if not student then might be teacher
        if TeacherInfo.objects.filter(unique_id__exact=uid).exists():
                value = 0
                unique = request.COOKIES.get('unique')                              #teacher's unique id (see schema diagram)


                # generate teachers home page
                teacher_model = TeacherInfo.objects.get(unique_id=unique)
                generated_dataharu = Application.objects.filter(professor__unique_id=unique , is_generated=True)

                dataharu = Application.objects.filter(professor__unique_id=unique)
                number = len(dataharu)
                # check if there is request or not on teachers page
                for data in dataharu:
                    if data.is_generated:
                        value += 1
                datakolength = len(dataharu)
                if datakolength == value:
                    check_value = True
                else:
                    check_value = False
                    # to convert database to json objects
                std_dataharu = serializers.serialize(
                    "json", Application.objects.filter(professor__unique_id=unique,is_generated=True)
                )
                non_generated = Application.objects.filter(
                    is_generated=False, professor__unique_id=unique
                )

                response = render(
                    request,
                    "Teacher.html",
                    {
                        "all_students": generated_dataharu,
                        "student_list": non_generated,
                        "check_value": check_value,
                        "teacher_number": number,
                        "std_dataharu": std_dataharu,
                        "teacher_model": teacher_model,
                    },
                )
                return response
        
    # if the request is not a GET request or user is not logged in , render index page
    return render(request, "index.html")
#now check studentLogin and teacherLogin


def gallery(request):
    return render(request, "gallery.html")


import textwrap
from fpdf import FPDF
from io import BytesIO as bio
#import fs
from home.forms import StudentForm

def text_to_pdf(text,roll, name):
    a4_width_mm = 270
    pt_to_mm = 0.35
    fontsize_pt = 11
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = (a4_width_mm / 1*character_width_mm)

    import unicodedata

    def normalize_text(text: str) -> str:
        # Replace “fancy” punctuation with ASCII equivalents
        replacements = {
            "’": "'",
            "‘": "'",
            "“": '"',
            "”": '"',
            "–": "-",
            "—": "-",
            "•": "*",
            "…": "...",
            "©": "(c)",
            "®": "(R)",
            "™": "TM",
        }
        for bad, good in replacements.items():
            text = text.replace(bad, good)

    # Normalize to remove accents (é -> e, ü -> u, etc.)
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    
    text = normalize_text(text)

    pdf = FPDF(orientation="P", unit="mm", format="Letter")
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', size=fontsize_pt*1.2)
    pdf.cell(0, 10,"Letter of Recommendation ",align='C')
    pdf.set_y(15)
    pdf.set_font(family="Arial", size=fontsize_pt)
    
    splitted = text.split("\n")
    a=0
    for line in splitted:
        lines = textwrap.wrap(line, width_text*1.2)

        if a==0:
            if len(lines) == 0:
                pdf.ln()
                a=a+1
                continue
        else:
            if len(lines) == 0:
                continue
      
         

        for wrap in lines:
            pdf.set_right_margin(25)

            pdf.set_x(25)
            pdf.multi_cell(0, fontsize_mm*1.5, wrap)
            a=a-1
           



    pdf.output("media/letter/"+roll+'_'+name+".pdf", "F")
    print("pdf generated")

    # docx_path = os.path.join(settings.MEDIA_ROOT, "letter", f"{roll}_{name}.docx")
    cv = Converter("media/letter/"+roll+'_'+name+".pdf")
    cv.convert("media/docs/" + roll + "_"+name + ".docx", start=0, end=None)
    print("docx generated")
    cv.close()

    # Return download link for the DOCX file




import re

### xhtml2pdf
def final(request, *args, **kwargs):
    if request.method == "POST":
        textarea1 = request.POST.get("textarea1")
        roll = request.POST.get("roll")
        unique = request.COOKIES.get('unique')
        application = Application.objects.get(std__roll_number=roll, professor__unique_id=unique)
        

        print("TEXT:\n",textarea1)

        # textarea2 = request.POST.get("textarea2")
        # textarea3 = request.POST.get("textarea3")
        letter=f'''
                \n{textarea1}
        '''
        print("inside final")
        print(textarea1)
        text_to_pdf(letter,roll, application.professor.name)
        application.is_generated = True
        application.save() 
        # messages.error(request, "Sorry!  The Credentials doesn't match.")
        send_mail('Recommendation Letter', 'Dear sir, \n Your letter has been generated your letter of recommendation. \n \n Best Regards, \n Ioe Recommendation Letter Generator', 'ioerecoletter@gmail.com', [application.email], fail_silently=True)
        return redirect("media/letter/"+roll+"_"+ application.professor.name +".pdf")

def studentfinal(request, *args, **kwargs):
    if request.method == "POST":
        pdf_or_docs = request.POST.get("id")
        roll = request.POST.get("roll")
        prof = request.POST.get('prof_name')

        if pdf_or_docs == 'pdf':
            return redirect("media/letter/"+roll+"_"+prof+".pdf")
        else: 
            try:
                return redirect("media/docs/"+roll+"_"+prof+".docx")
            except:
                return redirect("media/letter/"+roll+"_"+prof+".pdf")

def registerStudent(request):
    departments = Department.objects.all().values()
    programs = Program.objects.all().values()
    context_dict = { "departments": departments , "programs": programs}
    
    if request.method == "GET":
        naam = request.COOKIES.get('student')
        if StudentLoginInfo.objects.filter(username__exact=naam).exists():
            student = StudentLoginInfo.objects.get(username__exact=naam)

            teachers = TeacherInfo.objects.filter(department=student.department)
            if Application.objects.filter(std__username=naam).exists():                 #std is foreign key for StudentLoginInfo
                appli = Application.objects.filter(std__username=naam)
            else:
                appli = {}
            response = render(
                        request,
                        "student_success.html",
                        {
                            "naam": student.username,
                            "roll": student.roll_number,
                            "letter": True,
                            'applications': appli
                        },
                    )
                    
            return response
       
        # if StudentLoginInfo.objects.filter(username__exact=naam).exists():
        #     student = StudentLoginInfo.objects.get(username__exact=naam)
        #     teachers = TeacherInfo.objects.filter(department=student.department)
        #     response =  render(
        #             request,
        #             "Studentform1.html",
        #             {
        #                 "naam": student.username,
        #                 "teachers": teachers,
        #                 "roll": student.roll_number,
        #             },
        #         )
        #     return response
        unique = request.COOKIES.get('unique')
        if TeacherInfo.objects.filter(unique_id__exact=unique).exists():
                value = 0

                teacher_model = TeacherInfo.objects.get(unique_id=unique)
                generated_dataharu = Application.objects.filter(professor__unique_id=unique , is_generated=True)

                dataharu = Application.objects.filter(professor__unique_id=unique)
                number = len(dataharu)
                # to check if there is request or not on teachers page
                for data in dataharu:
                    if data.is_generated:
                        value += 1
                datakolength = len(dataharu)
                if datakolength == value:
                    check_value = True
                else:
                    check_value = False
                    # to convert database to json objects
                std_dataharu = serializers.serialize(
                    "json", Application.objects.filter(professor__unique_id=unique,is_generated=True)
                )
                non_generated = Application.objects.filter(
                    is_generated=False, professor__unique_id=unique
                )

                response = render(
                    request,
                    "Teacher.html",
                    {
                        "all_students": generated_dataharu,
                        "student_list": non_generated,
                        "check_value": check_value,
                        "teacher_number": number,
                        "std_dataharu": std_dataharu,
                        "teacher_model": teacher_model,
                    },
                )
                return response
        
    if request.method == "POST":
        usern = request.POST.get("name")
        roll = request.POST.get("roll")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        Pass = request.POST.get("pass")
        confirmPass = request.POST.get("confirmPass")
        depart = request.POST.get("department")
        prog = request.POST.get("program")
        department = Department.objects.get(dept_name=depart)
        program = Program.objects.get(program_name=prog)
        
        if Pass != confirmPass:
            messages.error(request, "Passwords donot match")
            return render(request, "registerStudent.html", context=context_dict )
            
        try:
            if StudentLoginInfo.objects.filter(roll_number__exact=roll):
                messages.error(request, "Student Already Exists")
                return render(request, "registerStudent.html", context=context_dict )
            else:
                Student = StudentLoginInfo.objects.create(username=usern, 
                roll_number=roll, dob=dob, department=department, program=program, gender=gender, password=make_password(Pass))
                Student.save()
                messages.error(request, "Account Sucessfully Created")
                return render(request, "loginStudent.html")
        except Exception as e:
            messages.error(request, e)
            return render(request, "registerStudent.html", context=context_dict )
    return render(request, "registerStudent.html", context=context_dict )

def loginStudent(request):
    # after login /loginstudent url will also be a homepage

    #handles just after student is logged in
    if request.method == "GET":
        naam = request.COOKIES.get('student')
        if StudentLoginInfo.objects.filter(username__exact=naam).exists():
            student = StudentLoginInfo.objects.get(username__exact=naam)

            teachers = TeacherInfo.objects.filter(department=student.department)
            if Application.objects.filter(std__username=naam).exists():                 #std is foreign key for StudentLoginInfo
                appli = Application.objects.filter(std__username=naam)
            else:
                appli = {}
            response = render(
                        request,
                        "student_success.html",
                        {
                            "naam": student.username,
                            "roll": student.roll_number,
                            "letter": True,
                            'applications': appli
                        },
                    )
                    
            return response
        unique = request.COOKIES.get('unique')
        if TeacherInfo.objects.filter(unique_id__exact=unique).exists():
                value = 0

                teacher_model = TeacherInfo.objects.get(unique_id=unique)
                generated_dataharu = Application.objects.filter(professor__unique_id=unique , is_generated=True)

                dataharu = Application.objects.filter(professor__unique_id=unique)
                number = len(dataharu)
                # to check if there is request or not on teachers page
                for data in dataharu:
                    if data.is_generated:
                        value += 1
                datakolength = len(dataharu)
                if datakolength == value:
                    check_value = True
                else:
                    check_value = False
                    # to convert database to json objects
                std_dataharu = serializers.serialize(
                    "json", Application.objects.filter(professor__unique_id=unique,is_generated=True)
                )
                non_generated = Application.objects.filter(
                    is_generated=False, professor__unique_id=unique
                )

                response = render(
                    request,
                    "Teacher.html",
                    {
                        "all_students": generated_dataharu,
                        "student_list": non_generated,
                        "check_value": check_value,
                        "teacher_number": number,
                        "std_dataharu": std_dataharu,
                        "teacher_model": teacher_model,
                    },
                )
                return response
    
    # post request from loginStudent.html
    if request.method == "POST":
        naam = request.POST.get("username")
        Pass = request.POST.get("pass")
             # check if user is real
        if StudentLoginInfo.objects.filter(username__exact=naam).exists():
            student = StudentLoginInfo.objects.get(username__exact=naam)
            if not check_password(Pass, student.password):
                messages.error(request, "Sorry!  The Credentials doesn't match.")
                return render(request, "loginStudent.html")
            teachers = TeacherInfo.objects.filter(department=student.department)


            if Application.objects.filter(std__username=naam).exists():                 #std is foreign key for StudentLoginInfo
                appli = Application.objects.filter(std__username=naam)
            else:
                appli = {}
            response = render(
                        request,
                        "student_success.html",
                        {
                            "naam": student.username,
                            "roll": student.roll_number,
                            "letter": True,
                            'applications': appli
                        },
                    )

            response.set_cookie('student', student)
            return response

        else:
            messages.error(request, "Sorry!  The Credentials doesn't match.")
            return render(request, "loginStudent.html")
        
    
    return render(request, "loginStudent.html")
            # if Application.objects.filter(std__username=naam).exists():                 #std is foreign key for StudentLoginInfo
            #     appli = Application.objects.filter(std__username=naam)
            #     if appli[0].is_generated: 
            #         response = render(
            #             request,
            #             "student_success.html",
            #             {
            #                 "naam": student.username,
            #                 "roll": student.roll_number,
            #                 "letter": appli[0].is_generated,
            #                 'applications': appli
            #             },
            #         )
                    
            #     else:
            #         messages.error(request, "You are succesfully logged in.")
            #         response =  render(
            #             request,
            #             "Studentform1.html",
            #             {
            #                 "naam": student.username,
            #                 "teachers": teachers,
            #                 "roll": student.roll_number,
            #             },
            #         )

            # else:
            #     messages.error(request, "You are succesfully logged in.")
            #     response =  render(
            #         request,
            #         "Studentform1.html",
            #         {
            #             "naam": student.username,
            #             "teachers": teachers,
            #             "roll": student.roll_number,
            #         },
            #     )
                
    #         response.set_cookie('student', student)
    #         return response

    #     else:
    #         messages.error(request, "Sorry!  The Credentials doesn't match.")
    #         return render(request, "loginStudent.html")
        
    
    # return render(request, "loginStudent.html")
#now check studentform1.html 


@login_required(login_url="/loginTeacher")
def make_letter(request):
    if request.method == "POST":
        roll = request.POST.get("roll")
        teacher_id = request.COOKIES.get("unique")
        teacher_model = TeacherInfo.objects.get(unique_id=teacher_id)

        stu = StudentLoginInfo.objects.get(roll_number=roll)
        appli = Application.objects.get(name=stu.username, professor__unique_id=teacher_id)
        paper = Paper.objects.get(application=appli)
        project = Project.objects.get(application = appli)
        
        linkedin = appli.linkedIn
        personal_statement = appli.personal_statement
        recommendation_purpose = appli.recommendation_purpose

        # Get all universities instead of just one
        universities = University.objects.filter(application=appli)
        quality = Qualities.objects.get(application=appli)
        academics = Academics.objects.get(application=appli)
        files = Files.objects.get(application=appli)

        templates = CustomTemplates.objects.filter(professor = appli.professor)

        teacher_name = appli.professor.name

        

        return render(
            request,
            "formTeacher.html",
            {
                "student": appli,
                "roll": roll,
                "paper": paper,
                "project": project,
                "university": universities,
                "quality": quality,
                "academics": academics,
                "teacher": teacher_name,
                "teacher_model": teacher_model,
                "files": files, 
                'templates': templates,
                'linkedin': linkedin,  
                'personal_statement': personal_statement, 
                'recommendation_purpose': recommendation_purpose              
                
            },
        )


def studentform1(request):
    if request.method == "POST":
        naam = request.POST.get("naam")
        uroll = request.POST.get("roll")
        uemail = request.POST.get("email")
        uprof = request.POST.get("prof")
        known_year = request.POST.get("yrs")
        
        s_project = request.POST.get("sproject")
        is_project = request.POST.get("is_project")
        
        pro1 = request.POST.get("pro1")
        has_paper = request.POST.get("has_paper")
        title_paper = request.POST.get("paper_title")
        paperlink = request.POST.get("paper_link")
        
        linkedIn_link = request.POST.get("linkedIn")
        pstatement = request.POST.get('personal_statement')
        rpurpose = request.POST.get('recommendation_purpose')
        

        
        deployed = request.POST.get('deploy')
        intern = request.POST.get('intern')

    
        subjects = Subject.objects.all()
        bisaya = []
        i = 0
        for subject in subjects:
            if request.POST.get("subject" + str(i)) is not None:
                bisaya.append(request.POST.get("subject" + str(i)))
            i = i + 1
        listToStr = ",".join([str(elem) for elem in bisaya])
        x = uprof.split("|")
        id = x[-1]
        if StudentLoginInfo.objects.filter(username=naam).exists():
            stu = StudentLoginInfo.objects.get(username=naam)
            teachers = TeacherInfo.objects.filter(department=stu.department)
            if TeacherInfo.objects.filter(unique_id=id).exists():
                prof = TeacherInfo.objects.get(unique_id=id)
                info = Application(
                    name=stu.username,
                    email=uemail,
                    professor=prof,
                    std=stu,
                    is_pro=is_project,
                    years_taught=known_year,
                    subjects=listToStr,
                    is_paper = has_paper,
                    intern = True if intern == "on" else False,
                )
                
                if Application.objects.filter(std__username = naam ,professor__name = prof.name ).exists():
                    info = Application.objects.get(std__username = naam ,professor__name = prof.name)
                    info.name=stu.username 
                    info.email=uemail 
                    info.professor=prof 
                    info.std=stu 
                    info.is_pro=is_project 
                    info.years_taught=known_year 
                    info.subjects=listToStr 
                    info.is_paper = has_paper 
                    info.intern = True if intern == "on" else False
                    info.personal_statement = pstatement 
                    info.recommendation_purpose = rpurpose
                    info.linkedIn = linkedIn_link
                    info.save() 
                    
                else:
                    info.save()

                project_info = Project(
                    supervised_project = s_project,
                    final_project = pro1,
                    deployed = True if deployed == "on" else False,
                    application = info,
                )
                
                if Project.objects.filter(application = info).exists():
                    project = Project.objects.get(application=info)
                    project.delete()
                    
                project_info.save()
                    
                
                paper_info = Paper(
                    paper_link = paperlink,
                    paper_title = title_paper,
                    application = info,
                )
                
                if Paper.objects.filter(application = info).exists():
                    paper = Paper.objects.get(application=info)
                    paper.delete()

                paper_info.save()
            
            else:
                messages.error(request, "Please select a professor.")
                return render(
                        request,
                        "Studentform1.html",
                        {
                            "naam": stu.username,
                            "teachers": teachers,
                            "roll": stu.roll_number,
                        },
                    )

            return render(request, "Studentform2.html", {'roll':uroll, 'naam' : naam, 'prof_name': prof.name},)

        else:
            messages.error(request, "Please login first")
            return render(request, "loginStudent.html")

    
    if request.method == "GET":
        naam = request.COOKIES.get('student')
        if StudentLoginInfo.objects.filter(username__exact=naam).exists():
            student = StudentLoginInfo.objects.get(username__exact=naam)
            teachers = TeacherInfo.objects.filter(department=student.department)
            response =  render(
                    request,
                    "Studentform1.html",
                    {
                        "naam": student.username,
                        "teachers": teachers,
                        "roll": student.roll_number,
                    },
                )
            return response
        # user = request.COOKIES.get('username')


    messages.error(request, "Please login first")
    return render(request, "loginStudent.html")

def studentform2(request):
    # Define max file size in bytes
    MAX_CV_SIZE = 5 * 1024 * 1024  # 10MB
    MAX_TRANSCRIPT_SIZE = 5 * 1024 * 1024  # 10MB
    MAX_PHOTO_SIZE = 3 * 1024 * 1024  # 3MB

    # if request.method == "POST":
    #     uroll = request.POST.get("roll")
    #     naam = request.POST.get("naam")
    #     prof_name = request.POST.get("prof_name")
    #     aca_gpa = request.POST.get("gpa")
    #     aca_ranking = request.POST.get("tentative_ranking")
    #     file_transcript = request.FILES.get("transcript")
    #     file_cv = request.FILES.get("cv")
    #     file_photo = request.FILES.get('photo')
    #     extra = request.POST.get('extraCurricular')

    #     universities = request.POST.getlist("universities")
    #     programs_applied = request.POST.getlist("programs_applied")
    #     deadlines = request.POST.getlist("deadlines")

    #     info = Application.objects.get(std__username=naam, professor__name=prof_name)
    #     info.is_generated = False
    #     info.save()

    #     if University.objects.filter(application=info).exists():
    #         University.objects.filter(application=info).delete()

    #     for i in range(len(universities)):
    #         uni_info = University(
    #             uni_name=universities[i],
    #             uni_deadline=deadlines[i],
    #             program_applied=programs_applied[i],
    #             application=info,
    #         )
    #         uni_info.save()

    #     if Academics.objects.filter(application=info).exists():
    #         Academics.objects.filter(application=info).delete()

    #     academics_info = Academics(
    #         gpa=aca_gpa,
    #         tentative_ranking=aca_ranking,
    #         application=info,
    #     )
    #     academics_info.save()

    #     if Files.objects.filter(application=info).exists():
    #         Files.objects.filter(application=info).delete()

    #     file_info = Files(
    #         transcript=file_transcript,
    #         CV=file_cv,
    #         Photo=file_photo,
    #         application=info,
    #     )
    #     file_info.save()

    #     if Qualities.objects.filter(application=info).exists():
    #         Qualities.objects.filter(application=info).delete()

    #     qualities_info = Qualities(
    #         extracirricular=extra,
    #         application=info,
    #     )
    #     qualities_info.save()

    #     send_mail(
    #         'Application for recommendation letter',
    #         f'Dear sir,\n {naam} has sent an application in Recommendation Letter Generator. Nearest Deadline is {deadlines[0]}. Please log in to generate the letter.\n Link: http://recommendation-generator.bct.itclub.pp.ua/',
    #         'ioerecoletter@gmail.com',
    #         [info.professor.email],
    #         fail_silently=False,
    #     )

    # return render(request, "student_success.html", {'roll': uroll, 'letter': False, 'naam': naam})

    if request.method == "POST" :
        uroll = request.POST.get("roll")

        naam = request.POST.get("naam")
        prof_name = request.POST.get("prof_name")

        # Get multiple values from form (lists of universities, programs, deadlines)
        universities = request.POST.getlist("universities")
        programs_applied = request.POST.getlist("programs_applied")
        deadlines = request.POST.getlist("deadlines")
        
        # Define nearest deadline for email
        uni_deadline = min(deadlines) if deadlines else 'No deadline'
        aca_gpa = request.POST.get("gpa")
        aca_ranking = request.POST.get("tentative_ranking")
        file_transcript = request.FILES.get("transcript")
        file_cv = request.FILES.get("cv")
        file_photo = request.FILES.get('photo')
        #presentation= request.POST.get('presentation')
        extra = request.POST.get('eca')
        #quality = request.POST.get('qual')


        # leaders = request.POST.get('quality1')
        # hardwork = request.POST.get('quality2')
        # social = request.POST.get('quality3')
        # teamwork = request.POST.get('quality4')
        # friendly = request.POST.get('quality5')
        
        # File size validation
        if file_transcript and file_transcript.size > MAX_TRANSCRIPT_SIZE:
            return render(request, "studentform.html", {"error": "Transcript file size exceeds the limit of 5MB."})
        
        if file_cv and file_cv.size > MAX_CV_SIZE:
            return render(request, "studentform.html", {"error": "CV file size exceeds the limit of 5MB."})
        
        if file_photo and file_photo.size > MAX_PHOTO_SIZE:
            return render(request, "studentform.html", {"error": "Photo file size exceeds the limit of 3MB."})



        info = Application.objects.get(std__username = naam ,professor__name = prof_name )

        info.is_generated = False
        info.save()

        # Save all universities submitted
        for i in range(len(universities)):
            if universities[i].strip():  # avoid empty rows
                uni_info = University(
                    uni_name=universities[i],
                    uni_deadline=deadlines[i],
                    program_applied=programs_applied[i],
                    application=info,
                )
                if University.objects.filter(application = info).exists():
                    uni = University.objects.get(application=info)
                    uni.delete()
                uni_info.save()

        academics_info = Academics(
            gpa = aca_gpa,
            tentative_ranking = aca_ranking,
            application  = info,
        )
        
        if Academics.objects.filter(application = info ).exists():
            academic = Academics.objects.get(application = info )
            academic.delete()
            
        academics_info.save()

        file_info = Files(
            transcript = file_transcript,
            CV = file_cv,
            Photo = file_photo,
            application = info,
        )
        
        if Files.objects.filter(application = info ).exists():
            file = Files.objects.get(application = info )
            file.delete()
            
        file_info.save()

        qualities_info = Qualities(
            # leadership = True if leaders == "on" else False,
            # hardworking = True if hardwork == "on" else False,
            # social = True if social == "on" else False,
            # teamwork = True if teamwork == "on" else False,
            # friendly =True if friendly == "on" else False,
            # quality = quality,
            # presentation = presentation,
            extracirricular = extra,
            application = info ,
        )
        
        if Qualities.objects.filter(application = info ).exists():
            quality = Qualities.objects.get(application = info )
            quality.delete()
            
        qualities_info.save()

        send_mail('Application for recommendation letter', f'Dear sir,\n {naam} has send application in Recommendation Letter Generator. Nearest Deadline is {uni_deadline}. Please log in to generate the letter.  \n Link: http://recommendation-generator.bct.itclub.pp.ua/  \n\nBest Regards,\nIoe Recommendation Letter Generator', 'ioerecoletter@gmail.com', [info.professor.email], fail_silently=True)


    return render(request, "student_success.html",{'roll':uroll, 'letter' : False, 'naam' : naam})



def loginTeacher(request):
    if request.method == "GET":
        naam = request.COOKIES.get('student')
        if StudentLoginInfo.objects.filter(username__exact=naam).exists():
            student = StudentLoginInfo.objects.get(username__exact=naam)

            teachers = TeacherInfo.objects.filter(department=student.department)
            if Application.objects.filter(std__username=naam).exists():                 #std is foreign key for StudentLoginInfo
                appli = Application.objects.filter(std__username=naam)
            else:
                appli = {}
            response = render(
                        request,
                        "student_success.html",
                        {
                            "naam": student.username,
                            "roll": student.roll_number,
                            "letter": True,
                            'applications': appli
                        },
                    )
                    
            return response
        user = request.COOKIES.get('username')
        if TeacherInfo.objects.filter(name__exact=user).exists():
                value = 0
                unique = request.COOKIES.get('unique')

                teacher_model = TeacherInfo.objects.get(unique_id=unique)
                generated_dataharu = Application.objects.get(professor__unique_id=unique , is_generated=True)

                dataharu = Application.objects.filter(professor__unique_id=unique)
                number = len(dataharu)
                # to check if there is request or not on teachers page
                for data in dataharu:
                    if data.is_generated:
                        value += 1
                datakolength = len(dataharu)
                if datakolength == value:
                    check_value = True
                else:
                    check_value = False
                    # to convert database to json objects
                std_dataharu = serializers.serialize(
                    "json", Application.objects.filter(professor__unique_id=unique,is_generated=True)
                )
                non_generated = Application.objects.filter(
                    is_generated=False, professor__unique_id=unique
                )

                response = render(
                    request,{
                        "all_students": generated_dataharu,
                        "student_list": non_generated,
                        "check_value": check_value,
                        "teacher_number": number,
                        "std_dataharu": std_dataharu,
                        "teacher_model": teacher_model,
                    },
                )
                return response
        return render(request, "loginTeacher.html")
            
    value = 0
    if request.method == "POST":
        email = request.POST.get("username")   
        passwo = request.POST.get("password")
        # check if user is real
        tempUsers = User.objects.filter(email__exact=email)
        if tempUsers.count() > 1:
            messages.error(request, "Multiple accounts found with this email. Please contact admin.")
            return render(request, "loginTeacher.html")
        elif not tempUsers.exists():
            messages.error(request, "You are not registered as a professor.")
            return render(request, "loginTeacher.html")
        else:
            tempUser = tempUsers.first()
            usern = tempUser.username
            user = authenticate(username=usern, password=passwo)
            if user is not None:
                print("user authenticated")
                login(request, user)
                full_name = request.user.get_full_name()
                x = full_name.split("/")
                unique = x[-1]
                print(x)
                print(f'Unique id {unique}')
                teacher_model = TeacherInfo.objects.get(unique_id=unique)
                generated_dataharu = Application.objects.filter(professor__unique_id=unique , is_generated=True)
                dataharu = Application.objects.filter(professor__unique_id=unique)
                number = len(dataharu)
                for data in dataharu:
                    if data.is_generated:
                        value += 1
                datakolength = len(dataharu)
                if datakolength == value:
                    check_value = True
                else:
                    check_value = False
                std_dataharu = serializers.serialize(
                    "json", Application.objects.filter(professor__unique_id=unique,is_generated=True)
                )
                non_generated = Application.objects.filter(
                    is_generated=False, professor__unique_id=unique
                )
                response = render(
                    request,
                    "Teacher.html",
                    {
                        "all_students": generated_dataharu,
                        "student_list": non_generated,
                        "check_value": check_value,
                        "teacher_number": number,
                        "std_dataharu": std_dataharu,
                        "teacher_model": teacher_model,
                    },
                )
                response.set_cookie("unique", unique)
                response.set_cookie("username", user.username)
                return response
            else:
                messages.error(request, "Sorry!  The Password doesnot match.")
                return render(request, "loginTeacher.html")
    



def logoutUser(request):
    logout(request)
    response = redirect("/")
    response.delete_cookie('unique')
    response.delete_cookie('csrftoken')
    response.delete_cookie('username')
    response.delete_cookie('OTP_value')
    return response

def logoutStudent(request):
    response = redirect("/")
    response.delete_cookie('student')
    return response

def forgotPassword(request):
    # generating otp so that it is generated only once
    OTP_value = OTP_generator(5)
    response = render(request, "forgotPassword.html")
    response.set_cookie("OTP_value", OTP_value)
    return response


def forgotUsername(request):
    # generating otp so that it is generated only once
    OTP_value = OTP_generator(5)
    response = render(request, "forgotUsername.html")
    response.set_cookie("OTP_value", OTP_value)
    return response


# check email of username is valid or not
def checkEmail(request):
    if request.method == "POST":

        email = request.POST.get("user_email")
        if User.objects.filter(email__exact=email).exists():
            user = User.objects.get(email__exact=email)
            send_mail(
                "UserName ",
                "Your username  is " + user.username,
                "christronaldo9090909@gmail.com",
                [email],
                fail_silently=False,
            )
            messages.success(request, "Username has been sent to your gmail.")
            return redirect("loginTeacher")
        else:
            messages.error(request, "Email is not registered.")
            return redirect("loginTeacher")
    return redirect("loginTeacher")


# OTP
def otp(request):

    if request.method == "POST":
        Usernaam = request.POST.get("username")
        if User.objects.filter(username=Usernaam).exists():
            sir = User.objects.get(username=Usernaam)
            full_name = sir.get_full_name()
            x = full_name.split("/")
            name = x[0]
            id = x[-1]

            if TeacherInfo.objects.filter(unique_id=id).exists():
                master = TeacherInfo.objects.get(unique_id=id)

                OTP_value = request.COOKIES.get("OTP_value")

                send_mail(
                    "OTP ",
                    "Your OTP for Recoomendation Letter is " + str(OTP_value),
                    "recoioe@gmail.com",
                    [master.email],
                    fail_silently=False,
                )

                response = render(
                    request,
                    "otp.html",
                    {"teacherkonam": master, "OTP_value": OTP_value},
                )
                # making cookies to store and send them to other view page

                response.set_cookie("teacher_ko_naam", master)
                response.set_cookie("teacher_ko_user", Usernaam)
                return response

            else:
                messages.error(request, "Sorry You are not registered as a Professor.")
                return render(request, "loginTeacher.html")

        else:
            messages.error(request, "Sorry You are not registered as a Professor.")
            return render(request, "loginTeacher.html")


# Otp check
def OTP_check(request):
    if request.method == "POST":
        user_OTP_value = request.POST.get("user_typed_OTP_value")

        # using cookies to obtain otp value and teacher
        OTP_value = request.COOKIES.get("OTP_value")
        teacher_ko_naam = request.COOKIES.get("teacher_ko_naam")

        if OTP_value == user_OTP_value:
            return render(
                request, "validatePassword.html", {"teacher_ko_naam": teacher_ko_naam}
            )
        else:
            messages.error(request, "Wrong OTP_value")
            return render(request, "loginTeacher.html")


# #to pass the username and to validate the user

# def validatePassword(request):
#     teacher_ko_naam=request.COOKIES.get('teacher_ko_naam')
#     OTP_value=request.COOKIES.get('OTP_value')
#     return render(request, 'validatePassword.html',{'teacher_ko_naam':teacher_ko_naam, 'OTP_value':OTP_value})


# pwd is changed of corresponding user passed from validatePassword
def changePassword(request):

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

    if password1 == password2:
        # Teacher ko Username using cookies from 'otp' view page
        teacher_ko_user_naam = request.COOKIES.get("teacher_ko_user")

        # changing Pwd
        usr = User.objects.get(username=teacher_ko_user_naam)
        usr.set_password(password1)
        usr.save()
        messages.success(request, "Password has been changed successfully.")
        return render(request, "loginTeacher.html")
    else:

        return render(request, "validatePassword.html")


def OTP_generator(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


# to pass message to admin user
def contact(request):

    return render(request, "contact.html")


def about(request):

    return render(request, "about.html")


def feedback(request):

    if request.method == "POST":
        First_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        feedback = request.POST.get("feedback")

        message = (
            str(First_name)+" " 
            + str(last_name)
            + "\n"
            + str(email)
            + "\n"
            + str(feedback)
        )

        mail_admins(
            "Feedback", message, fail_silently=False, connection=None, html_message=None
        )
        send_mail(
            "Reply From Recoomendation Letter Team",
            "Thank you for your feedback. We will get back to you soon.",
            " christronaldo9090909@gmail.com",
            [email],
            fail_silently=False,
        )
        messages.success(request, "Your message has been sent.")
        return render(request, "contact.html")


def userDetails(request):
    subject=[]
    naya_subjects=[]
    unique = request.COOKIES.get("unique")
   
    
    teacherkonam = TeacherInfo.objects.get(unique_id=unique)
    email = teacherkonam.email
    username = User.objects.get(email=email)
    subjects=teacherkonam.subjects.all()
    length = len(subjects)
    bisaya=Subject.objects.all()
    
    for i in bisaya:
        if i not in subjects:
            naya_subjects.append(i)
        else:
            subject.append(i)
    
    return render(
        request,
        "userDetails.html",
        {"teacher_username": username, "teacher": teacherkonam,'subjects':subject,'bisaya':bisaya, 'length':length},
    )
    
def studentDetails(request):
    student = request.COOKIES.get("student")
    if StudentLoginInfo.objects.filter(username__exact = student).exists():
        student = StudentLoginInfo.objects.get(username__exact = student)
        return render(
            request,
            "studentDetails.html",
            {"username": student.username,'roll':student.roll_number, 'department': student.department,'program': student.program,'gender': student.gender,
            'dob': student.dob},
        )
    else:
        return render(
            request,
            "studentDetails.html")
    
def profileUpdate(request):
    unique = request.COOKIES.get("unique")
    teacherkonam = TeacherInfo.objects.get(unique_id=unique)

    return render(request, "profileUpdate.html", {"teacher": teacherkonam})


def profileUpdateRequest(request):

    unique = request.COOKIES.get("unique")
    teacherkonam = TeacherInfo.objects.get(unique_id=unique)
    email = teacherkonam.email
    username = User.objects.get(email=email)

    if request.method == "POST":
        photo = request.FILES["file"]

        # TeacherInfo.objects.filter(unique_id=unique).update(images=photo)

        teacherkonam = TeacherInfo.objects.get(unique_id=unique)
        teacherkonam.images = photo
        teacherkonam.save()

    return render(request, "userDetails.html", {"teacher_username": username, "teacher": teacherkonam})


def changeUsername(request):
    if request.method == "POST":
        old_username = request.POST.get("old_username")
        new_username = request.POST.get("new_username")

        if User.objects.filter(username=old_username).exists():
            if User.objects.filter(username=new_username).exists():
                messages.error(request, "Username already exists.")
                return redirect(userDetails)

            user = User.objects.get(username=old_username)
            user.username = new_username
            user.save()
            messages.success(request, "Username has been changed successfully.")
            return redirect(loginTeacher)
        else:
            messages.error(request, "No such username exists. ")
    return redirect(userDetails)

def changeStudentName(request):
    if request.method == "POST":
        old_username = request.POST.get("old_username")
        new_username = request.POST.get("new_username")

        if StudentLoginInfo.objects.filter(username=old_username).exists():
            if StudentLoginInfo.objects.filter(username=new_username).exists():
                messages.error(request, "Student already exists.")
                return redirect(studentDetails)

            student = StudentLoginInfo.objects.get(username=old_username)
            student.username = new_username
            student.save()
            messages.success(request, "Your username has been changed successfully.")
            response = redirect(loginStudent)
            response.delete_cookie('student')
            return response
        else:
            messages.error(request, "No such student exists. ")
            return redirect(studentDetails)
    return redirect(studentDetails)


# to change the password of the corresponding user within website
@login_required(login_url="/loginTeacher")
def userPasswordChange(request):
    if request.method == "POST":
        typed_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # to obtain old password,
        user = User.objects.get(username=request.COOKIES.get("username"))
        current_password = request.user.password

        # confirming typed old password is true or not
        old_new_check = check_password(typed_password, current_password)
        if old_new_check:
            if new_password == confirm_password:
                user = User.objects.get(username=request.COOKIES.get("username"))
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password has been changed successfully.")
                return redirect(loginTeacher)
            else:
                messages.error(request, "Password does not match.")
                return redirect(userDetails)
        else:
            messages.error(request, "Old Password didnt match")
            return redirect(userDetails)

# to change the password of the corresponding student within website
@login_required(login_url="/loginStudent")
def studentPasswordChange(request):
    if request.method == "POST":
        typed_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # to obtain old password,
        student = StudentLoginInfo.objects.get(username=request.COOKIES.get("student"))
        current_password = student.password

        # confirming typed old password is true or not
        old_new_check = check_password(typed_password, current_password)
        if old_new_check:
            if new_password == confirm_password:
                student = StudentLoginInfo.objects.get(username=student)
                student.password = make_password(new_password)
                student.save()
                response = redirect(loginStudent)
                messages.success(request, "Password has been changed successfully.")
                response.delete_cookie('student')
                return response
            else:
                messages.error(request, "Passwords do not match.")
                return redirect(studentDetails)
        else:
            messages.error(request, "Old Password didn't match")
            return redirect(studentDetails)


def changeTitle(request):
    if request.method == "POST":
        new_title = request.POST.get("new_title")
        usernaam = request.COOKIES.get("username")

        user = User.objects.get(username=usernaam)
        full_name = user.get_full_name()
        x = full_name.split("/")

        unique = x[-1]

        if TeacherInfo.objects.filter(unique_id=unique).exists():
            teacher = TeacherInfo.objects.get(unique_id=unique)
            teacher.title = new_title
            teacher.save()

            messages.success(request, "Title has been changed successfully.")
            return redirect(userDetails)
        else:
            messages.error(request, "No such Teacher exists. ")
            return redirect(userDetails)

    return redirect(userDetails)


def changePhone(request):
    if request.method == "POST":
        new_phone = request.POST.get("new_phone")
        usernaam = request.COOKIES.get("username")

        user = User.objects.get(username=usernaam)
        full_name = user.get_full_name()
        x = full_name.split("/")

        unique = x[-1]

        if TeacherInfo.objects.filter(unique_id=unique).exists():
            teacher = TeacherInfo.objects.get(unique_id=unique)
            teacher.phone = new_phone
            teacher.save()

            messages.success(request, "Phone Number has been changed successfully.")
            return redirect(userDetails)
        else:
            messages.error(request, "No such Teacher exists. ")
            return redirect(userDetails)

    return redirect(userDetails)


def changeEmail(request):
    if request.method == "POST":
        new_email = request.POST.get("new_email")
        usernaam = request.COOKIES.get("username")

        user = User.objects.get(username=usernaam)
        full_name = user.get_full_name()
        x = full_name.split("/")

        unique = x[-1]

        if TeacherInfo.objects.filter(unique_id=unique).exists():
            teacher = TeacherInfo.objects.get(unique_id=unique)
            teacher.email = new_email
            teacher.save()

            user = User.objects.get(username=usernaam)
            user.email = new_email
            user.save()

            messages.success(request, "Email has been changed successfully.")
            return redirect(userDetails)
        else:
            messages.error(request, "No such Teacher exists. ")
            return redirect(userDetails)

    return redirect(userDetails)

def addSubjects(request):
    if request.method == "POST":
        subject= request.POST.get("subject")
        usernaam = request.COOKIES.get("username")

        user = User.objects.get(username=usernaam)
        full_name = user.get_full_name()
        x = full_name.split("/")

        unique = x[-1]
      
        if TeacherInfo.objects.filter(unique_id=unique).exists():
            teacher = TeacherInfo.objects.get(unique_id=unique)
            naya_subject=Subject.objects.get(name=subject)
            # to check if subject is in teacher model or not
            check=[]
            subjects=teacher.subjects.all()
            for i in subjects:
                check.append(i.name)
            
            if subject in check:
                messages.error(request, "Subject already exists.")
                return redirect(userDetails)
        
            else:
                teacher.subjects.add(naya_subject)
                messages.success(request, "Subject has been added successfully.")
                return redirect(userDetails)
        else:
            messages.error(request, "No such Subject exists. ")
            return redirect(userDetails)

    return redirect(userDetails)

def deleteSubjects(request):
   
    if request.method == "POST":
        subject= request.POST.get("subject")
        usernaam = request.COOKIES.get("username")

        unique = request.COOKIES.get("unique")
        if TeacherInfo.objects.filter(unique_id=unique).exists():
            teacher = TeacherInfo.objects.get(unique_id=unique)
            naya_subject=Subject.objects.get(sub_name=subject)

            # to check if subject is in teacher model or not
            check=[]
            subjects=teacher.subjects.all()
            for i in subjects:
                check.append(i.sub_name)
            if subject not in check:
               
                messages.error(request, "Subject does not exists.")
                return redirect(userDetails)
        
            else:
                teacher.subjects.remove(naya_subject)
                messages.success(request, "Subject has been removed successfully.")
                return redirect(userDetails)
        else:
            messages.error(request, "No such Subject exists. ")
            return redirect(userDetails)

    return redirect(userDetails)

# for dynamic dropdown of subjects
def getdetails(request):
    teacher_id = json.loads(request.GET.get("d_name"))
    result_set = []

    teacher = TeacherInfo.objects.get(unique_id=teacher_id)
    subjects = teacher.subjects.all()
    print(subjects)
    for subject in subjects:
        result_set.append({"subject_name": subject})
    return HttpResponse(
        json.dumps(result_set, indent=4, sort_keys=True, default=str),
        content_type="application/json",
    )


# edit letter of recommendation
def edit(request):
    if request.method == "POST":
        roll = request.POST.get("roll")
        unique = request.COOKIES.get("unique")

        presentation= request.POST.get('presentation')
        quality = request.POST.get('qual')

        leaders = request.POST.get('quality1')
        hardwork = request.POST.get('quality2')
        social = request.POST.get('quality3')
        teamwork = request.POST.get('quality4')
        friendly = request.POST.get('quality5')

        recommend = request.POST.get('recommend')

        info = Application.objects.get(std__roll_number=roll, professor__unique_id=unique)


        # qualities_info = Qualities(
        #     leadership = True if leaders == "on" else False,
        #     hardworking = True if hardwork == "on" else False,
        #     social = True if social == "on" else False,
        #     teamwork = True if teamwork == "on" else False,
        #     friendly =True if friendly == "on" else False,
        #     quality = quality,
        #     presentation = presentation,
        #     recommend = recommend,
        #     #extracirricular = extra,
        #     student = stu_info,
        # )
        # qualities_info.save(update_fields=["leadership", "hardworking", 
        # "social", "teamwork", "friendly", "quality", "presentation", "recommend" , "student"])

        Qualities.objects.filter(application  = info).update(leadership = True if leaders == "on" else False,
                                                            hardworking = True if hardwork == "on" else False,
                                                            social = True if social == "on" else False,
                                                            teamwork = True if teamwork == "on" else False,
                                                            friendly =True if friendly == "on" else False,
                                                            quality = quality,
                                                            presentation = presentation,
                                                            recommend = recommend,)


        # student = StudentData.objects.get(std__roll_number = roll)
        stu = StudentLoginInfo.objects.get(roll_number=roll)
        # print("STU NAME",stu.username)
        application = Application.objects.get(name=stu.username, professor__unique_id=unique)
        paper = Paper.objects.get(application = application )
        project = Project.objects.get(application = application)
        university = University.objects.get(application = application)
        quality = Qualities.objects.get(application = application)
        academics = Academics.objects.get(application = application)
        teacher_name = application.professor.name
        teacher_model = application.professor

        files = Files.objects.get(application = application)

        bisaya=application.subjects
        
        subjec=bisaya.split(',')
        subjects=subjec[:-1]
        subject=subjec[-1]

        #student firstname
        name = application.name
        fname = name.split(' ')
        firstname = fname[0]
        

        length=len(subjec)
        if length==1:
            value=True
        else:
            value=False

        return render(request, 
                        "test.html", 
                        {   'application':application,
                            'student': application.std,
                            'subjects':subjects,
                            'subject':subject,
                            'value':value , 
                            'firstname':firstname,
                            "paper": paper,
                            "project": project,
                            "university": university,
                            "quality": quality,
                            "academics": academics,
                            "teacher": teacher_model,
                            "files": files, 
                        }
                    )


def testing(request):
    if request.method == "POST":
        textarea = request.POST.get("textarea")
    return render(request, "testing.html", {"letter": textarea})


def teacher(request):
    value=0
   
    unique = request.COOKIES.get("unique")

    teacher_model = TeacherInfo.objects.get(unique_id=unique)
    # for loop launlaii 
    generated_dataharu = Application.objects.filter(professor__unique_id=unique , is_generated=True)

    dataharu = Application.objects.filter(professor__unique_id=unique)
    number = len(dataharu)
    # to check if there is request or not on teachers page
    for data in dataharu:
        if data.is_generated:
            value += 1
    datakolength = len(dataharu)
    if datakolength == value:
        check_value = True
    else:
        check_value = False
        # to convert database to json objects
    std_dataharu = serializers.serialize(
        "json", Application.objects.filter(professor__unique_id=unique,is_generated=True)
    )
    non_generated = Application.objects.filter(
        is_generated=False, professor__unique_id=unique
    )

    response = render(
        request,
        "Teacher.html",
        {
            "all_students": generated_dataharu,
            "student_list": non_generated,
            "check_value": check_value,
            "teacher_number": number,
            "std_dataharu": std_dataharu,
            "teacher_model": teacher_model,
        },
    )
    return response



def renderCustom(request):
    if request.method == "POST":
        from jinja2 import Template
        unique = request.COOKIES.get("unique")
        roll = request.POST.get("roll")
        presentation = request.POST.get('presentation')
        quality = request.POST.get('qual')
        leaders = request.POST.get('quality1')
        hardwork = request.POST.get('quality2')
        social = request.POST.get('quality3')
        teamwork = request.POST.get('quality4')
        friendly = request.POST.get('quality5')
        recommend = request.POST.get('recommend')
        template_name = request.POST.get('temp')
        info = Application.objects.get(professor__unique_id=unique , std__roll_number=roll)
        Qualities.objects.filter(application = info).update(
            leadership = True if leaders == "on" else False,
            hardworking = True if hardwork == "on" else False,
            social = True if social == "on" else False,
            teamwork = True if teamwork == "on" else False,
            friendly =True if friendly == "on" else False,
            quality = quality,
            presentation = presentation,
            recommend = recommend,)
        stu = StudentLoginInfo.objects.get(roll_number=roll)
        application = Application.objects.get(name=stu.username , professor__unique_id=unique)
        paper = Paper.objects.get(application = application )
        project = Project.objects.get(application = application)
        university = University.objects.get(application = application)
        quality = Qualities.objects.get(application = application)
        academics = Academics.objects.get(application = application)
        teacher_model = application.professor
        teacher_name = teacher_model.name
        files = Files.objects.get(application = application)
        bisaya = application.subjects
        subjec = bisaya.split(',')
        subjects = subjec[:-1]
        subject = subjec[-1]
        name = application.name
        fname = name.split(' ')
        firstname = fname[0]
        length = len(subjec)
        value = True if length == 1 else False
        # Template selection logic
        template_obj = None
        if template_name and template_name != 'default':
            template_obj = CustomTemplates.objects.filter(template_name=template_name, professor=teacher_model).first()
        if not template_obj:
            # Try to get a "Default" template for this professor
            template_obj = CustomTemplates.objects.filter(template_name__iexact='Default', professor=teacher_model).first()
        if not template_obj:
            # Fallback to a hardcoded default template
            default_template_content = """
To Whom It May Concern,\n\nI am delighted to write this letter of recommendation for {{ student.name }}, who has been a student in my {{ subjects|join(', ') }} class{{ 'es' if subjects|length > 1 else '' }} at IOE Pulchowk Campus.\n\n{% if student.gender == 'male' %}He{% elif student.gender == 'female' %}She{% else %}They{% endif %} has consistently demonstrated a high level of dedication and academic excellence.\n\n{% if academics.gpa %}With a GPA of {{ academics.gpa }}, {{ student.name }} ranks among the top students in the class.{% endif %}\n\n{% if project.supervised_project %}In addition to coursework, {{ student.name }} successfully completed the project titled \"{{ project.supervised_project }}\".{% endif %}\n\n{% if paper.paper_title %}{{ student.name }} has also contributed to research, co-authoring the paper \"{{ paper.paper_title }}\".{% endif %}\n\n{% if quality.extracirricular %}Beyond academics, {{ student.name }} has actively participated in extracurricular activities such as {{ quality.extracirricular }}.{% endif %}\n\n{% if quality.leadership %}{{ student.name }} has shown strong leadership skills.{% endif %}{% if quality.hardworking %} {{ student.name }} is known for a hardworking attitude.{% endif %}{% if quality.teamwork %} {{ student.name }} excels in teamwork and collaboration.{% endif %}\n\n{% if university.uni_name and university.program_applied %}I strongly recommend {{ student.name }} for the {{ university.program_applied }} program at {{ university.uni_name }}.{% else %}I strongly recommend {{ student.name }} for further studies and future endeavors.{% endif %}\n\nIf you require any further information, please feel free to contact me at {{ teacher.email }}.\n\nSincerely,\n{{ teacher.name }}\n{{ teacher.title }}\nIOE Pulchowk Campus\n"""
            jinja_template = Template(default_template_content)
        else:
            jinja_template = Template(template_obj.template)
        print("GOT TEMPLATE NAME", template_name)
        
        rendered_letter = jinja_template.render({
            'application':application,
            "student": application.std,
            'subjects': subjects,
            'subject': subject,
            'value': value,
            'firstname': firstname,
            "paper": paper,
            "project": project,
            "university": university,
            "quality": quality,
            "academics": academics,
            "teacher": teacher_model,
            "files": files,
        })
        print("Quality",quality.quality)
        return render(request, 'test2.html', {'letter': rendered_letter, 'student': application.std, 'template_name':template_name})


def template(request):
    if request.method == "GET":
        
        unique = request.COOKIES.get("unique")
        teacher = TeacherInfo.objects.get(unique_id=unique)

        return render(request, "customTemplate.html", {'professor':teacher})



def getTemplate(request):
    if request.method == "POST":
        content = request.POST.get("content")
        uid = request.POST.get("uid")
        name = request.POST.get("templateName")
        teacher = TeacherInfo.objects.get(unique_id= uid)
        print(content)
        content = content.replace('<p>&nbsp;</p>\n<p>&nbsp;</p>', '')
        content = content.replace('<p>&nbsp;</p>', '')

        # Replace various types of new lines between paragraphs with <br> tags
        content = content.replace('</p>\n<p>', '<br>')
        content = content.replace('</p>\r\n<p>', '<br>')
        content = content.replace('</p>\r<p>', '<br>')

        # Ensure every paragraph starts with <br>
        content = content.replace('<p>', '<p><br>')

        print(content)

        template = CustomTemplates(template_name =  name, template=content, professor = teacher)
        template.save()

        return render(request, "customTemplate.html", {'template':template})
    

def admin_login(request):
    try:
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect("adminDashboard")
        
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user_obj = User.objects.filter(username=username)

            if not user_obj.exists():
                messages.error(request, "User does not exist")
                return render(request, "adminLogin.html")
            
            print(f'username {username} password {password}')

            user_obj = authenticate(username=username, password=password)
            print(user_obj)


            if user_obj and user_obj.is_superuser:
                login(request, user_obj)
                messages.success(request, "Login successful")
                return redirect("adminDashboard")
            
            
            messages.info(request, "Invalid credentials")
            return redirect("loginAdmin")
        
        if request.method == "GET":
            return render (request, "adminLogin.html")
        
        return render(request, "adminLogin.html")
    
    except Exception as e:
        print(e)
        messages.error(request, "An error occured. Please try again.")
        return render(request, "adminLogin.html")
    

def generate_unique_id():
    return str(random.randint(10000, 99999))


def adminDashboard(request):
    if request.method == 'POST':
        form = TeacherInfoForm(request.POST, request.FILES)
        if form.is_valid():
            email = request.POST.get('email')
            if TeacherInfo.objects.filter(email=email).exists():
                messages.warning(request, 'Another teacher with the same email already exists.')
                return redirect('adminDashboard')
            
            unique_id = generate_unique_id()
            while TeacherInfo.objects.filter(unique_id=unique_id).exists():
                unique_id = generate_unique_id()
            
            teacher_info = form.save(commit=False)
            teacher_info.unique_id = unique_id
            teacher_info.save()


            # Check if other teacher has same email

            uname = teacher_info.name.lower().replace('dr. ', '').replace(' ', '') + "_" + unique_id
            # Create corresponding User with a password
            user = User.objects.create_user(
                username=uname,
                password=form.cleaned_data['password'],  # Password is taken from the cleaned data
                first_name=teacher_info.name,
                last_name= '/' + unique_id             # 78batch: seniors had made to input last name as /unique id
                                                        # so, we had to continue with this( lazy us). You guys can change it. 
                                                        # we leave this for you. Otherwise works completely fine. Better not touch it.
            )
            user.email = teacher_info.email
            user.save()
            
            # Save many-to-many relationships
            form.save_m2m()
            
            messages.success(request, 'Teacher added successfully!')
            send_mail('Account Created Successfully', f'Dear sir,\n  Your account has been created in Recommendation Letter Generator. Your username is {uname}. Please login to verify. If you get any problem please contact us.  \n Link: http://recommendation-generator.bct.itclub.pp.ua/  \n \nBest Regards, \nIoe Recommendation Letter Generator', 'ioerecoletter@gmail.com', [teacher_info.email], fail_silently=False)


            return redirect('adminDashboard')
        else:
            messages.error(request, 'An error occurred while adding the teacher. Please try again.')
            return redirect('adminDashboard')
    else:
        form = TeacherInfoForm()

    # Query departments and subjects for the form
    departments = Department.objects.all()
    subjects = Subject.objects.all()
    teachers = TeacherInfo.objects.all()
    
    # make username dic of all teachers
    teacher_usernames = {}
    for teacher in teachers:
        teacher_usernames[teacher.name] = f"{teacher.name.lower().replace('dr. ', '').replace(' ', '')}_{teacher.unique_id}"
    

#reverse the order of elements in the dict 
    reversed_teacher_usernames = OrderedDict(reversed(list(teacher_usernames.items())))

    return render(request, 'adminDashboard.html', {
        'form': form,
        'departments': departments,
        'subjects': subjects,
        'professors': reversed_teacher_usernames
    })
from .forms import TeacherInfoForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from docx import Document
from jinja2 import Template
import datetime
from fpdf import FPDF

from django.http import HttpResponse
from weasyprint import HTML
import datetime

@csrf_exempt
def download_letter(request):
    if request.method == 'POST':
        roll = request.POST.get('roll')
        file_format = request.POST.get('format')
        unique = request.COOKIES.get('unique')

        # Fetch your objects (Application, Paper, Project, etc.)
        application = Application.objects.get(std__roll_number=roll, professor__unique_id=unique)
        paper = Paper.objects.get(application=application)
        project = Project.objects.get(application=application)
        university = University.objects.get(application=application)
        quality = Qualities.objects.get(application=application)
        academics = Academics.objects.get(application=application)
        teacher_model = application.professor
        files = Files.objects.get(application=application)
        bisaya = application.subjects
        subjec = bisaya.split(',')
        subjects = subjec[:-1]
        subject = subjec[-1]
        name = application.name
        fname = name.split(' ')
        firstname = fname[0]
        length = len(subjec)
        value = True if length == 1 else False
        stu = StudentLoginInfo.objects.get(roll_number=roll)

        # Template selection
        template_name = request.POST.get('template_name', 'Default')
        template_obj = CustomTemplates.objects.filter(template_name=template_name, professor=teacher_model).first()
        if not template_obj:
            template_obj = CustomTemplates.objects.filter(template_name__iexact='Default', professor=teacher_model).first()

        default_template_content = """
        <p>To Whom It May Concern,</p>
        <p>I am delighted to write this letter of recommendation for {{ student.name }} ...</p>
        """
        jinja_template = Template(template_obj.template if template_obj else default_template_content)

        context = {
            "student": stu,
            "application": application,
            "subjects": subjects,
            "subject": subject,
            "value": value,
            "firstname": firstname,
            "paper": paper,
            "project": project,
            "university": university,
            "quality": quality,
            "academics": academics,
            "teacher": teacher_model,
            "files": files,
            "today": datetime.date.today().strftime("%B %d, %Y"),
        }

        rendered_letter = jinja_template.render(context)

        from bs4 import BeautifulSoup

        def html_to_docx_paragraphs(rendered_html):
            """
            Convert rendered HTML into a list of paragraphs suitable for python-docx.
            Preserves line breaks (<br>) and spacing/indentation at the start of lines.
            """
            soup = BeautifulSoup(rendered_html, 'html.parser')
            paragraphs = []

            # Iterate over <p> tags
            for p in soup.find_all('p'):
                lines = []
                for elem in p.descendants:
                    if elem.name == 'br':
                        lines.append('\n')
                    elif isinstance(elem, str):
                        lines.append(elem)
                text = ''.join(lines)
                # Split by line breaks inside <p> and preserve indentation
                for line in text.split('\n'):
                    if line.strip():  # Skip empty lines
                        paragraphs.append(line)

            # Fallback: if no <p> tags, treat all text as one block split by double newlines
            if not paragraphs:
                text = soup.get_text("\n")
                paragraphs = [t.strip() for t in text.split('\n\n') if t.strip()]

            return paragraphs



        if file_format == 'docx':
            from docx import Document
            doc = Document()
            paragraphs = html_to_docx_paragraphs(rendered_letter)

            for para in paragraphs:
                doc.add_paragraph(para)

            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename=Recommendation_{application.name}.docx'
            doc.save(response)
            return response

        # --- PDF export using WeasyPrint ---
        elif file_format == 'pdf':
            pdf_file = HTML(string=rendered_letter).write_pdf()
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename=Recommendation_{application.name}.pdf'
            return response

        else:
            return HttpResponse("Invalid format", status=400)



def registerProfessor(request):
    if request.method == 'POST':
        form = TeacherInfoForm(request.POST, request.FILES)
        if form.is_valid():
            teacher_info = form.save(commit=False)
            # Generate unique_id
            unique_id = str(random.randint(10000, 99999))
            while TeacherInfo.objects.filter(unique_id=unique_id).exists():
                unique_id = str(random.randint(10000, 99999))
            teacher_info.unique_id = unique_id
            teacher_info.save()
            form.save_m2m()
            # Create corresponding User
            uname = teacher_info.name.lower().replace('dr. ', '').replace(' ', '') + "_" + unique_id
            user = User.objects.create_user(
                username=uname,
                password=form.cleaned_data['password'],
                first_name=teacher_info.name,
                last_name='/' + unique_id,
                email=teacher_info.email
            )
            user.save()
            messages.success(request, 'Professor registered successfully! You can now log in.')
            return redirect('loginTeacher')
    else:
        form = TeacherInfoForm()
    return render(request, 'registerProfessor.html', {'form': form})

def add_default_template_to_all_professors():
    from home.models import TeacherInfo, CustomTemplates
    default_template_content = """
To Whom It May Concern,\n\nI am delighted to write this letter of recommendation for {{ student.name }}, who has been a student in my {{ subjects|join(', ') }} class{{ 'es' if subjects|length > 1 else '' }} at IOE Pulchowk Campus.\n\n{% if student.gender == 'male' %}He{% elif student.gender == 'female' %}She{% else %}They{% endif %} has consistently demonstrated a high level of dedication and academic excellence.\n\n{% if academics.gpa %}With a GPA of {{ academics.gpa }}, {{ student.name }} ranks among the top students in the class.{% endif %}\n\n{% if project.supervised_project %}In addition to coursework, {{ student.name }} successfully completed the project titled \"{{ project.supervised_project }}\".{% endif %}\n\n{% if paper.paper_title %}{{ student.name }} has also contributed to research, co-authoring the paper \"{{ paper.paper_title }}\".{% endif %}\n\n{% if quality.extracirricular %}Beyond academics, {{ student.name }} has actively participated in extracurricular activities such as {{ quality.extracirricular }}.{% endif %}\n\n{% if quality.leadership %}{{ student.name }} has shown strong leadership skills.{% endif %}{% if quality.hardworking %} {{ student.name }} is known for a hardworking attitude.{% endif %}{% if quality.teamwork %} {{ student.name }} excels in teamwork and collaboration.{% endif %}\n\n{% if university.uni_name and university.program_applied %}I strongly recommend {{ student.name }} for the {{ university.program_applied }} program at {{ university.uni_name }}.{% else %}I strongly recommend {{ student.name }} for further studies and future endeavors.{% endif %}\n\nIf you require any further information, please feel free to contact me at {{ teacher.email }}.\n\nSincerely,\n{{ teacher.name }}\n{{ teacher.title }}\nIOE Pulchowk Campus\n"""
    for prof in TeacherInfo.objects.all():
        if not CustomTemplates.objects.filter(professor=prof, template_name__iexact='Default').exists():
            CustomTemplates.objects.create(
                template_name="Default",
                template=default_template_content,
                professor=prof,
                is_default=True
            )