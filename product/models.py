import datetime
from django.db import models
from store.models import Account
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.d 

class Category(models.Model):
    name = models.CharField(max_length=250, unique=True )
    offer = models.PositiveIntegerField()
    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    offer = models.PositiveIntegerField(default=0)
    stock = models.IntegerField()
    brand = models.CharField(max_length=200)
    image1 = models.ImageField(upload_to="ecom/image")
    image2 = models.ImageField(upload_to="ecom/image")
    image3 = models.ImageField(upload_to="ecom/image")
    image4 = models.ImageField(upload_to="ecom/image")



class Coupon(models.Model):
    coupon_code=models.CharField(max_length=100,null=True,unique=True)
    discount = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)],null=True,default = 0)
   


class CartItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True, blank=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True)
    discount=models.IntegerField(default=0)

class GuestCart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user_ref = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True)


class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id=models.CharField(max_length=120)
    payment_method=models.CharField(max_length=120)
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2)
    status=models.CharField(max_length=120)
    created_at=models.DateTimeField(auto_now_add=True)
    order_id=models.CharField(max_length=200,default=None,unique=True)


class Address(models.Model):
    user= models.ForeignKey (Account, on_delete=models.PROTECT)
    phone=models.CharField(max_length=20)
    address1=models.TextField(max_length=200)
    country=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    postcode=models.IntegerField()



class Order(models.Model):
    payment_choice = (("1", "cod"), ("2", "RAZORPAY"))
    delivery_status_choice =(
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'), 
        ('shipped', 'Shipped'),
        ('out for delivery', 'out for delivery'),
        ('Delivered', 'Delivered'), 
        ('Cancelled', 'cancelled'),
        ('Returned', 'Returned'),
        )
    user= models.ForeignKey (Account, on_delete=models.PROTECT)
    total_price = models.DecimalField(max_digits=6, decimal_places=2) 
    payment_id = models.CharField(max_length=200, null=True)
    payment_method = models.CharField(max_length=200, choices= payment_choice) 
    payment_status = models.BooleanField(default=False)
    delivery_status = models.CharField(max_length=200, choices=delivery_status_choice, default="Pending") 
    status = models.BooleanField(default=True)
    order_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=200, default=None) 
    address = models.ForeignKey(Address, related_name="shipping_address", on_delete=models.SET_NULL, blank=True, null=True)



class Orderitem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product= models.ForeignKey(Product, on_delete=models.CASCADE, max_length=120)
    product_price= models.DecimalField(max_digits=6, decimal_places=2, null=True)
    quantity = models.PositiveIntegerField()


class Wishlist(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='wishlist_products')
    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    added_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.product}added to wishlist"
    
class Banner(models.Model):
    title = models.CharField(max_length=120)
    image = models.ImageField(upload_to="ecom/image")
   