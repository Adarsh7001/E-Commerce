from django.shortcuts import render,redirect
from shop.models import Product
from cart.models import Cart,Payment
from cart.models import Order_table
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import login

import razorpay

# Create your views here.
# @login_required
def cart(request,pk):
    p=Product.objects.get(id=pk)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=p)
        if(p.stock>0):
            cart.quantity+=1
            cart.save()
            p.stock_=1
            p.save()
    except:
        cart=Cart.objects.create(user=u,product=p,quantity=1)
        cart.save()
        p.stock-=1
        p.save()
    return redirect('cart:cart_view')
# @login_required
def cart_view(request):
    u=request.user
    cart=Cart.objects.filter(user=u)
    return render(request,'cart_view.html',{'cart':cart})

def decrement(request,pk):
    p=Product.objects.get(id=pk)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=p)
        if(cart.quantity>1):
            cart.quantity-=1
            cart.save()
            p.stock+=1
            p.save()
        else:
            cart.delete()
            cart.save()
            p.stock+=1
            p.save()
    except:
        pass
    return redirect('cart:cart_view')


def delete(request, pk):
    p = Product.objects.get(id=pk)
    u = request.user
    try:
        cart = Cart.objects.get(user=u, product=p)
        cart.delete()
        p.stock += cart.quantity
        p.save()
    except:
        pass
    return redirect('cart:cart_view')


def order(request):
    if(request.method=='POST'):
        n=request.POST.get('n')
        a=request.POST.get('a')
        z=request.POST.get('z')
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0
        for i in c:
            total=total+(i.quantity*i.product.price)
        total=int(total*100)
#create razorpay client usong our API credentials
        client=razorpay.Client(auth=('rzp_test_PWhGmAwZRgvpt4','p6BwVsUsGN8gmZZSM7m3Hq8n'))
#create order
        response_payment=client.order.create(dict(amount=total,currency='INR'))
        # print(response_payment)
        order_id=response_payment['id']
        order_status=response_payment['status']
        if(order_status=='created'):
            p=Payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c:
                o=Order_table.objects.create(user=u,product=i.product,address=a,phone=n,pin=z,no_of_items=i.quantity,order_id=order_id)
                o.save()
        response_payment['name']=u.username
        return render(request,'payment.html',{'payment':response_payment})
    return render(request,'order.html')


def payment(request):
    return render(request,'payment.html')

@csrf_exempt
def payment_status(request,u):

    if not request.user.is_authenticated:
        user=User.objects.get(username=u)
        login(request,user)
    if(request.method=='POST'):
        response=request.POST
        print(u)
        param_dict={
            'razorpay_order_id':response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature']
        }
        client = razorpay.Client(auth=('rzp_test_PWhGmAwZRgvpt4', 'p6BwVsUsGN8gmZZSM7m3Hq8n'))
        try:
            status=client.utility.verify_payment_signature(param_dict)

            #after successful payment

            #retrieve a particular record with particula order id
            ord=Payment.objects.get(order_id=response['razorpay_order_id'])
            ord.razorpay_payment_id=response['razorpay_payment_id']
            ord.paid=True
            ord.save()
            u=User.objects.get(username=u)
            c=Cart.objects.filter(user=u)


            #filter the order_table details for particular user with order_id=response['razorpay_order_id']
            o=Order_table.objects.filter(user=u,order_id=response['razorpay_order_id'])
            for i in o:
                i.payment_status='paid'
                i.save()
            c.delete()
            return render(response,'status.html',{'status':True})
        except:
            return render(request,'status.html',{'status':False})
@login_required()
def order_view(request):
    u=request.user
    b=Order_table.objects.filter(user=u,payment_status='paid')
    return render(request,'order_view.html',{'customer':b,'u':u.username})
