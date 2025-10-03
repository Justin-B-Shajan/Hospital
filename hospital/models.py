from django.db import models
from django.contrib.auth.models import User



departments=[('Cardiologist','Cardiologist'),
('Dermatologists','Dermatologists'),
('Emergency Medicine Specialists','Emergency Medicine Specialists'),
('Allergists/Immunologists','Allergists/Immunologists'),
('Anesthesiologists','Anesthesiologists'),
('Colon and Rectal Surgeons','Colon and Rectal Surgeons')
]
class Doctor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/DoctorProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=True)
    department= models.CharField(max_length=50,choices=departments,default='Cardiologist')
    status=models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return "{} ({})".format(self.user.first_name,self.department)



class Patient(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/PatientProfilePic/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    symptoms = models.CharField(max_length=100,null=True, blank=True)
    assignedDoctorId = models.PositiveIntegerField(null=True)
    admitDate=models.DateField(null=True, blank=True)
    status=models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name+" ("+self.symptoms+")"


class Appointment(models.Model):
    patientId= models.ForeignKey(Patient, null=True, on_delete=models.SET_NULL)
    doctorId= models.ForeignKey(Doctor, null=True, on_delete=models.SET_NULL)
    patientName=models.CharField(max_length=40,null=True)
    doctorName=models.CharField(max_length=40,null=True)
    appointment_date=models.DateField(null=True)
    appointment_time=models.TimeField(null=True)
    description=models.TextField(max_length=500)
    status=models.BooleanField(default=False)
    cancelled=models.BooleanField(default=False)



class PatientDischargeDetails(models.Model):
    patient=models.ForeignKey(Patient,on_delete=models.CASCADE, null=True)
    patientName=models.CharField(max_length=40)
    assignedDoctorName=models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=True)
    symptoms = models.CharField(max_length=100,null=True)

    admitDate=models.DateField(null=False)
    releaseDate=models.DateField(null=False)
    daySpent=models.PositiveIntegerField(null=False)

    roomCharge=models.PositiveIntegerField(null=False)
    medicineCost=models.PositiveIntegerField(null=False)
    doctorFee=models.PositiveIntegerField(null=False)
    OtherCharge=models.PositiveIntegerField(null=False)
    total=models.PositiveIntegerField(null=False)
    payment_status = models.BooleanField(default=False)


class HealthResource(models.Model):
    CATEGORY_CHOICES = [
        ('tips', 'Health Tips'),
        ('articles', 'Articles'),
        ('wellness', 'Wellness Resources'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"

class Pharmacy(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_info = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.SET_NULL, null=True, blank=True)
    medication = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    instructions = models.TextField()
    date_prescribed = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Prescription for {self.patient} by Dr. {self.doctor.get_name}"

class Insurance(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    provider = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=100)
    coverage_type = models.CharField(max_length=100)
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.patient.get_name}'s Insurance"
