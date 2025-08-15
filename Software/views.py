from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Voter
from .models import Admin
from .models import Party
from .models import Elec_Name
from .models import Elec_Results
import os
from django.http import FileResponse
from reportlab.pdfgen import canvas
from collections import Counter
from django.core.mail import send_mail
from django.contrib.auth.models import User
# from .models import OTP
import random
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)

def main(request):
    # Reset session keys for navigation protection
    request.session['from_button'] = False
    details = Elec_Name.objects.all()
    return render(request,'Main_1.0.html',{'details':details})

def registrationForm(request):
    # Allow access only if coming from the button click
    if request.session.get('from_button', False):
        request.session['from_button'] = False  # Reset after access
        return render(request, 'registrationForm_1.0.html')
    else:
        return HttpResponseForbidden("You cannot access this page directly.")
    
def insertVoterInfo(request):
    nic= request.POST['NIC'];
    fName=request.POST['firstName'];
    mName=request.POST['middleName'];
    lName=request.POST['lastName'];
    phoneNo=request.POST['phoneNo'];
    email = request.POST['email'];
    address=request.POST['address'];
    uName=request.POST['userName'];
    pWord=request.POST['password'];
    
    if Voter.objects.filter(NIC_Number=nic).exists(): 
        messages.error(request,"Given NIC number is already exists.")
        return render(request, 'registrationForm_1.0.html')
    elif Voter.objects.filter(Email=email).exists():
        messages.error(request,"Given e-mail address is already exists.")
        return render(request, 'registrationForm_1.0.html')
    else:
        request.session['nic'] = nic
        request.session['fName'] = fName
        request.session['mName'] = mName
        request.session['lName'] = lName
        request.session['phoneNo'] = phoneNo
        request.session['email'] = email
        request.session['address'] = address
        request.session['uName'] = uName
        request.session['pWord'] = pWord
        

        messages.success(request, "Please enter the 6-digit OTP sent to your e-mail address for complete registration.")
        return send_regisration_otp(request)
    
def userLogin(request):
    # Allow access only if coming from the button click
    if request.session.get('from_button', False):
        request.session['from_button'] = False  
        return render(request, 'userLogin_.html')
    else:
        return HttpResponseForbidden("You cannot access this page directly.")
    
def user_Verify(request):
    # global uName
    uName = request.POST.get('username');
    uPWord = request.POST.get('password');
    request.session['uName'] = uName

    filtered_user = Voter.objects.filter(User_Name=uName)

    if filtered_user.exists():
        user = filtered_user.first()
        if (uPWord == user.Password): 
            if user.OTP_Count >=1:
             # Secure password verification
                messages.success(request, "User identified successfully! Please enter the 6-digit OTP sent to your e-mail address for verification.")
                return send_otp(request)
            else:
                messages.error(request, "You have already voted for this election!.")
                return main(request)
        else:
            # return HttpResponse("Invalid password.")
           messages.error(request, "Invalid password.")
           return render(request,'userLogin_.html')
    else:
        # return HttpResponse("User not found.")
        messages.error(request, "User not found!")
        return render(request,'userLogin_.html')

def resetPassword(request):
    # global uName
    u_Name = request.POST.get('userName');
    u_NIC = int(request.POST.get('NIC'));
    u_Email =  request.POST.get('email');

    request.session['uName'] = u_Name

    filtered_user = Voter.objects.filter(User_Name=u_Name)

    if filtered_user.exists():
        user = filtered_user.first()
        uOtpCount = user.OTP_Count
        
        if (u_NIC == int(user.NIC_Number)) :
            if (u_Email == user.Email): 
                messages.success(request, "User identified successfully! Please enter the 6-digit OTP sent to your e-mail address for verification.")
                record = Voter.objects.get(Email = u_Email)

                record.OTP_Count = uOtpCount+1
                record.save()

                return send_otp_for_resetPW(request)
        else:
           
           messages.error(request, "Invalid Request.")
           return render(request,'userLogin_.html')
    else:
        # return HttpResponse("User not found.")
        messages.error(request, "User not found!")
        return render(request,'userLogin_.html')

def forgotPassword(request):
        return render(request, 'resetPassword.html')

# def send_otp(request):
#     uName = request.session.get('uName')
#     filtered_user = Voter.objects.filter(User_Name=uName)
#     if filtered_user.exists():
#         user = filtered_user.first()
#         uEmail = user.Email
#         uOtpCount = user.OTP_Count
#         user = User.objects.filter(email=uEmail).first()
#         global otp_code
#         otp_code = str(random.randint(100000, 999999))
#         request.session['otp_code']= otp_code
#         # 
#         subject = "E-Voting System - Verification OTP"
#         message = f"""
#         Dear User,

#         Thank you for using our E-Voting System. To complete your verification, please use the OTP code below:

#         🔹 **Your OTP Code:** {otp_code}

#         This OTP is valid for a limited time. Please do not share it with anyone for security reasons.

#         If you did not request this OTP, please ignore this email.

#         Best regards,  
#         **E-Voting System Team**
#         """
#         sender_email = "your_email@gmail.com"
        
#         send_mail(subject, message, sender_email, [uEmail], fail_silently=False)
#         record = Voter.objects.get(Email = uEmail)
#         record.OTP_Count = uOtpCount-1
#         record.save()

#         return render(request, "OTP_Verification_1.0.html")
    
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_otp(request):

    uName = request.session.get('uName')
    filtered_user = Voter.objects.filter(User_Name=uName)
    if filtered_user.exists():
        user = filtered_user.first()
        uEmail = user.Email
        uOtpCount = user.OTP_Count
        user = User.objects.filter(email=uEmail).first()
        global otp_code
        otp_code = str(random.randint(100000, 999999))
        request.session['otp_code']= otp_code

    subject = 'Your OTP Code for E-Voting Verification'
    from_email = 'capstonept01@gmail.com'
    to = [uEmail]

    html_content = render_to_string('emails/otp_email.html', {'otp_code': otp_code})
    text_content = f"Your OTP Code: {otp_code}\nDo not share this code with anyone."

    email = EmailMultiAlternatives(subject, text_content, from_email, to)
    email.attach_alternative(html_content, "text/html")
    email.send()

    record = Voter.objects.get(Email = uEmail)
    record.OTP_Count = uOtpCount-1
    record.save()

    return render(request, "OTP_Verification_1.0.html")


# def send_otp_for_resetPW(request):
#     uName = request.session.get('uName')
#     filtered_user = Voter.objects.filter(User_Name=uName)
#     if filtered_user.exists():
#         user = filtered_user.first()
#         uEmail = user.Email
#         uOtpCount = user.OTP_Count
#         user = User.objects.filter(email=uEmail).first()
#         global otp_code
#         otp_code = str(random.randint(100000, 999999))
#         request.session['otp_code']= otp_code
#         # 
#         subject = "E-Voting System - Verification OTP"
#         message = f"""
#         Dear User,

#         Thank you for using our E-Voting System. To complete your verification, please use the OTP code below:

#         🔹 **Your OTP Code:** {otp_code}

#         This OTP is valid for a limited time. Please do not share it with anyone for security reasons.

#         If you did not request this OTP, please ignore this email.

#         Best regards,  
#         **E-Voting System Team**
#         """
#         sender_email = "your_email@gmail.com"
        
#         send_mail(subject, message, sender_email, [uEmail], fail_silently=False)
#         record = Voter.objects.get(Email = uEmail)
#         record.OTP_Count = uOtpCount-1
#         record.save()

#         return render(request, "OTP_Verification_1.2.html")

def send_otp_for_resetPW(request):   
    uName = request.session.get('uName')
    filtered_user = Voter.objects.filter(User_Name=uName)
    if filtered_user.exists():
        user = filtered_user.first()
        uEmail = user.Email
        uOtpCount = user.OTP_Count
        user = User.objects.filter(email=uEmail).first()
        global otp_code
        otp_code = str(random.randint(100000, 999999))
        request.session['otp_code']= otp_code

    subject = 'Your OTP Code for E-Voting Verification'
    from_email = 'capstonept01@gmail.com'
    to = [uEmail]

    html_content = render_to_string('emails/otp_email.html', {'otp_code': otp_code})
    text_content = f"Your OTP Code: {otp_code}\nDo not share this code with anyone."

    email = EmailMultiAlternatives(subject, text_content, from_email, to)
    email.attach_alternative(html_content, "text/html")
    email.send()

    record = Voter.objects.get(Email = uEmail)
    record.OTP_Count = uOtpCount-1
    record.save()

    return render(request, "OTP_Verification_1.2.html")

# def send_regisration_otp(request):
#         email = request.POST['email'];
#         otp_code = str(random.randint(100000, 999999))
#         request.session['otp_code']= otp_code
#         # 
#         subject = "E-Voting System - Verification OTP"
#         message = f"""
#         Dear User,

#         Thank you for registration to our E-Voting System. To complete your verification, please use the OTP code below:

#         🔹 **Your OTP Code:** {otp_code}

#         This OTP is valid for a limited time. Please do not share it with anyone for security reasons.

#         If you did not request this OTP, please ignore this email.

#         Best regards,  
#         **E-Voting System Team**
#         """
#         sender_email = "your_email@gmail.com"
        
#         send_mail(subject, message, sender_email, [email], fail_silently=False)
        

#         return render(request, "OTP_Verification_1.1.html")

def send_regisration_otp(request):  
    email = request.POST['email'];
    otp_code = str(random.randint(100000, 999999))
    request.session['otp_code']= otp_code

    subject = 'Your OTP Code for E-Voting Verification'
    from_email = 'capstonept01@gmail.com'
    to = [email]

    html_content = render_to_string('emails/otp_email.html', {'otp_code': otp_code})
    text_content = f"Your OTP Code: {otp_code}\nDo not share this code with anyone."

    email = EmailMultiAlternatives(subject, text_content, from_email, to)
    email.attach_alternative(html_content, "text/html")
    email.send()

    return render(request, "OTP_Verification_1.1.html")

def verify_registration(request):
    otp_code = request.session.get('otp_code')
    inputOTP = request.POST['otp'];

    if inputOTP == otp_code :
        messages.success(request,"OTP Verified Successfully!")
        nic= request.session.get('nic')
        fName=request.session.get('fName')
        mName=request.session.get('mName')
        lName=request.session.get('lName')
        phoneNo=request.session.get('phoneNo')
        email = request.session.get('email')
        address=request.session.get('address')
        uName=request.session.get('uName')
        pWord=request.session.get('pWord')

        voterDetails=Voter(NIC_Number=nic,First_Name = fName ,Last_Name = lName , Middle_Name = mName ,Phone_Number = phoneNo, Email =email, Address = address, User_Name = uName, Password = pWord);
        voterDetails.save();
        return main(request) 
    else:
        messages.error(request,"Registration failed!...Invalid OTP!...")
        return main(request) 
          
def verify_otp(request):
    otp_code = request.session.get('otp_code')
    inputOTP = request.POST['otp'];
    print(otp_code)
    print(inputOTP)

    uName = request.session.get('uName')
    filtered_user = Voter.objects.filter(User_Name=uName)
    user = filtered_user.first()
    uEmail = user.Email
    uOtpCount = user.OTP_Count

    if inputOTP == otp_code :
        messages.success(request,"OTP Verified Successfully!")
        return selectParty(request) 
    else:
        messages.error(request,"Invalid OTP!")

        record = Voter.objects.get(Email = uEmail)
        record.OTP_Count = uOtpCount+1
        record.save()
        return main(request)

def verify_reset_otp(request):
    otp_code = request.session.get('otp_code');
    inputOTP = request.POST['otp'];

    if (otp_code == inputOTP):
        messages.success(request,"User verified Successfully!")
        return render(request, "setNewPassword.html")
    else:
         messages.error(request,"Invalid OTP!")
         return main(request)

def setNewPassword(request):
    uName = request.session.get('uName')
    pWord = request.POST['password'];

    record = Voter.objects.get(User_Name = uName)

    record.Password = pWord
    record.save()
    messages.success(request,"Password reset successfully!")
    return main(request)


def adminLogin(request):
    
    # Allow access only if coming from the button click
    if request.session.get('from_button', False):
        request.session['from_button'] = False  
        return render(request, 'adminLogin.html')
    else:
        return HttpResponseForbidden("You cannot access this page directly.")
    
def admin_Verify(request):
    aName = request.POST['username'];
    aPWord = request.POST['password'];

    filtered_admin = Admin.objects.filter(Admin_name=aName)
 
    if filtered_admin.exists():
        admin = filtered_admin.first()
        if admin.Admin_password == aPWord: 
            return render(request, 'adminInterface.html')
        else:
            messages.error(request, "Invalid password.")
            return render(request,'adminLogin.html')
    else:
        messages.error(request, "Invalid password.")
        return render(request,'adminLogin.html')
    
def setElectionName(request):
    # Allow access only if coming from the button click
    if request.session.get('from_button', False):
        request.session['from_button'] = False  # Reset after access
        return render(request, 'selectElectionName.html')
    else:
        return HttpResponseForbidden("You cannot access this page directly.")

def addNewParty(request):
    # Allow access only if coming from the button click
    if request.session.get('from_button', False):
        request.session['from_button'] = False  # Reset after access
        return render(request, 'addNewParty.html')
    else:
        return HttpResponseForbidden("You cannot access this page directly.")
    
def deletePartyPage(request):
    politicalParties = Party.objects.all()
    if request.session.get('from_button', False):
        request.session['from_button'] = False  # Reset after access
        return render(request, 'deleteParty_1.0.html',{'politicalParties':politicalParties})
    else:
        return HttpResponseForbidden("You cannot access this page directly.")
    
def deleteParty(request):
    partyName = request.POST.get("partyName")
    filtered_party = Party.objects.filter(Party_Name=partyName)
    filtered_party.delete()
    messages.success(request, "Party Deleted Successfully!.")
    return render(request,'adminInterface.html')
    
def selectParty(request):
    # request.session['from_button'] = False
    politicalParties = Party.objects.all()
    return render(request,'partySelection_2.0.html',{'politicalParties':politicalParties})
    

def selectCandidate(request):
    
    if request.method == "POST":
        selected_party = request.POST.get("flexRadioDefault")
        
        if selected_party: 
            global partyR
            partyR = selected_party    
            return render(request, 'selectCandidate_1.0.html')
    
        selected_choices = request.POST.getlist("choices")

        if len(selected_choices) > 3:
            messages.error(request," You can only select a maximum of 3 choices.")
            return render(request, 'selectCandidate_1.0.html')

        Vote1 = selected_choices[0] if len(selected_choices) > 0 else None
        Vote2 = selected_choices[1] if len(selected_choices) > 1 else None
        Vote3 = selected_choices[2] if len(selected_choices) > 2 else None
        
        submitVote = Elec_Results(Political_Party = partyR, First_Vote =Vote1, Second_Vote = Vote2, Third_Vote=Vote3);
        submitVote.save();
        
        messages.success(request,"Your vote was subbmitted successfully!")
        return main(request)
    
def insertPartyDetails(request):
    
    pName= request.POST['partyName'];
    pLogo=request.FILES.get('partyLogo');
    pColor=request.POST['partyColor'];
    LogoName = pName
    image_path = os.path.join(settings.BASE_DIR, 'media', LogoName)
    with open(image_path, 'wb+') as destination:
                for chunk in pLogo.chunks():
                    destination.write(chunk)

    partyDetails=Party(Party_Name = pName,Party_Logo = LogoName , Party_Color = pColor);
    partyDetails.save();
    return render(request, 'adminInterface.html')


def insertElectionName(request):
    if Elec_Name.objects.filter(Election_ID=1).exists():
        eName = request.POST['eName'];
        eYear = request.POST['eYear'];
        eMonth = request.POST['eMonth'];
        Elec_Name.objects.filter(Election_ID=1).update(Election_Name=eName)
        Elec_Name.objects.filter(Election_ID=1).update(Election_Year=eYear)
        Elec_Name.objects.filter(Election_ID=1).update(Election_Month=eMonth)
    else:
        eName = request.POST['eName'];
        eYear = request.POST['eYear'];
        eMonth = request.POST['eMonth'];
        Name = Elec_Name(Election_Name = eName,Election_Year = eYear, Election_Month=eMonth);      
        Name.save()
    return render(request, 'adminInterface.html')


def setOtpCount(request):
    messages.success(request,"OTP count has been reset successfully!")
    Voter.objects.update(OTP_Count = 1)
    Elec_Results.objects.all().delete()
    return render(request, 'adminInterface.html')

from reportlab.lib.colors import navy
from reportlab.lib.colors import black


def generateReport(request):
    parties = Party.objects.values_list('Party_Name',flat=True)
    IDsOfParties = Party.objects.values_list('Party_ID')

    votes = list(Elec_Results.objects.values_list('Vote_ID','Political_Party','First_Vote','Second_Vote','Third_Vote'))
    partyResults ={}
    candidateResults = {}

    for party in parties:
        partyVotes = 0
        for vote in votes :
            if  party == vote[1]:
                partyVotes += 1 
        partyResults.update({f"{party}":f"{partyVotes}"})

    
    for party in parties:
        partyVotes =0
        votedNumbers =[]
        for vote in votes:
            if  party == vote[1]:
                partyVotes += 1
                votedNumbers.append(vote[2])
                votedNumbers.append(vote[3])
                votedNumbers.append(vote[4])
        
        count = Counter(votedNumbers)
        sortedCount ={k: v for k, v in sorted(count.items(), key = lambda ele: ele[1])}
        candidateResults.update({party:sortedCount})

    sortedPartyResults = {k: v for k, v in sorted(partyResults.items(), key = lambda ele: ele[1])}

                
    file_path = "generated_report.pdf"  
    eName = Elec_Name.objects.values_list('Election_Name',flat=True)
    eYear = Elec_Name.objects.values_list('Election_Year',flat = True)
    # Create a new PDF file using `with open()`
    with open(file_path, "wb") as pdf_file:
        pdf = canvas.Canvas(pdf_file)
        pdf.setFont("Helvetica-Bold", 25)
        pdf.setFillColor(navy)
        pdf.drawCentredString(300, 800, f"The results sheet")  
        pdf.drawCentredString(300, 770, f"of")
        pdf.drawCentredString(300, 740, f"{eName[0]}")
        pdf.drawCentredString(300, 710, f"{eYear[0]}")
        pdf.setFont("Helvetica-Bold", 20)
        pdf.setFillColor(black)
        pdf.drawString(50, 660, "Overall results of political parties : ")
        j=1
        i=630
        pdf.setFont("Helvetica-Bold", 14)
        for key, value in sortedPartyResults.items():           
            pdf.drawString(80, i, f"{j}) {key} - {value}")
            i-=20
            j+=1
        
        pdf.showPage()
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(50, 800, "Overall results of candidates : ")
        i=760
        j=1
        k=1
        for party, candidate_dict in candidateResults.items():
                pdf.setFont("Helvetica-Bold", 16)
                pdf.drawString(80, i, f"{k}) {party}")              
                i-=30
                j=1

                for key, value in candidate_dict.items():
                    pdf.setFont("Helvetica-Bold", 14)         
                    pdf.drawString(110, i, f"{j}) {key} - {value}")
                    i-=20
                    j+=1
                k+=1
                
        pdf.save()

    # Return the file as a response so the user can download it
    response = FileResponse(open(file_path, "rb"), as_attachment=True)
    return response    

def adminLogout(request):
    if request.session.get('from_button', False):
        request.session['from_button'] = False  
        return main(request)
    else:
        return HttpResponseForbidden("You cannot access this page directly.")    
    
def set_from_button(request, page_name):
    # Set session key when button is clicked
    request.session['from_button'] = True
    if page_name == "register":
        return redirect('register')
    elif page_name == "vote_now":
        return redirect('vote_now')
    elif page_name == "adminLogin":
        return redirect('adminLogin')
    elif page_name=="otp_Verification":
        return redirect('otp_Verification')
    elif page_name=="selectElectionName":
        return redirect('selectElectionName')
    elif page_name=="addNewParty":
        return redirect('addNewParty')
    elif page_name=="elecName":
        return redirect('elecName')  
    elif page_name=="setOtpCount":
        return redirect('setOtpCount')
    elif page_name=="generateReport":
        return redirect('generateReport')
    elif page_name=="deletePartyPage":
        return redirect('deletePartyPage')
    elif page_name=="adminLogout":
        return redirect('adminLogout')
    else:
        return HttpResponseForbidden("Invalid page request.")

def otp_verification_page(request):
    return render(request, "otp_verification.html")

