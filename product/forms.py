from django import forms
from .models import CartItems, Product,Category, SubCategory,Coupon

class ProductForm(forms.ModelForm):
    image2 = forms.ImageField(required=False)
    image3 = forms.ImageField(required=False)
    image4 = forms.ImageField(required=False)
    class Meta:
        model = Product
        fields = '__all__'
    def _init_(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control',})
        self.fields['category'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['subcategory'].widget.attrs.update({'style': 'width: 500px;', 'class':'form-control'})
        self.fields['price'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['offer'].widget.attrs.update({'style':'width:500px;','class':'form-control'})
        self.fields['stock'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['brand'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['image1'].widget.attrs.update({'style': 'height: 800px;', 'class': 'form-control'})
        self.fields['image2'].widget.attrs.update({'style': 'height: 800px;', 'class': 'form-control'})
        self.fields['image3'].widget.attrs.update({'style': 'height: 800px;', 'class': 'form-control'})
        self.fields['image4'].widget.attrs.update({'style': 'height: 800px;', 'class': 'form-control'})
        

class CartItemsForm(forms.ModelForm):
    # size = forms.ModelChoiceField(queryset=Size.objects.all())

    class Meta:
        model = CartItems
        fields = ['product', 'quantity']

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

class CouponForm(forms.ModelForm):
    # size = forms.ModelChoiceField(queryset=Size.objects.all())

    class Meta:
        model = Coupon
        fields = ['coupon_code', 'discount']

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)