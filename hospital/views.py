from django.shortcuts import get_object_or_404, render,redirect,reverse
from . import forms,models
from django.contrib import messages
from django.db.models import Sum, Q, Prefetch
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.conf import settings
from django.db.models import Q
from .forms import HealthResourceForm, PharmacyForm, PrescriptionForm, InsuranceForm, DoctorProfileForm
from .models import HealthResource, Pharmacy, Prescription, Insurance

# Create your views here.
def home_view(request):
    
    return render(request,'hospital/index.html')


#for showing signup/login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/adminclick.html')


#for showing signup/login button for doctor(by sumit)
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/doctorclick.html')


#for showing signup/login button for patient(by sumit)
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'hospital/patientclick.html')



def admin_signup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect('adminlogin')
    return render(request,'hospital/adminsignup.html',{'form':form})



def doctor_signup_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST,request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.save()
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)
        return HttpResponseRedirect('doctorlogin')
    return render(request,'hospital/doctorsignup.html',context=mydict)


def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.status=False
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'hospital/patientsignup.html',context=mydict)






#-----------for checking user is doctor , patient or admin(by sumit)
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()
def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval=models.Doctor.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request,'hospital/index.html')
    elif is_patient(request.user):
        accountapproval=models.Patient.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('patient-dashboard')
        else:
            return render(request,'hospital/index.html')
    
    return render(request,'hospital/index.html')










#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    #for both table in admin dashboard
    doctors=models.Doctor.objects.all().order_by('-id')
    patients=models.Patient.objects.all().order_by('-id')
    #for three cards
    doctorcount=models.Doctor.objects.all().filter(status=True).count()
    pendingdoctorcount=models.Doctor.objects.all().filter(status=False).count()

    patientcount=models.Patient.objects.all().filter(status=True).count()
    pendingpatientcount=models.Patient.objects.all().filter(status=False).count()

    appointmentcount=models.Appointment.objects.all().filter(status=True).count()
    pendingappointmentcount=models.Appointment.objects.all().filter(status=False).count()
    mydict={
    'doctors':doctors,
    'patients':patients,
    'doctorcount':doctorcount,
    'pendingdoctorcount':pendingdoctorcount,
    'patientcount':patientcount,
    'pendingpatientcount':pendingpatientcount,
    'appointmentcount':appointmentcount,
    'pendingappointmentcount':pendingappointmentcount,
    }
    return render(request,'hospital/admin_dashboard.html',context=mydict)


# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request,'hospital/admin_doctor.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)

    userForm=forms.DoctorUserForm(instance=user)
    doctorForm=forms.DoctorForm(request.FILES,instance=doctor)
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST,instance=user)
        doctorForm=forms.DoctorForm(request.POST,request.FILES,instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            doctor=doctorForm.save(commit=False)
            doctor.status=True
            doctor.save()
            return redirect('admin-view-doctor')
    return render(request,'hospital/admin_update_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_doctor_view(request):
    userForm=forms.DoctorUserForm()
    doctorForm=forms.DoctorForm()
    mydict={'userForm':userForm,'doctorForm':doctorForm}
    if request.method=='POST':
        userForm=forms.DoctorUserForm(request.POST)
        doctorForm=forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            doctor=doctorForm.save(commit=False)
            doctor.user=user
            doctor.status=True
            doctor.save()

            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-doctor')
    return render(request,'hospital/admin_add_doctor.html',context=mydict)




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Doctor.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_doctor.html',{'doctors':doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'hospital/admin_view_doctor_specialisation.html',{'doctors':doctors})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request,'hospital/admin_patient.html')




@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients = models.Patient.objects.filter(status=True).order_by('-id')

    for patient in patients:
        # Find the doctor from the most recent appointment
        last_appointment = models.Appointment.objects.filter(patientId=patient, status=True).order_by('-appointment_date', '-appointment_time').first()
        if last_appointment and last_appointment.doctorId:
            patient.assigned_doctor_name = last_appointment.doctorName
        elif patient.assignedDoctorId:
            # Fallback to the manually assigned doctor if no appointments
            doctor_user = models.User.objects.filter(id=patient.assignedDoctorId).first()
            patient.assigned_doctor_name = doctor_user.get_full_name() if doctor_user else "Not Assigned"
    return render(request, 'hospital/admin_view_patient.html', {'patients': patients})





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)

    if request.method=='POST':
        userForm = forms.PatientUserForm(request.POST, instance=user)
        patientUpdateForm = forms.PatientUpdateForm(request.POST, request.FILES, instance=patient)
        if userForm.is_valid() and patientUpdateForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientUpdateForm.save()
            return redirect('admin-view-patient')
    else:
        userForm=forms.PatientUserForm(instance=user)
        patientUpdateForm=forms.PatientUpdateForm(instance=patient)
        
    mydict={'userForm':userForm,'patientForm':patientUpdateForm}
    return render(request,'hospital/admin_update_patient.html',context=mydict)





@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_patient_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()

            patient=patientForm.save(commit=False)
            patient.user=user
            patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

        return HttpResponseRedirect('admin-view-patient')
    return render(request,'hospital/admin_add_patient.html',context=mydict)



#------------------FOR APPROVING PATIENT BY ADMIN----------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=models.Patient.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_patient.html',{'patients':patients})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')



#--------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients = models.Patient.objects.all().filter(status=True)
    # Get IDs of patients who have paid
    paid_patient_ids = models.PatientDischargeDetails.objects.filter(payment_status=True).values_list('patient_id', flat=True)
    patient_data = []
    for patient in patients:
        # Check if the patient's ID is in the list of paid patient IDs
        is_discharged_and_paid = patient.id in paid_patient_ids
        patient_data.append({'patient': patient, 'is_discharged': is_discharged_and_paid})
    return render(request, 'hospital/admin_discharge_patient.html', {'patient_data': patient_data})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    # Handle case where admitDate might be None
    if patient.admitDate:
        days=(date.today()-patient.admitDate) #2 days, 0:00:00
        d = days.days
        if d == 0: # If admitted and discharged on the same day, count as 1 day
            d = 1
    else:
        d=0

    # Find the doctor from the most recent appointment for this patient
    last_appointment = models.Appointment.objects.filter(patientId=patient, status=True).order_by('-appointment_date', '-appointment_time').first()
    assigned_doctor_name = "Not Assigned"
    if last_appointment and last_appointment.doctorId:
        assigned_doctor_name = last_appointment.doctorName
    elif patient.assignedDoctorId:
        try:
            assigned_doctor_user = models.User.objects.get(id=patient.assignedDoctorId)
            assigned_doctor_name = assigned_doctor_user.get_full_name()
        except models.User.DoesNotExist:
            pass # Keep "Not Assigned"

    try:
        insurance = models.Insurance.objects.get(patient=patient)
    except models.Insurance.DoesNotExist:
        insurance = None

    patientDict={
        'patientId':pk,
        'name':patient.get_name,
        'mobile':patient.mobile,
        'address':patient.address,
        'symptoms':patient.symptoms,
        'admitDate':patient.admitDate or date.today(),
        'todayDate':date.today(),
        'day':d,
        'assignedDoctorName':assigned_doctor_name,
        'insurance': insurance,
    }
    if request.method == 'POST':
        feeDict ={
            'roomCharge':int(request.POST['roomCharge'])*int(d),
            'doctorFee':request.POST['doctorFee'],
            'medicineCost' : request.POST['medicineCost'],
            'OtherCharge' : request.POST['OtherCharge'],
            'total':(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)

        if insurance:
            insured_amount = patientDict['total'] * 0.8
            out_of_pocket = patientDict['total'] - insured_amount
            patientDict['insured_amount'] = insured_amount
            patientDict['out_of_pocket'] = out_of_pocket

        #for updating to database patientDischargeDetails (pDD)
        pDD=models.PatientDischargeDetails()
        pDD.patient=patient
        pDD.patientName=patient.get_name
        pDD.assignedDoctorName=assigned_doctor_name
        pDD.address=patient.address
        pDD.mobile=patient.mobile
        pDD.symptoms=patient.symptoms
        pDD.admitDate=patient.admitDate or date.today()
        pDD.releaseDate=date.today()
        pDD.daySpent=int(d)
        pDD.medicineCost=int(request.POST['medicineCost'])
        pDD.roomCharge=int(request.POST['roomCharge'])*int(d)
        pDD.doctorFee=int(request.POST['doctorFee'])
        pDD.OtherCharge=int(request.POST['OtherCharge'])
        pDD.total=(int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request,'hospital/patient_final_bill.html',context=patientDict)
    return render(request,'hospital/patient_generate_bill.html',context=patientDict)


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_insurance_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    try:
        insurance = models.Insurance.objects.get(patient=patient)
    except models.Insurance.DoesNotExist:
        insurance = None
    return render(request, 'hospital/patient_insurance.html', {'insurance': insurance, 'patient': patient})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def add_insurance_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    form = forms.InsuranceForm()
    if request.method == 'POST':
        form = forms.InsuranceForm(request.POST)
        if form.is_valid():
            insurance = form.save(commit=False)
            insurance.patient = patient
            insurance.save()
            return redirect('patient-insurance')
    return render(request, 'hospital/add_insurance.html', {'form': form, 'patient': patient})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def update_insurance_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    insurance = models.Insurance.objects.get(patient=patient)
    form = forms.InsuranceForm(instance=insurance)
    if request.method == 'POST':
        form = forms.InsuranceForm(request.POST, instance=insurance)
        if form.is_valid():
            form.save()
            return redirect('patient-insurance')
    return render(request, 'hospital/update_insurance.html', {'form': form})

#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return


def download_pdf_view(request,pk):
    dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patient_id=pk).order_by('-id')[:1][0]
    patient = models.Patient.objects.get(id=pk)
    insurance = models.Insurance.objects.filter(patient=patient).first()

    total = dischargeDetails.total
    insurance_coverage = 0
    final_bill = total

    if insurance:
        # Assuming a fixed 80% coverage for demonstration
        insurance_coverage = total * 0.80
        final_bill = total - insurance_coverage

    dict={
        'patientName':dischargeDetails.patientName,
        'assignedDoctorName':dischargeDetails.assignedDoctorName,
        'address':dischargeDetails.address,
        'mobile':dischargeDetails.mobile,
        'symptoms':dischargeDetails.symptoms,
        'admitDate':dischargeDetails.admitDate,
        'releaseDate':dischargeDetails.releaseDate,
        'daySpent':dischargeDetails.daySpent,
        'medicineCost':dischargeDetails.medicineCost,
        'roomCharge':dischargeDetails.roomCharge,
        'doctorFee':dischargeDetails.doctorFee,
        'OtherCharge':dischargeDetails.OtherCharge,
        'total':total,
        'insurance': insurance,
        'insurance_coverage': insurance_coverage,
        'final_bill': final_bill,
    }
    return render_to_pdf('hospital/download_bill.html',dict)



#-----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request,'hospital/admin_appointment.html')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments=models.Appointment.objects.all().filter(status=True, cancelled=False)
    return render(request,'hospital/admin_view_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_add_appointment_view(request):
    appointmentForm=forms.AppointmentForm()
    mydict={'appointmentForm':appointmentForm,}
    if request.method=='POST':
        appointmentForm=forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment=appointmentForm.save(commit=False)
            doctor_id = request.POST.get('doctorId')
            patient_id = request.POST.get('patientId')
            doctor = models.Doctor.objects.get(user_id=doctor_id)
            patient = models.Patient.objects.get(user_id=patient_id)
            appointment.doctorId = doctor
            appointment.patientId = patient
            appointment.doctorName = doctor.user.get_full_name()
            appointment.patientName = patient.user.get_full_name()
            appointment.status=True
            appointment.save()
        return HttpResponseRedirect('admin-view-appointment')
    return render(request,'hospital/admin_add_appointment.html',context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'hospital/admin_approve_appointment.html',{'appointments':appointments})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')
#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    
    # Get unique patient IDs from all appointments with this doctor
    patient_ids = models.Appointment.objects.filter(doctorId=doctor).values_list('patientId', flat=True).distinct()
    patientcount = models.Patient.objects.filter(id__in=patient_ids, status=True).count()
    appointmentcount=models.Appointment.objects.all().filter(status=True,doctorId=doctor, cancelled=False).count()
    patientdischarged=models.PatientDischargeDetails.objects.all().distinct().filter(assignedDoctorName=request.user.get_full_name(), payment_status=True).count()

    #for  table in doctor dashboard
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id).order_by('-id')
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid).order_by('-id')
    appointments=zip(appointments,patients)
    mydict={
    'patientcount':patientcount,
    'appointmentcount':appointmentcount,
    'patientdischarged':patientdischarged,
    'appointments':appointments,
    'doctor':doctor, #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_dashboard.html',context=mydict)



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict={
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'hospital/doctor_patient.html',context=mydict)





@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    # Get the current doctor instance
    doctor = models.Doctor.objects.get(user_id=request.user.id)

    # Get all approved appointments for this doctor
    appointments = models.Appointment.objects.filter(doctorId=doctor, status=True, cancelled=False)

    # Get the unique patients from these appointments
    patient_ids = appointments.values_list('patientId', flat=True).distinct()
    patients = models.Patient.objects.filter(id__in=patient_ids).prefetch_related(
        Prefetch('prescription_set', queryset=models.Prescription.objects.filter(doctor=doctor), to_attr='prescriptions')
    )

    patients_with_details = []
    for patient in patients:
        # For the symptoms, get the description from the last appointment with this doctor.
        last_appointment = appointments.filter(patientId=patient).order_by('-appointment_date', '-appointment_time').first()
        symptoms = ""
        if last_appointment:
            symptoms = last_appointment.description
        
        patients_with_details.append({
            'patient': patient,
            'symptoms': symptoms,
            'prescriptions': patient.prescriptions
        })

    return render(request, 'hospital/doctor_view_patient.html', {'patients_with_details': patients_with_details, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def search_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=request.user.id).filter(Q(symptoms__icontains=query)|Q(user__first_name__icontains=query))
    return render(request,'hospital/doctor_view_patient.html',{'patients':patients,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    # Get the full name of the logged-in doctor
    doctor_full_name = request.user.get_full_name()
    # Filter discharge details for patients assigned to this doctor and who have paid
    discharged_patients = models.PatientDischargeDetails.objects.filter(
        assignedDoctorName=doctor_full_name, payment_status=True,
    ).select_related('patient').order_by('-releaseDate')

    return render(request, 'hospital/doctor_view_discharge_patient.html', {
        'dischargedpatients': discharged_patients,
        'doctor': models.Doctor.objects.get(user_id=request.user.id)  # for profile picture of doctor in sidebar
    })


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'hospital/doctor_appointment.html',{'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id, cancelled=False)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_view_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id, cancelled=False)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.cancelled=True
    appointment.save()
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id, cancelled=False)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'hospital/doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_prescription_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)

    # Get all patients that have an appointment with the current doctor
    appointments = models.Appointment.objects.filter(doctorId=doctor, status=True, cancelled=False)
    patient_ids = appointments.values_list('patientId', flat=True).distinct()
    patients = models.Patient.objects.filter(id__in=patient_ids)

    selected_patient_id = request.GET.get('patient_id')
    prescriptions = None
    if selected_patient_id:
        prescriptions = models.Prescription.objects.filter(patient_id=selected_patient_id, doctor=doctor)
    else:
        # By default, show all prescriptions from this doctor
        prescriptions = models.Prescription.objects.filter(doctor=doctor)


    context = {
        'doctor': doctor,
        'patients': patients,
        'prescriptions': prescriptions,
        'selected_patient_id': selected_patient_id,
    }
    return render(request, 'hospital/doctor_prescription.html', context)



@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def create_prescription_view(request):
    selected_patient_id = request.GET.get('patient_id')
    last_appointment = None
    if selected_patient_id:
        try:
            patient = models.Patient.objects.get(id=selected_patient_id) # This is patient.id
            doctor = models.Doctor.objects.get(user_id=request.user.id)
            last_appointment = models.Appointment.objects.filter(patientId=patient, doctorId=doctor).order_by('-appointment_date', '-appointment_time').first()
        except models.Patient.DoesNotExist:
            pass

    if request.method == 'POST':
        form = forms.PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = models.Doctor.objects.get(user_id=request.user.id)
            prescription.appointment = last_appointment
            prescription.save()
            return redirect('doctor-prescription')
    else:
        form = forms.PrescriptionForm()
        if selected_patient_id:
            try:
                form.fields['patient'].queryset = models.Patient.objects.filter(id=selected_patient_id)
                form.fields['patient'].initial = selected_patient_id
            except models.Patient.DoesNotExist:
                pass

    context = {
        'form': form,
        'doctor': models.Doctor.objects.get(user_id=request.user.id),
        'selected_patient_id': selected_patient_id,
        'last_appointment': last_appointment
    }
    return render(request, 'hospital/create_prescription.html', context)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def add_pharmacy_view(request):
    if request.method == 'POST':
        form = PharmacyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('doctor-prescription')
    else:
        form = PharmacyForm()
    context = {
        'form': form,
        'doctor': models.Doctor.objects.get(user_id=request.user.id),
    }
    return render(request, 'hospital/add_pharmacy.html', context)

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def send_prescription_view(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    prescription.is_sent = True
    prescription.save()
    return redirect('doctor-prescription')

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_profile_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    user = models.User.objects.get(id=doctor.user_id)

    if request.method == 'POST':
        userForm = forms.DoctorUserForm(request.POST, instance=user)
        doctorForm = forms.DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            doctorForm.save()
            return redirect('doctor-profile')
    else:
        userForm = forms.DoctorUserForm(instance=user)
        doctorForm = forms.DoctorProfileForm(instance=doctor)

    mydict = {'userForm': userForm, 'doctorForm': doctorForm, 'doctor': doctor}
    return render(request, 'hospital/doctor_profile.html', context=mydict)

#---------------------------------------------------------------------------------
#------------------------ DOCTOR RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------






#---------------------------------------------------------------------------------
#------------------------ PATIENT RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id)
    doctor = None
    if patient.assignedDoctorId:
        try:
            doctor = models.Doctor.objects.get(user_id=patient.assignedDoctorId)
        except models.Doctor.DoesNotExist:
            doctor = None

    mydict={
        'patient': patient,
        'doctorName': doctor.get_name if doctor else 'Not Assigned',
        'doctorMobile': doctor.mobile if doctor else 'N/A',
        'doctorAddress': doctor.address if doctor else 'N/A',
        'symptoms': patient.symptoms,
        'doctorDepartment': doctor.department if doctor else 'N/A',
        'admitDate': patient.admitDate,
        'doctor': doctor,
    }
    return render(request,'hospital/patient_dashboard.html',context=mydict)



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_appointment.html',{'patient':patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    initial_data = {}
    doctor_id = request.GET.get('doctorId')
    if doctor_id:
        initial_data['doctorId'] = doctor_id
    
    appointmentForm=forms.PatientAppointmentForm(initial=initial_data)
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    message=None
    mydict={'appointmentForm':appointmentForm,'patient':patient,'message':message}
    if request.method=='POST':
        appointmentForm=forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            doctor_user_id = request.POST.get('doctorId')
            doctor = models.Doctor.objects.get(user_id=doctor_user_id)
            
            appointment = appointmentForm.save(commit=False)
            appointment.doctorId = doctor
            appointment.patientId = patient
            appointment.doctorName = doctor.user.get_full_name()
            appointment.patientName = patient.get_name
            appointment.status = False
            appointment.save()
            return HttpResponseRedirect('patient-view-appointment')
    return render(request,'hospital/patient_book_appointment.html',context=mydict)


def patient_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})


def search_doctor_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    
    # whatever user write in search box we get in query
    query = request.GET['query']
    doctors=models.Doctor.objects.all().filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'hospital/patient_view_doctor.html',{'patient':patient,'doctors':doctors})




@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(patientId=patient).prefetch_related('prescription_set').order_by('-appointment_date', '-appointment_time')
    return render(request, 'hospital/patient_view_appointment.html', {'appointments': appointments, 'patient': patient})



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    dischargeDetails = models.PatientDischargeDetails.objects.filter(patient_id=patient.id).order_by('-id').first()

    total = 0
    insurance_covered = 0
    final_amount = 0
    payment_status = False
    assigned_doctor_name = "Not Assigned"

    insurance = models.Insurance.objects.filter(patient=patient).first()

    if dischargeDetails:
        discharge = dischargeDetails
        total = discharge.total
        payment_status = discharge.payment_status
        assigned_doctor_name = discharge.assignedDoctorName

        if insurance:
            # You can either use fixed 80% as in download_pdf_view
            insurance_covered = total * 0.8
        final_amount = total - insurance_covered

        patientDict = {
            'is_discharged': True,
            'patient': patient,
            'patientId': patient.id,
            'patientName': discharge.patientName,
            'assignedDoctorName': discharge.assignedDoctorName,
            'address': discharge.address,
            'mobile': discharge.mobile,
            'symptoms': discharge.symptoms,
            'admitDate': discharge.admitDate,
            'releaseDate': discharge.releaseDate,
            'daySpent': discharge.daySpent,
            'medicineCost': discharge.medicineCost,
            'roomCharge': discharge.roomCharge,
            'doctorFee': discharge.doctorFee,
            'OtherCharge': discharge.OtherCharge,
            'total': total,
            'insurance_covered': insurance_covered,
            'final_amount': final_amount,
            'payment_status': payment_status,
            'assignedDoctorName': assigned_doctor_name,
        }
    else:
        # If not discharged, try to find doctor from last appointment
        last_appointment = models.Appointment.objects.filter(patientId=patient, status=True).order_by('-appointment_date', '-appointment_time').first()
        if last_appointment and last_appointment.doctorName:
            assigned_doctor_name = last_appointment.doctorName
        elif patient.assignedDoctorId:
            doctor_user = models.User.objects.filter(id=patient.assignedDoctorId).first()
            assigned_doctor_name = doctor_user.get_full_name() if doctor_user else "Not Assigned"

        patientDict = {
            'is_discharged': False,
            'patient': patient,
            'patientId': request.user.id,
            'total': total,
            'assignedDoctorName': assigned_doctor_name,
            'final_amount': final_amount,
            'payment_status': payment_status,
        }

    return render(request, 'hospital/patient_discharge.html', context=patientDict)






#------------------------ PATIENT RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------








#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START ------------------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'hospital/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'hospital/contactussuccess.html')
    return render(request, 'hospital/contactus.html', {'form':sub})


#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------



import stripe
from django.conf import settings
from django.shortcuts import render
from django.http import Http404
from .models import PatientDischargeDetails

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def payment(request, patient_id):
    # Fetch the latest discharge details
    invoice = models.PatientDischargeDetails.objects.filter(patient_id=patient_id).order_by('-id').first()
    if not invoice:
        raise Http404("No discharge details found for this patient")

    # Fetch insurance if exists
    patient = models.Patient.objects.get(id=patient_id)
    insurance = models.Insurance.objects.filter(patient=patient).first()

    total = invoice.total
    insurance_covered = 0
    final_amount = total

    if insurance:
        # Example: 80% coverage or adjust based on your logic
        insurance_covered = total * 0.8
        final_amount = total - insurance_covered

    # Stripe expects amount in paise (smallest currency unit)
    amount_cents = int(final_amount * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': f"Invoice Payment for {invoice.patientName}",
                },
                'unit_amount': amount_cents,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f"/payment-success/{patient_id}/"),
        cancel_url=request.build_absolute_uri(f"/payment-cancel/{patient_id}/"),
    )

    return render(request, "hospital/payment.html", {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'session_id': session.id,
        'final_amount': final_amount,  # optional, to display on payment page
        'insurance_covered': insurance_covered,
    })


def payment_success(request, patient_id):
    # Fetch the latest discharge details and update payment status
    invoice = models.PatientDischargeDetails.objects.filter(patient_id=patient_id).order_by('-id').first()
    if invoice:
        invoice.payment_status = True
        invoice.save()
    return render(request, "hospital/payment_success.html", {"patientId": patient_id})

def payment_cancel(request, patient_id):
    return render(request, "hospital/payment_cancel.html", {"patientId": patient_id})


@login_required
@user_passes_test(is_admin)
def admin_health_resources(request):
    resources = HealthResource.objects.all().order_by('-created_at')
    return render(request, 'hospital/admin_health_resources.html', {'resources': resources})

@login_required
@user_passes_test(is_admin)
def create_health_resource(request):
    if request.method == "POST":
        form = HealthResourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_health_resources')
    else:
        form = HealthResourceForm()
    return render(request, 'hospital/create_health_resource.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def edit_health_resource(request, pk):
    resource = get_object_or_404(HealthResource, pk=pk)
    if request.method == "POST":
        form = HealthResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, "Resource updated successfully!")
            return redirect('admin_health_resources')
    else:
        form = HealthResourceForm(instance=resource)
    return render(request, 'hospital/edit_health_resource.html', {'form': form, 'resource': resource})

@login_required
@user_passes_test(is_admin)
def delete_health_resource(request, pk):
    resource = get_object_or_404(HealthResource, pk=pk)
    if request.method == "POST":
        resource.delete()
        messages.success(request, "Resource deleted successfully!")
        return redirect('admin_health_resources')
    return render(request, 'hospital/delete_health_resource.html', {'resource': resource})

@login_required
def health_resources(request):
    tips = HealthResource.objects.filter(category='tips').order_by('-created_at')
    articles = HealthResource.objects.filter(category='articles').order_by('-created_at')
    wellness = HealthResource.objects.filter(category='wellness').order_by('-created_at')
    patient = models.Patient.objects.get(user_id=request.user.id)

    context = {
        'tips': tips,
        'articles': articles,
        'wellness': wellness,
        'patient': patient,
    }
    return render(request, 'hospital/health_resources.html', context)

def is_patient(user):
    return hasattr(user, 'patient')

@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_prescription_view(request):
    # get the logged-in patient
    patient = models.Patient.objects.get(user_id=request.user.id)

    # get all prescriptions for this patient
    prescriptions = Prescription.objects.filter(patient=patient)

    context = {
        'patient': patient,
        'prescriptions': prescriptions,
    }
    return render(request, 'hospital/patient_prescription.html', context)
