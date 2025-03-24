import os
from dataclasses import dataclass, field

import stripe
from dotenv import load_dotenv
from stripe import Charge
from stripe.error import StripeError
from typing import Protocol

_ = load_dotenv()

class PaymentProcessor(Protocol):
    def process_transaction(self, customer_data: dict, payment_data: dict) -> Charge:
        ...

class Notifier(Protocol):
    def send_confirmation(self, customer_data: dict ) -> None:
        ...


class CustomerValidator:

    def validate(self, customer_data: dict) -> None:

        if not customer_data.get("name"):
            print("Invalid customer data: missing name")
            raise ValueError("Invalid customer data: missing name")

        if not customer_data.get("contact_info"):
            print("Invalid customer data: missing contact info")
            raise ValueError("Invalid customer data: missing contact info")


class PaymentValidator:

    def validate(self, payment_data: dict) -> None:

        if not payment_data.get("source"):
            print("Invalid payment data")
            raise ValueError("Invalid payment data")


class StripePaymentProcessor():
    def process_transaction(self, customer_data, payment_data) -> Charge:

        stripe.api_key = os.getenv("STRIPE_API_KEY")
        try:
            charge = stripe.Charge.create(
                amount=payment_data["amount"],
                currency="usd",
                source=payment_data["source"],
                description="Charge for " + customer_data["name"],
            )
            print("Payment successful")
            return charge
        except StripeError as e:
            print("Payment failed:", e)
            raise e


class EmailNotifier():
    def send_confirmation(self, customer_data: dict) -> None:
    
        # import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText("Thank you for your payment.")
        msg["Subject"] = "Payment Confirmation"
        msg["From"] = "no-reply@example.com"
        msg["To"] = customer_data["contact_info"]["email"]

        # server = smtplib.SMTP("localhost")
        # server.send_message(msg)
        # server.quit()
        print("Email sent to", customer_data["contact_info"]["email"])


class SMSNotifier():
    def send_confirmation(self, customer_data: dict) -> None:
        phone_number = customer_data["contact_info"]["phone"]
        sms_gateway = "the custom SMS Gateway"
        print(
            f"send the sms using {sms_gateway}: SMS sent to {phone_number}: Thank you for your payment."
        )



class TransactionLogger:

    def log(self, customer_data: dict, payment_data: dict, charge: Charge) -> None:
        with open("transactions.log", "a") as log_file:
            log_file.write(
                f"{customer_data['name']} paid {payment_data['amount']}\n"
            )
            log_file.write(f"Payment status: {charge['status']}\n")




@dataclass
class PaymentService:
    customer_validator = CustomerValidator()
    payment_validator = PaymentValidator()
    payment_processor: PaymentProcessor = field(default_factory=StripePaymentProcessor)
    notifier: Notifier = field(default_factory=EmailNotifier)
    transaction_logger = TransactionLogger()

    def process_transaction(self, customer_data: dict, payment_data: dict) -> Charge:
        self.customer_validator.validate(customer_data)
        self.payment_validator.validate(payment_data)
        charge = self.payment_processor.process_transaction(customer_data, payment_data)
        self.notifier.send_confirmation(customer_data)
        self.transaction_logger.log(customer_data, payment_data, charge)
        return charge





if __name__ == "__main__":

    # Example 1: Phone notification
    # -------------------------------------

    payment_processor = PaymentService(
        notifier=SMSNotifier()
    )

    customer_data_with_phone = {
        "name": "John Doe",
        "contact_info": {"phone": "1234567890"},
    }

    payment_data = {"amount": 500, "source": "tok_mastercard", "cvv": 123}

    payment_processor.process_transaction(
        customer_data_with_phone, payment_data
    )

    # Example 2: Email notification
    # -------------------------------------

    payment_processor = PaymentService(
        notifier=EmailNotifier()
    )

    customer_data_with_email = {
        "name": "Platzi Python",
        "contact_info": {"email": "e@mail.com"},
    }

    payment_processor.process_transaction(
        customer_data_with_email, payment_data
    )
