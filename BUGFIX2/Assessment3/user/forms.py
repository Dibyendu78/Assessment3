from django import forms
from django.shortcuts import render, redirect
import re

class LeadForm(forms.Form):
    name = forms.CharField(required=True,max_length=50)
    email = forms.CharField(required=True,max_length=50)
    phone = forms.CharField(required=True,max_length=10)


    def clean_email(self):
        email= self.cleaned_data.get('email',"")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise forms.ValidationError("Invalid email format")
        return email
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', "")
        if not re.match(r"^[6-9]\d{9}$", phone):
            raise forms.ValidationError("Invalid phone number format")
        return phone
     