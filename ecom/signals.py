from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment, Shipping
from notifications.signals import notify

@receiver(post_save, sender=Payment)
def notify_payment(sender, instance,created, **kwargs):
        
    product = instance.product
    seller = product.user
    customer = instance.user
    notify.send(instance, recipient=seller, verb='you reached level 10',description=f'You have successfully paid for {product.name}.')



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
