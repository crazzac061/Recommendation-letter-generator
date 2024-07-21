from django import forms
from home.models import StudentLoginInfo, TeacherInfo
from django.core.exceptions import ValidationError

class StudentForm(forms.ModelForm):
    username = forms.CharField(max_length=120, help_text="Enter Name:")
    roll_number = forms.CharField(max_length=9, help_text="Roll no: ")
    dob = forms.DateField(help_text="Date of Birth")
    gender = forms.CharField(max_length=10, help_text="Gender")

    class Meta:
        model = StudentLoginInfo
        exclude = ('department','program',)

## 78 batch
class TeacherInfoForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = TeacherInfo
        fields = ['name', 'title', 'phone', 'email', 'department', 'images', 'subjects']

        widgets = {
            'subjects': forms.CheckboxSelectMultiple(),  # Or use forms.SelectMultiple() if you prefer a dropdown
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match")
        return cleaned_data
