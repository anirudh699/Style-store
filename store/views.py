from django.shortcuts import redirect, render
from django.views.generic import View,TemplateView,FormView
from store.forms import OrderForm, Signupform,SiginForm
from store.models import BasketItem, OrderItem, Product, Size, User,Order
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
import os
RZP_KEY_ID=os.environ.get("RZP_KEY_ID")
RZP_KEY_SECRET=os.environ.get("RZP_KEY_SECRET")



# Create your views here.
def send_opt_phone(otp):
    
    from twilio.rest import Client
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
  
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

class SignoutView(View):
    def get(self,request,*args,**kwargs):
        
        logout(request)
        
        return redirect("signin")   
      

class ProductListView(View):
    
    template_name="index.html"
    
    def get(self,request,*args,**kwargs):
        
        qs=Product.objects.all()
        
        p=Paginator(qs,4)
        
        page_number=request.GET.get('page')
        
        try:
         page_obj = p.get_page(page_number)
        except PageNotAnInteger:
              page_obj = p.page(1)
        except EmptyPage:
            page_obj = p.page(p.num_pages)
        context = {'page_obj': page_obj}
            
            
        return render(request,self.template_name,context)

class ProductDetailView(View):
    template_name="product-detail.html"
    
    def get(self,request,*args,**kwargs):
        
        id=kwargs.get("pk")
        qs=Product.objects.get(id=id)
        
        return render(request,self.template_name,{"data":qs})
        
class AddtoCartView(View):
        
        def post(self,request,*args,**kwargs):
            
            id=kwargs.get("pk")
            
            size=request.POST.get("size")
            
            quantity=request.POST.get("quantity")
            
            product_object=Product.objects.get(id=id)
            
            size_object=Size.objects.get(name=size)
            
            basket_object=request.user.cart
            
            BasketItem.objects.create(
                product_object=product_object,
                quantity=quantity,
                size_object=size_object,
                basket_object=basket_object,
                
            )
            print("item added")
            
            return redirect('cart-summary')  
        
class CartSummaryView(View):
    template_name="cart_summary.html"
    
    def get(self,request,*args,**kwargs):
        
        qs=BasketItem.objects.filter(basket_object=request.user.cart,is_order_placed=False)
        
        basket_item_count=qs.count()
        
        baket_total=sum([bi.item_total for bi in qs])
        
        
         
        return render(request,self.template_name,{"basket_items":qs,"basket_total":baket_total,"basket_item_count":basket_item_count})
            
class DeleteCartItemView(View):
        
    def get(self,request,*args,**kwargs):
        
        id=kwargs.get("pk")
        
        BasketItem.objects.get(id=id).delete()
        messages.success(request,"Item removed")
        return redirect("cart-summary")
        

       
      
            
class PlaceHolderView(View):
    
    template_name="place_order.html"
    
    form_class=OrderForm
    def get(self,request,*args,**kwargs):
        
        form_instance=self.form_class()
        
        qs=request.user.cart.cart_item.filter(is_order_placed=False)
        
        total=sum([bi.item_total for bi in qs])
        
        return render(request,self.template_name,{"form":form_instance,"items":qs,"total":total})

    def post(self,request,*args,**kwargs):
        
        form_data=request.POST
        
        
        form_insatance=self.form_class(form_data)
        
        if form_insatance.is_valid():
            
            form_insatance.instance.customer=request.user
            
            order_instance=form_insatance.save()
            
            
            basket_items=request.user.cart.cart_item.filter(is_order_placed=False)
            
            for bi in basket_items:
                
                OrderItem.objects.create(
                    order_object=order_instance,
                    product_object=bi.product_object,
                    quantity=bi.quantity,
                    size_object=bi.size_object,
                    price=bi.product_object.price   
                    
                )
                
                bi.is_order_placed=True
                
                bi.save()
                
        return redirect('productlist')               
        
class OrderSummaryView(View):
    
    template_name="order_summary.html"
    
    def get(self,request,*args,**kwargs):
        
        qs=reversed(request.user.orders.all())
        
        return render(request,self.template_name,{"orders":qs})   
    
       
        
    
    
    
    
    
            
        
            
            
            
            
            
