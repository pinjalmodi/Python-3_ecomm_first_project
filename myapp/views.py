from django.shortcuts import render,redirect
from . models import User,Product,Wishlist,Cart
from django.conf import settings
from django.core.mail import send_mail
import random
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

def validate_signup(request):
	email=request.GET.get('email')
	data={
		'is_taken': User.objects.filter(email__iexact=email).exists()
	}
	return JsonResponse(data)

def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="buyer":
			return render(request,'index.html')
		else:
			return render(request,'seller-index.html')
	except:
		return render(request,'index.html')

def contact(request):
	return render(request,'contact.html')

def register(request):
	if request.method=="POST":
		try:
			User.objects.get(email=request.POST['email'])
			msg="Email already registered"
			return render(request,'login.html',{'msg':msg})

		except:
			if request.POST['password']==request.POST['cpassword']:

				User.objects.create(
						fname=request.POST['f_name'],
						lname=request.POST['l_name'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						password=request.POST['password'],
						profile_picture=request.FILES['profile_picture'],
						usertype=request.POST['usertype'],
						)
				msg='User registered Successfully Please login'
				return render(request,'login.html',{'msg':msg})
			else:
				msg='Password and confirm password does not match'
				return render(request,'register.html',{'msg':msg})
	else:		
		return render(request,'register.html')

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				request.session['email']=user.email 
				request.session['fname']=user.fname
				request.session['profile_picture']=user.profile_picture.url
				wishlists=Wishlist.objects.filter(user=user)

				request.session['wishlist_count']=len(wishlists)
				carts=Cart.objects.filter(user=user,payment_status=False)
				request.session['cart_count']=len(carts)
				msg='Login Successfully'
				if user.usertype=='buyer':
					return render(request,'index.html',{'msg':msg})
				else:
					return render(request,'seller-index.html',{'msg':msg})
			else:
				msg='Password Incorrect'
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
		msg='Logged Out successfully'
		return render(request,'login.html',{'msg':msg})

	except:
		msg='Logged Out successfully'
		return render(request,'login.html',{'msg':msg})

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
					msg='Password Updated Successfully'
					return render(request,'login.html',{'msg':msg})
				else:
					
					msg='New Password cant be from old passwords'
					if user.usertype=="buyer":
						return render(request,'change-password.html',{'msg':msg})
					else:
						return render(request,'seller-change-password.html',{'msg':msg})		

			else:
				msg='New and confirm new password does not match'
				if user.usertype=="buyer":
					return render(request,'change-password.html',{'msg':msg})
				else:
					return render(request,'seller-change-password.html',{'msg':msg})
				
		else:
			msg='old Password does not match'
			if user.usertype=="buyer":
				return render(request,'change-password.html',{'msg':msg})
			else:
				return render(request,'seller-change-password.html',{'msg':msg})
			
	else:
		if user.usertype=="buyer":
			return render(request,'change-password.html')
		else:
			return render(request,'seller-change-password.html')


def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['f_name']
		user.lname=request.POST['l_name']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		try:
			user.profile_picture=request.FILES['profile_picture']
		except:
			pass
		user.save()
		request.session['profile_picture']=user.profile_picture.url
		msg='Profile Updated Successfully'
		if user.usertype=="buyer":
			return render(request,'profile.html',{'msg':msg})
		else:
			return render(request,'seller-profile.html',{'msg':msg})
		

	else:
		if user.usertype=="buyer":
			return render(request,'profile.html',{'user':user, 'msg':msg })
		else:
			return render(request,'seller-profile.html',{'user':user})
		


def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=str(random.randint(1000,9999))
			subject = 'OTP for Forgot Password'
			message = 'Hello'+user.fname+'Your OTP for forgot Password is'+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, message, email_from, recipient_list )
			request.session['email']=user.email
			request.session['otp']=otp

			return render(request,'otp.html')
		except:
			msg="Email Not Registered"
			return render(request,'forgot-password.html',{'msg':msg})

	else:
		return render(request,'forgot-password.html')


def verify_otp(request):
	otp1=int(request.POST['otp'])
	otp2=int(request.session['otp'])

	if otp1==otp2:
		del request.session['otp']
		return render(request,'new-password.html')
	else:
		msg='Invalid OTP'
		return render(request,'otp.html',{'msg':msg})


def new_password(request):
	if request.POST['new_password']==request.POST['cnew_password']:
		user=User.objects.get(email=request.session['email'])
		if user.password!=request.POST['new_password']:
			user.password=request.POST['new_password']
			user.save( )
			del request.session['email']
			msg="Password Updated Successfully"
			return render(request,'login.html')
		else:
			msg='New Password can not be from old passwords'
			return render(request,'new-password.html',{'msg':msg})


	else:
		msg="New password and confirm new password does not match"
		return render(request,'new-password.html',{'msg':msg})


def seller_add_product(request):
	if request.method=="POST":
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
			seller=seller,
			product_name=request.POST['product_name'],
			product_price=request.POST['product_price'],
			product_category=request.POST['product_category'],
			product_desc=request.POST['product_desc'],
			product_image=request.FILES['product_image'],

			)
		msg='Product Added Successfully'
		return render(request,"seller-add-product.html",{'msg':msg})

	else:
		return render(request,"seller-add-product.html")

def seller_view_product(request):
	seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=seller)
	return render(request,'seller-view-product.html',{'products':products})

def seller_product_details(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller-product-details.html',{'product':product})


def seller_product_edit(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_category=request.POST['product_category']
		product.product_name=request.POST['product_name']
		product.product_price=request.POST['product_price']
		
		product.product_desc=request.POST['product_desc']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass

		product.save()
		msg='Product Updated Successfully'
		return render(request,'seller-product-edit.html',{'product':product , 'msg':msg})

	else:
		return render(request,'seller-product-edit.html',{'product':product})


def seller_product_delete(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	msg="Product deleted successfully"
	return redirect('seller-view-product')


def products(request):
	products=Product.objects.all()
	return render(request,'products.html',{'products':products})

def product_details(request,pk):
	
	wishlist_flag=False
	cart_flag=False
	user=User.objects.get(email=request.session['email'])
	product=Product.objects.get(pk=pk)
	
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
	return render(request,'product-details.html',{'product':product, 'wishlist_flag':wishlist_flag , 'cart_flag':cart_flag})


def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,product=product)
	return redirect('wishlist')


def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists})


def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')

def products_by_category(request,cat):
	products=Product()
	if cat=='all':
		products=Product.objects.all()
	else:
		products=Product.objects.filter(product_category=cat)
	return render(request,'products.html',{'products':products})


def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(user=user,
		product=product,
		product_price=product.product_price,
		product_qty=1,
		total_price=product.product_price,
		payment_status=False
		)
	return redirect('cart')


def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price': net_price})


def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')


def change_qty(request):
	product_qty=int(request.POST['product_qty'])
	cid=int(request.POST['cid'])
	cart=Cart.objects.get(pk=cid)
	cart.product_qty=product_qty
	cart.total_price=cart.product_price*product_qty
	cart.save()
	return redirect('cart')

