from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import  User

STATUS_CHOICES = [
    ('delivered', 'Delivered'),
    ('onway', 'Onway'),
    ('pending', 'Pending'),
    ('dispatched', 'Dispatched'),
    ('cancelled', 'Cancelled'),
    ('returned', 'Returned'),

]


CATEGORY_CHOICES = [
    ('clothes', 'Clothes'),
    ('electronics', 'Electronics'),
    ('fashion', 'Fashion'),
    ('grocery', 'Grocery'),
    ('home', 'Home'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', null=True, blank=True)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.user.username} Profile'



class Category(models.Model):
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
    

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('unisex', 'Unisex')])
    class Meta:
        verbose_name_plural = 'SubCategories'

    def __str__(self):
        return self.name



class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    price = models.FloatField()
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    status = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0)
    discount = models.IntegerField(default=0, null=True, blank=True)  # Discount percentage
    date = models.DateField(auto_now_add=True)
    

    class Meta:
        ordering = ['-date']
    @property
    def price_with_discount(self):
        return self.price * (1 - self.discount / 100)

    def __str__(self):
        return self.name
    
    
class ProductAtribute(models.Model):
    product = models.ForeignKey(Product, related_name='attribute', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class Rating(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE,)
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        product = self.content_object
        return f"{self.stars} stars for {product} by {self.user}" if product else None
    

class PaymentMethod(models.Model):
    name = models.CharField(
        max_length=100, 
        choices=[
            ('visa', 'Visa'), ('mastercard', 'Mastercard'),
            ('paypal', 'PayPal'), ('applepay', 'ApplePay'),
            ('googlepay', 'GooglePay')
            ]
        )

    def __str__(self):
        return self.name



class Payment(models.Model):
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    unit_price = models.FloatField()
  

    def __str__(self):
        return self.product.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return self.user.username


class NNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    
class Shipping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username