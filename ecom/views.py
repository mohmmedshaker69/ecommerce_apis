from django.db import transaction
from rest_framework.response import Response
from rest_framework import  viewsets
from .models import  SubCategory, Product, Rating, Cart, Payment, Category, NNotification, PaymentMethod, Wishlist, Shipping
from .serializers import SubCategorySerializer, ProductSerializer, CartSerializer, CategorySerializer, UserSerializer, NotificationSerializer, WishlistSerializer, ShippingSerializer
from rest_framework.decorators import action
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from notifications.signals import notify
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
import csv
from django.http import HttpResponse



class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all().prefetch_related('category')
    serializer_class = SubCategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().prefetch_related('sub_category')
    serializer_class = ProductSerializer

    @transaction.atomic
    @action(detail=True, methods=['post'], url_name='add_rating', url_path='add_rating')
    def add_rating(self, request, pk):
        rating = Rating.objects.create(
            user=request.user,
            stars=request.data.get('stars'),
            content_type=ContentType.objects.get_for_model(self.get_object()),
            object_id=pk
        )
        return Response({'success': 'Rating added successfully.'}, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_name='add_to_wishlist', url_path='add_to_wishlist')
    def add_to_wishlist(self, request, pk):
    
        instance = self.get_object()
        wishlist = Wishlist(
            user=request.user,
            product=instance,
        )
        
        try:
            wishlist.save()
        except Exception as e:
            return Response({'error': f'An error occurred while adding the product to your wishlist'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'success': 'Product added successfully.'}, status=status.HTTP_201_CREATED)
    

    @transaction.atomic
    @action(detail=True, methods=['post'], url_name='add_to_cart', url_path='add_to_cart')
    def add_to_cart(self, request, pk):
    
        instance = self.get_object()
        cart = Cart(
            user=request.user,
            product=instance,
            object_id=instance.pk
        )
        
        try:
            cart.save()
        except Exception as e:
            return Response({'error': f'An error occurred while adding the product to your cart: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'success': 'Product added successfully.'}, status=status.HTTP_201_CREATED)
    




    @action(detail=True, methods=['get'], url_path='dashboard', url_name='dashboard')
    def dashboard(self, request, pk=None):
        try:
            products = Product.objects.filter(user=request.user)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': f'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all().prefetch_related('product', 'user')
    serializer_class = CartSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @transaction.atomic
    @action(detail=True, methods=['post'], url_name='pay', url_path='pay')
    def pay(self, request, pk):
        
        instance = self.get_object()
        

        user = request.user

        if user != instance.user:
            return Response({'error': 'You are not authorized to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        payment = Payment(
            user=user,
            product=instance.product,
            unit_price=instance.product.price,
            amount=instance.product.price,
            method=PaymentMethod.objects.get(name='visa'),
        )
        
        try:
            payment.save()
        except Exception as e:

            return Response({'error': f'An error occurred while saving the payment ({str(e)})'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            instance.delete()
        except Exception as e:
            return Response({'error': f'An error occurred while deleting the product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': 'Payment successful.'}, status=status.HTTP_200_OK)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = NNotification.objects.all()


    def get_queryset(self):
        return NNotification.objects.filter(user=self.request.user)
    

    
class SearchProducts(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'category__name', 'sub_category__name', 'price', 'rating__stars']


class WishListApi(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class ShippingApi(viewsets.ModelViewSet):
    queryset = Shipping.objects.all()
    serializer_class = ShippingSerializer



class CSVUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES['file']
        if not file_obj.name.endswith('.csv'):
            return Response({"error": "File is not a CSV"}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file_obj.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        for row in reader:
            serializer = ProductSerializer(data=row)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "success"}, status=status.HTTP_201_CREATED)
    

class CSVExportView(APIView):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_export.csv"'

        writer = csv.writer(response)
        
        writer.writerow(['User Name', 'Product name', 'subcategory','price', 'status', 'quantity'])
        
        for field in Product.objects.all():
            writer.writerow([field.user, field.name, field.subcategory, field.price, field.status, field.quantity])
        
        return response