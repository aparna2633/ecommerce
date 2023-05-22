from django.shortcuts import render,redirect
from product.forms import *
from store.views import index
from .models import CartItems, Product,Category,Address,Order,Orderitem,Coupon,Wishlist,GuestCart
from store.models import Account
import random
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
import razorpay
from django.shortcuts import render, get_object_or_404
import json
from django.core.exceptions import ObjectDoesNotExist
from store.views import loginacc
from django.core.paginator import Paginator
import os
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
def product_view_sorting(request):
    if not request.session.session_key:
        request.session.create()
    request.session['guest_key'] = request.session.session_key
    cart_items = GuestCart.objects.filter(user_ref=request.session['guest_key'])
    count = cart_items.count()
    sort_option = request.GET.get('select')
    if sort_option == 'price_asc':
        products = Product.objects.all().order_by('price')
    elif sort_option == 'price_desc':
        products = Product.objects.all().order_by('-price')
    else:
        products = Product.objects.all()

    # Pagination
    paginator = Paginator(products,3)  # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    category = Category.objects.all()
    sub = SubCategory.objects.all()
    count = CartItems.objects.filter(user_id=request.user.id).count()
    context = {
        'category': category,
        'products': page_obj,  # Pass the current page object instead of all products
        'sub': sub,
        'count': count,
        'paginator': paginator,  # Pass the paginator object
        'page_obj': page_obj,  # Pass the current page object
    }
    return render(request, 'products.html', context)


def skincare(request):
    products=Product.objects.filter(Category=skincare)
    return render(request,{'products':products})

def profile(request):
    if request.user.is_authenticated:
        fields = Address.objects.filter(user=request.user)
        return render(request, 'profile.html',{'fields':fields})
    else:
        return redirect(loginacc)

def order_deatails(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user)
        orderitm =Orderitem.objects.all()
        return render(request, 'order_list.html',{'order':order,'orderitm':orderitm})

def order_cancel(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return HttpResponse("Invalid order id.")
    
    if order.status and order.delivery_status == 'Pending':
        order.status = False
        order.delivery_status = 'Cancelled'
        messages.success(request, "Order canceled.")
        order.save()
        return redirect('order_deatails')
    else:
        messages.error(request, "Order already canceled.")
        return redirect('order_deatails')
    
def order_return(request, id):
    try:
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        return HttpResponse("Invalid order id.")
    
    if order.status and order.delivery_status == 'Delivered':
        order.status = False
        order.delivery_status = 'Returned'
        messages.success(request, "Order Returned.")
        order.save()
        return redirect('order_deatails')
    else:
        messages.error(request, "Order already returned.")
        return redirect('order_deatails')

#starting_wishlist

def wishlist(request):
    if request.user.is_authenticated:
        wish_items = Wishlist.objects.filter(user=request.user)
        count_prod = Wishlist.objects.filter(user_id=request.user.id).count()
        count = CartItems.objects.filter(user_id=request.user.id).count()
    else:
        return redirect(loginacc)
    return render(request, 'wishlist.html',{'wish_items':wish_items,'count_prod':count_prod,'count':count})

def add_to_wishlist(request, id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=id)
        wish_item = Wishlist.objects.filter(product=product, user=request.user)
        
        if wish_item.exists():
            messages.warning(request, "Product already exists in your wishlist.")
        else:
            wish_item = Wishlist.objects.create(product=product, user=request.user)
            messages.success(request, "Product added to your wishlist.")
        
        return redirect('product_view_sorting')
    else:
        messages.error(request, "Please login.")
        return render(request, 'index.html')
    
def remove_item(request, id):
    if request.user.is_authenticated:
        Wishlist.objects.get(id=id).delete()
        return redirect(wishlist)
#ending_wishlist

def category_view(request):
    category = Category.objects.all()
    return render(request, 'products.html', category)

def single_product(request,id):
    if not request.session.session_key:
            request.session.create()
    request.session['guest_key']=request.session.session_key
    cart_items = GuestCart.objects.filter(user_ref = request.session['guest_key'])
    count = cart_items.count() 
    product = Product.objects.get(id=id)
    return render(request,'single-product-details.html',{'product':product})

def remove_cart(request, id):
    if request.user.is_authenticated:
        CartItems.objects.get(id=id).delete()
        count = CartItems.objects.filter(user_id=request.user.id).count()
        request.session['count'] = count
        return redirect(view_cart)
    # else:
    #     Guest_Cart.objects.get(id=id).delete()
    #     return redirect(view_cart)

@csrf_exempt
def success(request):
    
    response = request.POST
   
    params_dict = {
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_signature': response['razorpay_signature']
    }

    razorpay_key_id = os.getenv('RAZORPAY_KEY_ID') or 'rzp_test_S0yLGz7vAs7dYf'
    razorpay_key_secret = os.getenv('RAZORPAY_KEY_SECRET') or '03wmNfbrN6kxUtYDgE9XywDn'
    
    client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
    try:
        client.utility.verify_payment_signature(params_dict)
        print("ffffffff",request.POST)
        neworder = Order()
        neworder.user = request.user
        address_pk = request.session.get('addressId')
        print(address_pk)
        
        try:
            neworder.address = Address.objects.get(pk=address_pk)
            print(neworder.address,'hhhfdfhdkjfhalk')
        except ObjectDoesNotExist:

            return redirect('checkout', error='Address not found')

        neworder.payment_method = 'RAZORPAY'

        now = timezone.now()
        ord2 = str(datetime.now()) + str(request.user.id) + str(random.randint(0, 100))
        ord1 = ord2.translate({ord(':'): None, ord('-'): None, ord(' '): None, ord('.'): None}) 
        neworder.order_id = ord1
        if not neworder.address:
            return redirect(checkout)
        
        total_amount =0
        cartItems = CartItems.objects.filter(user=request.user)
        print('got cart items')
        for item in cartItems:
            print('looping')
            total_amount += item.total_price - item.discount
        print("total_price",total_amount)
        neworder.total_price = total_amount
        neworder.discount= request.session.get('discount')
        neworder.total=neworder.total_price+neworder.discount
        neworder.save()


        neworderitems = CartItems.objects.filter(user=request.user)
        for item in neworderitems:
            Orderitem.objects.create(
                order=neworder,
                product=item.product,
                product_price=item.unit_price * item.quantity,
                quantity=item.quantity
            )

        CartItems.objects.filter(user=request.user).delete()
        return redirect(order_confirmation)
    except Exception as e:
        print("jjjjjjjjjjjjjjj",e)
        return render(request, 'checkout.html', context={'status': False})

@login_required(login_url=loginacc)
def checkout(request):
        if request.user.is_authenticated:
            print('got tot this api')
            cart_items = CartItems.objects.filter(user=request.user)
            add=Address.objects.filter(user=request.user)

            
            coupon=request.session.get('coupon') if request.session.get('coupon') else "Apply coupon"
            count = cart_items.count()
            total_price = 0
            for item in cart_items:
                total_price += item.total_price - item.discount
            discount=0
            for itm in cart_items:
                discount+=itm.discount

            total=total_price+discount
            request.session["discount"] = discount
            print('discount',discount)
            razorpay_key_id = os.getenv('RAZORPAY_KEY_ID') or 'rzp_test_S0yLGz7vAs7dYf'
            razorpay_key_secret = os.getenv('RAZORPAY_KEY_SECRET') or '03wmNfbrN6kxUtYDgE9XywDn'
            client=razorpay.Client(auth=(razorpay_key_id,razorpay_key_secret))
            payment=client.order.create({'amount':int(total_price)*100,'currency':'INR','payment_capture':0})
            payment_id=payment['id']
            return render(request, 'checkout.html', {'cart_items': cart_items, 'count': count, 'total_price': total_price,'add':add,'payment_id':payment_id,'code':coupon,'discount':discount,'total':total})

def apply_coupon(request):
    if request.method == 'POST':
        print('apply coupon has been called')
        coupon = request.POST.get('coupon_code')
        print(coupon)
        couponDetail = Coupon.objects.get(coupon_code=coupon)
        print(couponDetail)
        cartDetails = CartItems.objects.filter(user=request.user)
        print(couponDetail.coupon_code)
        request.session["coupon"] = couponDetail.coupon_code
        total_price=0
        for obj in cartDetails:
            
            discountAmount = (obj.total_price * Decimal(couponDetail.discount)) / 100
            print(discountAmount)
            # obj.total_price -= discountAmount
            obj.coupon = couponDetail
            obj.discount = discountAmount
            obj.save()
            total_price = obj.total_price - obj.discount
            print(total_price)
        return JsonResponse({'message': 'Coupon has been applied.', 'total_price': total_price})

def update_cart(request):
    if request.method=="POST":
        prod_id=int(request.POST.get('product_id'))
        if(CartItems.objectst.filter(user=request.user, product_id=prod_id)):
            prod_qty=int(request.POST.get('product_stock'))
            cart=CartItems.objects.get(product_id=prod_id,user=request.user)
            cart.product_qty=prod_qty
            cart.save()
            return JsonResponse({"status":"Updated successfully"}) 


def add_to_cart(request, id):
    product = Product.objects.get(id=id)
    if request.user.is_authenticated:
        
        cart_item = CartItems.objects.filter(product=product, user=request.user)
        if cart_item.exists():
            cart_item = cart_item.first()
            cart_item.quantity += 1
            cart_item.total_price = cart_item.quantity * cart_item.unit_price
            cart_item.save()
        else:
            cart_item = CartItems.objects.create(product=product, user=request.user, quantity=1, unit_price=product.price, total_price=product.price)
        messages.success(request,'Product added to cart')
        return redirect('product_view_sorting')
    else:
        if not request.session.session_key:
            request.session.create()
        request.session['guest_key']=request.session.session_key
        guest_cart = GuestCart.objects.filter(product=product,user_ref = request.session['guest_key'])
        if guest_cart.exists():
            guest_cart = guest_cart.first()
            guest_cart.quantity += 1
            guest_cart.total_price = guest_cart.quantity * guest_cart.unit_price
            guest_cart.save()
        else:
            guest_cart = GuestCart.objects.create(product=product,user_ref = request.session['guest_key'],quantity = 1,unit_price=product.price,total_price=product.price)
        guest_cart = GuestCart.objects.filter(user_ref = request.session['guest_key'])
        count = guest_cart.count()
        messages.success(request,'Product added to cart')
        return redirect('product_view_sorting')

def view_cart(request):
    print('tttttttttttttttt')
    if request.user.is_authenticated:
        print('oooooooooooooo')
        cart_items = CartItems.objects.filter(user=request.user)
        count = cart_items.count()
        total_price = 0
        for item in cart_items:
            if item.total_price is not None:
                total_price += item.total_price
        print("hhhhhhhhhhhhhhhhhhhhhh",total_price)
        return render(request, 'cart.html', {'cart_items': cart_items, 'count': count, 'total_price': total_price})
    else:
        if not request.session.session_key:
            print('view_cart function called when guest user')
            request.session.create()
        request.session['guest_key'] = request.session.session_key
        guest_cart = GuestCart.objects.filter(user_ref=request.session['guest_key'])
        count = guest_cart.count()
        total_price = 0
        for item in guest_cart:
            total_price += item.total_price
        return render(request, 'cart.html', {'cart_items': guest_cart, 'count': count, 'total_price': total_price})

@csrf_exempt
def update_quantity(request):
    print("aaaaaaaa")
    if request.user.is_authenticated:
        print('sssssssssssssss')
        item_id = request.POST.get('item_id')
        new_quantity = request.POST.get('new_quantity')
        item = CartItems.objects.get(id=item_id)
        item.quantity = new_quantity
        #item.total_price = item.unit_price * item.quantity
        item.total_price = (item.unit_price * Decimal(item.quantity)).quantize(Decimal('0.00'))
        item.save()
        total_price = CartItems.objects.filter(user=request.user).aggregate(Sum('total_price'))
        return JsonResponse({ 'new_total_price': total_price['total_price__sum']})
    else:
        item_id = request.POST.get('item_id')
        new_quantity = request.POST.get('new_quantity')
        item = GuestCart.objects.get(id=item_id)
        item.quantity = new_quantity
        
        item.total_price = (item.unit_price * Decimal(item.quantity)).quantize(Decimal('0.00'))
        item.save()
        total_price = GuestCart.objects.filter(user_ref = request.session['guest_key']).aggregate(Sum('total_price'))
        return JsonResponse({ 'new_total_price': total_price['total_price__sum']})

def check_stock(request):
    if request.user.is_authenticated:
        item_id = request.GET.get('item_id')
        item = CartItems.objects.get(id=item_id)
        stock_level = item.product.stock
        data = {'stock_level': stock_level}
        return JsonResponse(data)

def save_details(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            address1=request.POST['address1']
            city=request.POST['city']
            postcode=request.POST['postcode']
            phone=request.POST['phone']
            country=request.POST['country']
            # if Address.objects.filter(user=request.user).count() >= 5:
            #     address = Address.objects.filter(user=request.user)
            #     return render(request, 'checkout.html', {'address_limit_exceeded': True,'address': address})
            add=Address(user=request.user,address1=address1,city=city,postcode=postcode,phone=phone,country=country)
            add.save()
        return redirect(checkout)
    return redirect(index)

@login_required
def place_order(request):
    print("dxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("qwwfwer",request.POST.get)
    if request.method == 'POST':
        if 'saveaddress' in request.POST:
            address1=request.POST['address1']
            city=request.POST['city']
            postcode=request.POST['postcode']
            phone=request.POST['phone']
            country=request.POST['country']
            add=Address(user=request.user,address1=address1,city=city,postcode=postcode,phone=phone,country=country)
            add.save()
        else:
            neworder = Order()
            neworder.user = request.user
            neworder.address = Address.objects.get(pk=request.POST['address'])
            neworder.discount= request.session.get('discount')
            address_pk = request.session.get('addressId')
            print(neworder.address)
            neworder.payment_method = request.POST.get('payment_method')
            print(neworder.payment_method)
            now = timezone.now()
            ord2 = str(datetime.now()) + str(request.user.id) + str(random.randint(0, 100))
            ord1 = ord2.translate({ord(':'): None, ord('-'): None, ord(' '): None, ord('.'): None}) 
            neworder.order_id = ord1
            if not neworder.address:
                return redirect('checkout')
            total_amount =0
            cartItems = CartItems.objects.filter(user=request.user)
            print('got cart items')
            for item in cartItems:
                print('looping')
                total_amount += item.total_price - item.discount
            print("total_price",total_amount)
            neworder.total_price = total_amount
            neworder.discount= request.session.get('discount')
            neworder.total=neworder.total_price+neworder.discount

            neworder.save()
            neworderitems = CartItems.objects.filter(user=request.user)
            for item in neworderitems:
                Orderitem.objects.create(
                    order=neworder,
                    product=item.product,
                    product_price=item.unit_price * item.quantity,
                    quantity=item.quantity,
                )
            CartItems.objects.filter(user=request.user).delete()
            return redirect(order_confirmation)
    return redirect(index)

def invoice(request,id):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user,id=id)
        orderitm=Order.objects.filter(id=id)
        return render(request, 'invoice.html',{'order':order,'orderitm':orderitm})  

def cat_view(request,id):
    if request.user.is_authenticated:
        cat = Category.objects.filter(user=request.user,id=id)
        prod=Product.objects.filter(id=id)
        return render(request, 'cat_view.html',{'cat':cat,'prod':prod})

def proceed_to_pay(request):
    neworder = Order()
    neworder.user = request.user
    neworder.address = Address.objects.get(pk=request.POST['address'])
    print(neworder.address)
    neworder.payment_method = request.POST.get('payment_method')
    print(neworder.payment_method)
    now = timezone.now()
    ord2 = str(datetime.now()) + str(request.user.id) + str(random.randint(0, 100))
    ord1 = ord2.translate({ord(':'): None, ord('-'): None, ord(' '): None, ord('.'): None}) 
    neworder.order_id = ord1
    if not neworder.address:
        return redirect('checkout')
    
    total_price = request.POST.get('total_price', Decimal(0))  
    print("total_price",total_price)
    neworder.total_price = total_price
    neworder.save()
    neworderitems = CartItems.objects.filter(user=request.user)
    for item in neworderitems:
        Orderitem.objects.create(
            order=neworder,
            product=item.product,
            product_price=item.unit_price * item.quantity,
            quantity=item.quantity
        )
        CartItems.objects.filter(user=request.user).delete()
        return redirect(index)
    return redirect("checkout")

def order_remove(request,id): 
    order = Order.objects.get(id=id)
    order.delivery_status='cancelled'
    order.save()
    return redirect(checkout)

def product_list_by_category(request, category_name):
    category = Category.objects.get(name=category_name)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'product_list_by_category.html', context)

def set_address(request):
    if request.method == 'POST':
        addressId =request.POST.get('addressId')
        request.session['addressId'] = addressId
        print("called set_address function",addressId)
    return checkout(request) 

def address_list(request):
    if request.user.is_authenticated:
        address=Address.objects.filter(user=request.user)
    return render(request,'address.html',{'address':address})

def delete_address(request,id):
    if request.user.is_authenticated:
        address=Address.objects.get(id=id)
        address.delete()
    return redirect(address_list)

def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id)
    if request.method == 'POST':
        address.address1 = request.POST.get('address1')
        address.city = request.POST.get('city')
        address.country = request.POST.get('country')
        address.postcode = request.POST.get('postcode')
        address.phone = request.POST.get('phone')
        address.save()
        return redirect('address_list')  # Replace 'address_list' with the appropriate URL name for the address list page
    return render(request, 'edit_address.html', {'address': address})

def contact(request):
    return render(request,'contact.html')

def blog(request):
    return render(request,'blog.html')

def order_confirmation(request):
    if request.user.is_authenticated:
        order=Order.objects.filter(user=request.user).order_by('-order_at').first()
        order_items=Orderitem.objects.filter(order=order)

        now=datetime.now()
        return render(request,'order_confirmation.html',{'order':order,'order_items':order_items,'now':now})
    


def search(request):
    search_query = request.GET.get('search')
    if search_query:
        search_vector = SearchVector('name',)
        search_query = SearchQuery(search_query, config='english')
        products = Product.objects.annotate(
            search=search_vector, 
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')
    else:
        products = Product.objects.all() 
    return render(request, 'products.html', {'products': products})