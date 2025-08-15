from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import main,registrationForm,insertVoterInfo,userLogin, adminLogin, set_from_button,admin_Verify,setElectionName,addNewParty,insertPartyDetails,insertElectionName, selectParty, user_Verify, selectCandidate,otp_verification_page,setOtpCount, generateReport,adminLogout,send_otp, verify_otp, verify_registration, deletePartyPage, deleteParty,resetPassword,forgotPassword,setNewPassword,verify_reset_otp

urlpatterns = [
    path('', main, name='home'),
    path('register/', registrationForm, name='register'),
    path('insertVoterInfo/',insertVoterInfo,name='insertVoterInfo'),
    path('vote_now/', userLogin, name='vote_now'),
    path('adminLogin/', adminLogin, name='adminLogin'),
    path('admin_Verify/',admin_Verify,name ='admin_Verify'),
    path('setElectionName/',setElectionName, name = 'selectElectionName'),
    path('addNewParty/',addNewParty,name='addNewParty'),
    path('insert_Party_Details/',insertPartyDetails,name='insertPartyDetails'),
    path('election_Name/',insertElectionName,name= 'election_Name'),
    path('select_Party/',selectParty,name='selectParty'),
    path('otp_Verification/',user_Verify, name = 'otp_Verification'),
    path('select_Candidate/',selectCandidate,name= 'select_Candidate'),
    path('setOtpCount/',setOtpCount,name='setOtpCount'),
    path('generateReport/', generateReport, name='generateReport'),
    path('adminLogout/',adminLogout,name='adminLogout'),
    path('navigate/<str:page_name>/', set_from_button, name='navigate'),  
    path("otp-verification/", otp_verification_page, name="otp_verification"),
    path("verify_registration/",verify_registration, name="verify_registration"),
    path('send_otp/', send_otp, name='send_otp'),
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('deletePartyPage/', deletePartyPage, name='deletePartyPage'),
    path('deleteParty/',deleteParty,name='deleteParty'),
    path('resetPassword/',resetPassword,name='resetPassword'),
    path('forgotPassword/',forgotPassword,name='forgotPassword'),
    path('verify_reset_otp/',verify_reset_otp,name='verify_reset_otp'),
    path('setNewPassword/',setNewPassword,name='setNewPassword'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
