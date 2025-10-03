from django import forms
from django.contrib.auth.models import User
from . import models
from .models import HealthResource, Pharmacy, Prescription, Insurance



#for admin signup
class AdminSigupForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }


#for student related form
class DoctorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class DoctorForm(forms.ModelForm):
    class Meta:
        model=models.Doctor
        fields=['address','mobile','department','status','profile_pic']

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model=models.Doctor
        fields=['address','mobile','department','profile_pic']


#for teacher related form
class PatientUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }
class PatientForm(forms.ModelForm):
    #this is the extrafield for linking patient and their assigend doctor
    class Meta:
        model=models.Patient
        fields=['address','mobile','profile_pic', 'admitDate']
        widgets = {
            'admitDate': forms.DateInput(attrs={'type': 'date'}),
        }

class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model=models.Patient
        fields=['address','mobile','profile_pic', 'admitDate', 'status']
        widgets = {
            'admitDate': forms.DateInput(attrs={'type': 'date'}),
        }



class AppointmentForm(forms.ModelForm):
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Doctor Name and Department", to_field_name="user_id")
    patientId=forms.ModelChoiceField(queryset=models.Patient.objects.all().filter(status=True),empty_label="Patient Name and Symptoms", to_field_name="user_id")
    class Meta:
        model=models.Appointment
        fields=['description','status']


class PatientAppointmentForm(forms.ModelForm):
    doctorId=forms.ModelChoiceField(queryset=models.Doctor.objects.all().filter(status=True),empty_label="Doctor Name and Department", to_field_name="user_id")
    class Meta:
        model=models.Appointment
        fields=['appointment_date','appointment_time','description','status']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }


#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))



class HealthResourceForm(forms.ModelForm):
    class Meta:
        model = HealthResource
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class PharmacyForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ['name', 'address', 'contact_info']

class PatientModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_name

class PrescriptionForm(forms.ModelForm):
    patient = PatientModelChoiceField(
        queryset=models.Patient.objects.all()
    )
    class Meta:
        model = models.Prescription
        fields = ['patient', 'pharmacy', 'medication', 'dosage', 'instructions']

class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ['provider', 'policy_number', 'coverage_type', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'})
        }