from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from .models import Payment, Shipping, Product, Wishlist
from notifications.signals import notify

@receiver(post_save, sender=Payment)
def notify_payment(sender, instance,created, **kwargs):
        
    product = instance.product
    seller = product.user
    customer = instance.user
    notify.send(instance, recipient=seller, verb='you reached level 10',description=f'customer have successfully paid for {product.name}.')
    notify.send(instance, recipient=customer, verb='you reached level 10',description=f'You have successfully paid for {product.name}.')

@receiver(post_save, sender=Payment)
def quantity_control(sender, instance,created, **kwargs):
        
    product = instance.product
    product.quantity=product.quantity - 1
    product.save()


@receiver(post_save, sender=Payment)
def ship(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        customer = instance.user

        Shipping.objects.create(
            user=customer,
            product=product,
            address=customer.profile.address, 
            city=customer.profile.city,       
            country=customer.profile.country,  
            status='pending'
        )



@receiver(post_save, sender=Product)
def notify_user_discount(sender,instance,validated_data, product_id, old_discount, new_discount, **kwargs):
    try:
        product = Product.objects.get(id=product_id)
        wishlists = Wishlist.objects.filter(products__id=product_id)
        old_discount = instance.discount
        new_discount = validated_data.get('discount', instance.discount)

        if old_discount and new_discount is not None:
            if old_discount < new_discount:
                for wishlist in wishlists:
                    user = wishlist.user
                    if user and product:
                        notify.send(
                            sender=product, 
                            recipient=user, 
                            verb='discount applied', 
                            description=f'{product.name} discount has been applied. Old discount: {old_discount}, New discount: {new_discount}.'
                        )
    except Product.DoesNotExist:
        pass
    except Exception as e:
        print(f'An error occurred')