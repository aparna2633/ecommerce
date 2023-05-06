from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
import datetime
from datetime import datetime
import xlwt
from store.models import Account
from product.models import Product,Category,SubCategory,Orderitem,Order,Banner
from django.contrib.auth.models import User
from .forms import *
from product.forms import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.postgres.search import SearchVector
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db import IntegrityError
import io,csv
# Create your views here.

@never_cache
def adminLogin(request):
    if request.user.is_authenticated and request.user.is_staff and request.user.is_admin:
        return redirect(adminHome)
    # if request.user.is_authenticated:
    #     return redirect()
    if request.method=='POST':
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email,password=password)
            if user is not None:
                if not user.is_staff:
                    messages.error(request, "You are not authorized to access this webpage!!!")
                    return render(request, 'admin_login.html')
                login(request,user)
                #messages.success(request, 'Successfully logged in')
                return redirect(adminHome)
            else:
                messages.error(request, 'EmailId or Password is wrong!')
                return redirect(adminLogin)
    return render(request,'admin_login.html')



@never_cache
def adminHome(request):
    if request.user.is_authenticated and request.user.is_staff:
        order = Order.objects.all()
        products = Product.objects.all()
        customers = Account.objects.all()
        order = order.count()
        product = products.count()
        customers = customers.count()


        total_price = Order.objects.filter(delivery_status='Delivered').aggregate(Sum('total_price'))['total_price__sum']
        a =[]
        for i in products:
            z = Orderitem.objects.filter(product_id=i.id).values('order')
            o = Order.objects.filter(id__in=z,delivery_status='Delivered').aggregate(Sum('total_price'))

            if o['total_price__sum'] is None or o is None:
                a.append({'title':i.name,'price':0})
            else:
                a.append({'title':i.name,'price':o['total_price__sum']})
            
        deliveredOrder = Order.objects.filter(delivery_status='Delivered')
        days=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        months =['January','February',' March','April','May','June','July','August','September','October','November','December']
        daily = []
        monthly = []

        #daily wise sales 
        for day in days:
            count = 0
            for dayObj in deliveredOrder:
                dayStr = dayObj.order_at.strftime("%A")
                if day == dayStr:
                    count += 1
               
            daily.append(count)
        
        #monthly wise sales
        for month in months:
            count = 0
            for monthObj in deliveredOrder:
                monthStr = monthObj.order_at.strftime("%B")
                if month == monthStr:
                    count += 1
               
            monthly.append(count)

        context = {
                'order_count':order,
                'total_price': total_price,
                'product_count':product,
                'customers_count': customers,  
                'a':a,
                "daily":daily,
                "monthly":monthly
                }
        
        
        return render(request, 'adminhome.html',context)
    return redirect(adminLogin)

    # if request.user.is_authenticated and request.user.is_staff:
    #     records = Account.objects.all()
    #     print(records)
    #     return render(request,'adminhome.html',{'records':records}) 
    # return redirect(adminHome)
@never_cache
def user_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        records = Account.objects.all().order_by('id')
        print(records)
        if request.method == 'GET'and request.GET.get('search') is not None:
            print(request.GET)
            search_query = request.GET.get('search')
            records = Account.objects.annotate(search=SearchVector('name','email')).filter(search=request.GET.get('search'))
            paginator = Paginator(records, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'records': page_obj, 'search_query': search_query, 'paginator': paginator}
            return render(request, 'user_management.html',context)
        paginator = Paginator(records, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'records': page_obj, 'paginator': paginator}
        return render(request, 'user_management.html', context)
        return render(request, 'user_management.html',{'records':records})
    return redirect(adminLogin)

def block(request,id):
    if request.user.is_authenticated and request.user.is_active and request.user.is_staff:
        flag = Account.objects.all().values('is_active').get(id=id)
        if flag['is_active'] == True:
            Account.objects.filter(id=id).update(is_active=False)
            return redirect(user_management)
        else:
            Account.objects.filter(id=id).update(is_active=True)
            return redirect(user_management)
    return redirect(user_management)
        

def product_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        products= Product.objects.all().order_by('id')
        print(products)
        if request.method == 'GET'and request.GET.get('search') is not None:
            print(request.GET)
            products = Product.objects.annotate(search=SearchVector('name')).filter(search=request.GET.get('search'))
            return render(request, 'product_management.html',{'products':products})

        return render(request, 'product_management.html',{'products':products})
    return redirect(adminLogin)

    
@never_cache
def add_product(request):
    if request.user.is_authenticated and request.user.is_staff:
        form = ProductForm()
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)

                # Check if the image fields are present and save only those that are filled
                if 'image1' in request.FILES:
                    product.image1 = request.FILES['image1']
                if 'image2' in request.FILES:
                    product.image2 = request.FILES['image2']
                if 'image3' in request.FILES:
                    product.image3 = request.FILES['image3']
                if 'image4' in request.FILES:
                    product.image4 = request.FILES['image4']

                product.save()
                return redirect(product_management)
            print(form.errors)
        else:
            categories = Category.objects.all()
            subcategories = SubCategory.objects.all()
            return render(request, 'add_product.html', {'form': form, 'categories': categories, 'subcategories': subcategories})

    return redirect(product_management)


def edit_product(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        product = Product.objects.get(id=id)
        path = request.path
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                return redirect(product_management)
        else:
            product = Product.objects.get(id=id)
            form = ProductForm(instance=product)
            return render(request, 'edit_product.html', context={'form': form,'path': path})
    return redirect(product_management)

def delete_product(request,id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=id)
        product.delete()
        #messages.success(request, "Deleted a record successfully.")
        return redirect(product_management)
    return redirect(product_management)

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id)
    data = [{'id': subcategory.id, 'name': subcategory.name} for subcategory in subcategories]
    return JsonResponse(data, safe=False)



def category_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        category= Category.objects.all().order_by('id')
        print(category)
        if request.method == 'GET'and request.GET.get('search') is not None:
            print(request.GET)
            category= Category.objects.annotate(search=SearchVector('name')).filter(search=request.GET.get('search'))
            return render(request, 'category_management.html',{'category':category})

        return render(request, 'category_management.html',{'category':category})
    return redirect(category_management)

def add_category(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            try:
                name = request.POST['name']
                offer = request.POST['offer']
                category = Category(name=name, offer=offer)
                category.save()
                return redirect(category_management)
            except IntegrityError:
                error_message = 'Category name already exist Please choose another name.'
            return render(request, 'add_category.html', {'error_message': error_message})

    return render(request, 'add_category.html')



def coupon_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        coupon= Coupon.objects.all().order_by('id')
        print(coupon)
        if request.method == 'GET'and request.GET.get('search') is not None:
            print(request.GET)
            search_query = request.GET.get('search')
            order = Order.objects.annotate(search=SearchVector('items_product_name', 'order_id','payment_method', 'delivery_status')).filter(search=search_query).distinct()            
            paginator = Paginator(coupon, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'order': page_obj, 'search_query': search_query, 'paginator': paginator}
            return render(request, 'order_management.html',context)
    
        paginator = Paginator(coupon, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'coupon': page_obj, 'paginator': paginator}
        return render(request, 'coupon_management.html',context)

        return render(request, 'coupon_management.html',{'coupon':coupon})
    return redirect(coupon_management)

def add_coupon(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            coupon_code = request.POST['coupon_code']
            discount = request.POST['discount']
            try:
                coupon = Coupon(coupon_code=coupon_code, discount=discount)
                coupon.save()
                return redirect(coupon_management)
            except IntegrityError:
                error_message = 'Coupon with this code already exists. Please choose a different code.'
            return render(request, 'add_coupon.html', {'error_message': error_message})

        return render(request, 'add_coupon.html')
    
def delete_coupon(request,id):
    if request.user.is_authenticated:
        coupon= Coupon.objects.get(id=id)
        coupon.delete()
        messages.success(request, f"Deleted brand successfully.")
        return redirect(coupon_management)
    return redirect(adminHome)

def edit_category(request,id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            name = request.POST['name']
            offer = request.POST['offer']
            Category.objects.filter(id=id).update(name=name,offer=offer)
        else:
            data = Category.objects.get(id=id)
            return render(request, 'edit_category.html',{'category':data})
    #messages.success(request, "Details have been Updated")
    return redirect(category_management)

def delete_category(request,id):
    if request.user.is_authenticated:
        category = Category.objects.get(id=id)
        category.delete()
        #messages.success(request, "Deleted a record successfully.")
        return redirect(category_management)
    return redirect(adminHome)

def sub_category(request):
    if request.user.is_authenticated and request.user.is_staff:
            subcategory= SubCategory.objects.all().order_by('id')
            print(subcategory)
            if request.method == 'GET'and request.GET.get('search') is not None:
                print(request.GET)
                subcategory= SubCategory.objects.annotate(search=SearchVector('name')).filter(search=request.GET.get('search'))
                return render(request, 'subcategory_manage.html',{'subcategory':subcategory})

            return render(request, 'subcategory_manage.html',{'subcategory':subcategory})
    return redirect(adminHome)


def add_sub_cat(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            name = request.POST['name']
            category_id = request.POST['category']
            category = Category.objects.get(id=category_id)
            subcategory=SubCategory(name=name,category=category)
            subcategory.save()
            return redirect(sub_category)
        categories = Category.objects.all()
        return render(request, 'add_subcategory.html',{'categories': categories})
    return redirect(sub_category)

def edit_sub_cat(request,id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            name = request.POST['name']
            SubCategory.objects.filter(id=id).update(name=name)
        else:
            data = SubCategory.objects.get(id=id)
            return render(request, 'edit_subcategory.html',{'subcategory':data})
    #messages.success(request, "Details have been Updated")
    return redirect(sub_category)

def delete_sub_cat(request,id):
    if request.user.is_authenticated:
        subcategory = SubCategory.objects.get(id=id)
        subcategory.delete()
        #messages.success(request, "Deleted a record successfully.")
        return redirect(sub_category)
    return redirect(adminHome)




@never_cache
def adminLogout(request):
    if request.user.is_authenticated and request.user.is_staff:
        logout(request)
        print("LoggedOut")
        messages.success(request, 'Logged Out Successfully')
        return redirect(adminLogin)
    return render(request,'admin_login.html')


# def order_management(request):
#     if request.user.is_authenticated and request.user.is_staff:
#         orderitem= Orderitem.objects.all().order_by('id')
#         order=Order.objects.all().order_by('id')
#         print(orderitem)
#         if request.method == 'GET'and request.GET.get('search') is not None:
#             print(request.GET)
#             category= Orderitem.objects.annotate(search=SearchVector('order_id','payment_method','product.name')).filter(search=request.GET.get('search'))
#             return render(request, 'order_management.html',{'orderitem':orderitem,'order':order})
#         return render(request, 'order_management.html',{'orderitem':orderitem,'order':order})
#     return redirect(order_management)

def delivery_status(request, id):
    order = Order.objects.get(id=id)
    if order.delivery_status == 'Pending':
        order.delivery_status = 'Shipped'
    elif order.delivery_status == 'Shipped':
        order.delivery_status = 'Out for delivery'
    elif order.delivery_status == 'Out for delivery':
        order.delivery_status = 'Delivered'
    order.save()
    return redirect(order_management)

def order_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        order = Order.objects.all().order_by('id')
        order_items = Orderitem.objects.all()
        print("orderitems-------->",order_items)
        print(order)

        if request.method == 'GET' and request.GET.get('search') is not None:
            print(request.GET)
            search_query = request.GET.get('search')
            # order = Order.objects.annotate(search=SearchVector('name')).filter(search=search_query)
            order = Order.objects.annotate(search=SearchVector('items_product_name', 'order_id','payment_method', 'delivery_status')).filter(search=search_query).distinct()
            paginator = Paginator(order, 5)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {'order': page_obj, 'search_query': search_query, 'paginator': paginator}
            return render(request, 'order_management.html',context)
    
        paginator = Paginator(order, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'order': page_obj, 'paginator': paginator}
        return render(request, 'order_management.html', context)
    return redirect(order_management)



def banner_management(request):
    if request.user.is_authenticated and request.user.is_staff:
        banner = Banner.objects.all() 
        return render(request,'banner.html',{'banner':banner})
    
def add_banner(request):
    if request.method == 'POST':
        title = request.POST['title']
        image = request.FILES['image']
        banner1 = Banner.objects.create(title=title,  image=image)
        return redirect(banner_management)
    else:
        return render(request, 'add_banner.html')
    

def edit_banner(request,id):
    if request.user.is_authenticated:
        banner = Banner.objects.get(id=id)
        if request.method == 'POST':
            title = request.POST['title']
            image = request.FILES.get('image')
            banner.title1 = title
            if image:
                banner.image = image
            banner.save()
            messages.success(request, "Banner Updated")
            return redirect(banner_management)
        return render(request,'edit_banner.html',{'banner':banner})
    return redirect(banner_management)



def delete_banner(request,id):
    if request.user.is_authenticated:
        banner1= Banner.objects.get(id=id)
        banner1.delete()
        messages.success(request, f"Deleted brand successfully.")
        return redirect(banner_management)
    return redirect(adminHome)


from django.core.paginator import Paginator

def sales(request):
    if request.user.is_authenticated and request.user.is_staff:
        today = datetime.now()
        #orders = Order.objects.filter(order_at__year=today.year, order_at__month=today.month)
        orders = Order.objects.filter(delivery_status='Delivered',order_at__year=today.year, order_at__month=today.month).order_by('-order_at')
        total_sales = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        #total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
        paginator = Paginator(orders, 10)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'orders': page_obj,
            'total_sales': total_sales,
            'paginator': paginator,
            'page_obj': page_obj,
        }
        return render(request, 'sales.html', context)
    return redirect(adminLogin)


def sales_excel_report(request):
    orders = Order.objects.all()
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sales_report.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sales Report')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Order ID', 'User', 'Items', 'Total Price', 'Payment Method', 'Order At']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()
    for order in orders:
        row_num += 1
        row = [
            order.id,
            order.user.name,
            ', '.join([f'{item.product.name} ({item.quantity})' for item in order.items.all()]),
            order.total_price,
            order.payment_method,
            order.delivery_status,
            order.order_at.strftime('%d-%m-%Y %H:%M:%S')
        ]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response

def sales_csv_report(request):
    orders = Order.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'User', 'Items', 'Total Price', 'Payment Method', 'Order At'])
    for order in orders:
        writer.writerow([
            order.id,
            order.user.name,
            ', '.join([f'{item.product.name} ({item.quantity})' for item in order.items.all()]),
            order.total_price,
            order.payment_method,
            order.delivery_status,
            order.order_at.strftime('%d-%m-%Y %H:%M:%S')
        ])
    return response





def sales_filter(request):
    print('sales_filter function called')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    print('step1')
    # Convert the start and end dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    print('step2')

    # Perform the filtering based on the date range
    orders = Order.objects.filter(
        delivery_status='Delivered',
        order_at__date__range=[start_date, end_date]
    ).order_by('-order_at')
    print(start_date,end_date)

    total_sales = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    print(total_sales)
    context = {
        'orders': orders,
        'total_sales': total_sales,
    }
    print(orders,total_sales)

    # Render the filtered sales report as HTML table
    return render(request, 'sales.html', context)
    