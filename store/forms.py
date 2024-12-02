from django import forms

from store.models import Order, User

from django.contrib.auth.forms import UserCreationForm


class Signupform(UserCreationForm):
    
    class Meta:
        
        model=User
        
        fields=["username","email","phone","password1","password2"]
        widgets={
            
        }
class SiginForm(forms.Form):
        username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
        password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control"}))


class OrderForm(forms.ModelForm):
    
    class Meta:
        
        model=Order
        
        fields=['address','phone','payment_method']
        
        