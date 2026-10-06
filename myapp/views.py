from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart
import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User  

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = 'http://127.0.0.1:8000'

def index(request):
    try:
        user=User.objects.get(email=request.session['email'])
        if user.usertype=="buyer":
            return render(request,'index.html')
        else:
            return render(request,'seller-index.html')
    except:
        return render(request,'index.html')

def shop(request):
    products=Product.objects.all()
    return render(request,'shop.html',{'products':products})

def contact(request):
    return render(request,'contact.html')

def signup(request):
    if request.method=="POST":
        try:
            user=User.objects.get(email=request.POST['email'])
            msg="Email Already Registered"
            return render(request,'signup.html',{'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    address=request.POST['address'],
                    password=request.POST['password'],
                    profile_picture=request.FILES['profile_picture'],
                    usertype=request.POST['usertype']
                )
                msg="User Sign Up Successfully"
                return render(request,'login.html',{'msg':msg})
            else:
                msg="Password & Confirm Password Does Not Matched"
                return render(request,'signup.html',{'msg':msg})
    else:
        return render(request,'signup.html')

def login(request):
    if request.method=="POST":
        try:
            user=User.objects.get(email=request.POST['email'])
            if user.password==request.POST['password']:
                request.session['email']=user.email
                request.session['fname']=user.fname
                request.session['profile_picture']=user.profile_picture.url
                if user.usertype=="buyer":
                    wishlist=Wishlist.objects.filter(user=user)
                    request.session['wishlist_count']=len(wishlist)
                    Carts=Carts.objects.filter(user=user,payment_status=False)
                    request.session['cart_count']=len(carts)
                    return render(request,'index.html')
                else:
                    return render(request,'seller-index.html')
            else:
                msg="Incorrect Password"
                return render(request,'login.html',{'msg':msg})
        except:
            msg="Email Not Registered"
            return render(request,'login.html',{'msg':msg})
    else:
        return render(request,'login.html')

def logout(request):
    try:
        del request.session['email']
        del request.session['fname']
        del request.session['profile_picture']
        del request.session['wishlist_count']
        del request.session['cart_count']
        msg="User Logged Successfully"
        return render(request,'login.html',{'msg':msg})
    except:
        msg="User Logged Successfully"
        return render(request,'login.html',{'msg':msg})

def profile(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        user.fname=request.POST['fname']
        user.lname=request.POST['lname']
        user.mobile=request.POST['mobile']
        user.address=request.POST['address']
        try:
            user.profile_picture=request.FILES['profile_picture']
        except:
            pass
        user.save()
        msg="Profile Updated Successfully"
        request.session['profile_picture']=user.profile_picture.url
        if user.usertype=="buyer":
            return render(request,'profile.html',{'user':user,'msg':msg})
        else:
            return render(request,'seller-profile.html',{'user':user,'msg':msg})
    else:
        if user.usertype=="buyer":
            return render(request,'profile.html',{'user':user})
        else:
            return render(request,'seller-profile.html',{'user':user})

def change_password(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        if user.password==request.POST['old_password']:
            if request.POST['new_password']==request.POST['cnew_password']:
                if user.password!=request.POST['new_password']:
                    user.password=request.POST['new_password']
                    user.save()
                    del request.session['email']
                    del request.session['fname']
                    del request.session['profile_picture']
                    msg="Password Changed Successfully"
                    return render(request,'login.html',{'msg':msg})
                else:
                    msg="Your New Password Can't Be From Your Old Password"
                    if user.usertype=="buyer":
                        return render(request,'change-password.html',{'msg':msg})
                    else:
                        return render(request,'seller-change-password.html',{'msg':msg})
            else:
                msg="Your New Password & Confirm New Password Does Not Matched"
                if user.usertype=="buyer":
                    return render(request,'change-password.html',{'msg':msg})
                else:
                    return render(request,'seller-change-password.html',{'msg':msg})
        else:
            msg="Old Password Does Not Matched"
            if user.usertype=="buyer":
                return render(request,'change-password.html',{'msg':msg})
            else:
                return render(request,'seller-change-password.html',{'msg':msg})
    else:
        if user.usertype=="buyer":
            return render(request,'change-password.html')
        else:
            return render(request,'seller-change-password.html')

def seller_add_product(request):
    seller=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        Product.objects.create(
            seller=seller,
            product_catagory=request.POST['product_catagory'],
            product_name=request.POST['product_name'],
            product_price=request.POST['product_price'],
            product_desc = request.POST.get('product_desc', ''),
            product_image=request.FILES.get('product_image'),
        )
        msg="Product Added Successfully"
        return render(request,'seller-add-product.html',{'msg':msg})
    else:
        return render(request,'seller-add-product.html')

def seller_view_product(request):
    seller=User.objects.get(email=request.session['email'])
    products=Product.objects.filter(seller=seller)
    return render(request,'seller-view-product.html',{'products':products})

def seller_product_details(request,pk):
    product=Product.objects.get(pk=pk)
    return render(request,'seller-product-details.html',{'product':product})

def product_details(request,pk):
    wishlist_flag=False
    cart_flag=False
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    try:
        Wishlist.objects.get(user=user,product=product)
        wishlist_flag=True 
    except:
        pass
    try:
        Cart.objects.get(user=user,product=product,payment_status=False)
        cart_flag=True 
    except:
        pass
    return render(request,'product-details.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def seller_product_edit(request,pk):
    product=Product.objects.get(pk=pk)
    if request.method=="POST":
        product.product_category=request.POST.get('product_category')
        product.product_name=request.POST['product_name']
        product.product_price=request.POST['product_price']
        product.product_desc=request.POST['product_desc']
        try:
            product.product_image=request.FILES['product_image']
        except:
            pass
        product.save()
        msg="Product Update Successfully"
        return render(request,'seller-product-edit.html',{'product':product,'msg':msg})
    else:
        return render(request,'seller-product-edit.html',{'product':product})

def seller_product_delete(request,pk):
    product=Product.objects.get(pk=pk)
    product.delete()
    return redirect('seller-view-product')

def catagory(request,cat):
    products=Product()
    if cat=="all":
        products=Product.objects.all()
    else:
        products=Product.objects.filter(product_catagory=cat)
    return render(request,'shop.html',{'products':products})

def add_to_wishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Wishlist.objects.get_or_create(user=user,product=product)
    return redirect('wishlist')

def wishlist(request):
    user=User.objects.get(email=request.session['email'])
    wishlists=Wishlist.objects.filter(user=user)
    request.session['wishlist_count']=len(wishlists)
    return render(request,'wishlist.html',{'wishlist':wishlists})

def remove_from_wishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    Wishlist.objects.filter(user=user,product=product).delete()
    return redirect('wishlist')

def add_to_cart(request, pk):
    email = request.session.get('email')
    if not email:
        return redirect('login')  
    product = Product.objects.get(pk=pk)
    user = User.objects.get(email=email)
    Cart.objects.get_or_create(
        user=user,
        product=product,
        product_price=product.product_price,
        product_qty=1,
        total_price=product.product_price,
        payment_status=False
    )
    return redirect('cart')

def cart(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')
    net_price = 0
    user = User.objects.get(email=email)
    carts = Cart.objects.filter(user=user,payment_status=False)
    for i in carts:
        net_price = net_price + i.total_price
    request.session['cart_count'] = len(carts)
    return render(request, 'cart.html', {'carts': carts, 'net_price': net_price})

def remove_from_cart(request, pk):
    email = request.session.get('email')
    if not email:
        return redirect('login')
        
    product = Product.objects.get(pk=pk)
    user = User.objects.get(email=email)
    Cart.objects.filter(user=user, product=product).delete()
    return redirect('cart')

def change_qty(request,pk):
    cart=Cart.objects.get(pk=pk)
    product_qty=int(request.POST['product_qty'])
    cart.product_qty=int(request.POST['product_qty'])
    cart.total_price=cart.product_price*product_qty
    cart.save()
    return redirect('cart')


@csrf_exempt
def create_checkout_session(request):
    try:
        checkout_session = stripe.checkout.Session.create(
            # Yahan se payment_method_types=['card'] HATA DIYA HAI
            line_items=[
                {
                    'price_data': {
                        'currency': 'inr', # Ya 'usd' jo aap use kar rahe ho
                        'product_data': {
                            'name': 'Total Cart Payment',
                        },
                        'unit_amount': 20059900, # Amount in paise (e.g. 200599 * 100)
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://127.0.0.1:8000/success/', # Aapka success page URL
            cancel_url='http://127.0.0.1:8000/cart/',      # Cancel hone par Cart page ka URL
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return HttpResponse(str(e))
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=400)

def success(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		i.payment_status=True
		i.save()
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')

def myorder(request):
    user=User.objects.get(email=request.session['email'])
    orders=Cart.objects.filter(user=user,payment_status=True)
    return render(request,'myorder.html',{'orders':orders})