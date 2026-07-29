import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:

    @staticmethod
    def create_checkout(payment):
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "unit_amount": int(payment.price * 100),
                        "product_data": {
                            "name": f"Flight #{payment.ticket.flight.id}",
                        },
                    },
                    "quantity": 1,
                }
            ],
            metadata={"payment_id": payment.id,},
            success_url="http://localhost:8000/payment/success",
            cancel_url="http://localhost:8000/payment/cancel",)
        payment.stripe_checkout_session_id = session.id
        payment.save(update_fields=["stripe_checkout_session_id"])

        return session