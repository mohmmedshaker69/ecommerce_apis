from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, SubCategory, Product, Cart, Profile, NNotification, Wishlist, Shipping, ProductAtribute


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['image']

class UserSerializer(serializers.ModelSerializer):
    image = serializers.CharField(max_length=100, source='profile.image')
    class Meta:
        model = User    
        fields = ['id', 'username','email','password', 'image']

    def create(self, validated_data):
        image = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **image)
        return user



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NNotification
        fields = '__all__'

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'

class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = '__all__'


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAtribute
        fields = ['attribute', 'name', 'quantity']


class ProductSerializer(serializers.ModelSerializer):
    attribute = ProductSizeSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'user', 'name', 'subcategory', 'price', 'description', 'image', 'status', 'quantity', 'attribute']

    def create(self, validated_data):
        attribute_data = validated_data.pop('attribute')
        product = super().create(validated_data)
        for attribute_data in attribute_data:
            ProductAtribute.objects.create(product=product, **attribute_data)
        return product

    def update(self, instance, validated_data):
        attributes_data = validated_data.pop('attribute')
        instance = super().update(instance, validated_data)
        for attribute_data in attributes_data:
            attribute_obj, created = ProductAtribute.objects.update_or_create(
                product=instance,
                attribute=attribute_data.get('attribute'),
                defaults={'quantity': attribute_data.get('quantity')}
            )

        return instance
