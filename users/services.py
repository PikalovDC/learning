import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_payment_session(course_name, amount):
    """
    Создает продукт, цену и сессию оплаты в Stripe
    Возвращает URL для оплаты
    """
    # Создаем продукт
    product = stripe.Product.create(
        name=course_name,
        type='service'
    )

    # Создаем цену (amount в рублях, переводим в копейки)
    price = stripe.Price.create(
        product=product.id,
        unit_amount=int(amount * 100),
        currency='rub',
    )

    # Создаем сессию оплаты
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price.id,
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:8000/success/',
        cancel_url='http://localhost:8000/cancel/',
    )

    return session.id, session.url, product.id, price.id
