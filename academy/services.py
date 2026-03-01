import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


class StripeService:
    @staticmethod
    def create_product(product_name, product_description):
        """Создание продукта"""
        return stripe.Product.create(
            name=product_name,
            description=product_description,
        )

    @staticmethod
    def create_price(product, product_price):
        """Создание цены для продукта для разового платежа"""
        return stripe.Price.create(
            product=product.id,
            unit_amount=product_price,  # Цена в минимальных единицах валюты (20.00)
            currency="usd",  # Валюта
        )

    @staticmethod
    def create_checkout_session(price):
        # Создание checkout session с созданной ценой
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price.id,  # ID только что созданной цены
                'quantity': 1,
            }],
            mode='payment',  # Или 'subscription' для подписок
            success_url='https://example.com/success',
            cancel_url='https://example.com/cancel',
        )

        # Получение URL для оплаты
        payment_url = checkout_session.url
        print(f"Ссылка для оплаты: {payment_url}")
        return payment_url
