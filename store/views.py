from django.shortcuts import redirect, render
from django.views.generic import View
from store.forms import Signupform,SiginForm
from store.models import Product, User
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
# Create your views here.
def send_opt_phone(otp):
    
    from twilio.rest import Client
  
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='+15636075703',
        body=otp,
        to='+919544541391')
    print(message.sid)


def send_otp_email(user):
    user.generate_otp()
    
    send_opt_phone(user.otp)
    
    subject = "Otp verification"
    
    message = f"your one time passord for verification is {user.otp}"
    
    from_email = "anirudhashok7898@gmail.com"
    
    to_email =[user.email]
    
    send_mail(subject,message,from_email,to_email)

    



class SignUpView(View):
    
    template_name="register.html"
    
    form_class=Signupform
    
    def get(self,request,*args,**kwargs):
        
        form_instance=self.form_class
        
        return render(request,self.template_name,{"form":form_instance})
    
    def post(self,request,*args,**kwargs):
        
        form_data=request.POST
        
        form_instance=self.form_class(form_data)
        
        if form_instance.is_valid():
            
          user_obj= form_instance.save(commit=False)
          
          user_obj.is_active=False
          
          user_obj.save()
          
          send_otp_email(user_obj)
          
          
          return redirect("verifyemail")
        return render(request,self.template_name,{"form":form_instance})
    
class VerifyEmailView(View):
        
        tempalte_name="verifyemail.html"
        
        def get(self,request,*args,**kwargs):
        
      
            return render(request,self.tempalte_name)
        
        def post(self,request,*args,**kwargs):
            
            otp=request.POST.get("otp")
            
            try:
            
                user_obj=User.objects.get(otp=otp)
                
                print(user_obj)
                
                user_obj.is_active=True
                
                user_obj.is_verfied=True
                
                user_obj.otp=None
                
                user_obj.save()
                
                return redirect("signin")
            except:
                messages.error(request,'Invalid Otp')
                
                return render(request,self.tempalte_name)
                
class SiginView(View):
    template_name="sigin.html"
    
    form_class=SiginForm
    
    def get(self,request,*args,**kwargs):
        
        form_insatance=self.form_class
        
        return render(request,self.template_name,{"form":form_insatance})
    
    def post(self,request,*args,**kwargs):
        
        form_data=request.POST
        
        form_instance=self.form_class(form_data)
        
        if form_instance.is_valid():
            
            uname=form_instance.cleaned_data.get("username")
            pwd=form_instance.cleaned_data.get("password")
            
            user_obj=authenticate(request,username=uname,password=pwd)
            
            if user_obj:
                
                login(request,user_obj)
                
                return redirect("productlist")
               
            
        
        return render(request,self.template_name,{"form":form_instance})
        

class ProductListView(View):
    
    template_name="index.html"
    
    def get(self,request,*args,**kwargs):
        
        qs=Product.objects.all()
        
        return render(request,self.template_name,{"data":qs})

class ProductDetailView(View):
    template_name="product-detail.html"
    
    def get(self,request,*args,**kwargs):
        
        id=kwargs.get("pk")
        qs=Product.objects.get(id=id)
        
        return render(request,self.template_name,{"data":qs})
        


    
    
            
            
            
            
        
            
            
            
            
            