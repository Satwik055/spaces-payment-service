from flask import Flask, jsonify, request, redirect
import psycopg2
import stripe
import requests


DB_CONFIG = {
    'host': "aws-0-ap-south-1.pooler.supabase.com",
    'database': "postgres",
    'user': "postgres.fayafjrwupqupjltsdeg",
    'password': "@Satwikkr055"
}

YOUR_DOMAIN = 'http://localhost:5000'
stripe_publishable_key = 'pk_test_51IlFYySIaKPCt7ZQaomoRMMVEjhy3CHnGLk6WvTUOzltBfWBLZOM8Gxi8qVfVPNEKl9B5QAuyVluCL6B2NRCfxCo00BE8Faezw'
stripe.api_key = 'sk_test_51IlFYySIaKPCt7ZQOAVwXGDaM1p5457AeYSANyjYxWdP4C4RX60i8JT5YN36dg798rgJx3DIXKdhm7jS67gOjKgj00zQ7OSlk4'
connection = psycopg2.connect(**DB_CONFIG)
cursor = connection.cursor()
app = Flask(__name__)



@app.route("/hello", methods=['GET'])
def hello():
    return "Hello from payment service"


@app.route('/create-checkout-session', methods=['GET','POST'])
def create_checkout_session():
    
    data = request.get_json()
    
    #-----Sample data-----
    # name="Jenny Rosen",
    # address={
    #     "line1": "510 Townsend St",
    #     "postal_code": "98140",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "country": "US",
    #     },
    
    customer_name = data['name'] 
    customer_address = data['address']

    
    try:
        my_customer = stripe.Customer.create(
            name= customer_name,
            address= customer_address
            )
        
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1PwH16SIaKPCt7ZQgyOAlY1n',
                    'quantity': 1,
                },
            ],
        
            customer = my_customer,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

# Success callback route
@app.route('/success', methods=['GET'])
def success():
    return "Payment successful! Thank you for your purchase."

# Fail callback route
@app.route('/cancel', methods=['GET'])
def cancel():
    return "Payment failed or was canceled. Please try again."

@app.route('/payment-sheet', methods=['GET','POST'])
def payment_sheet():
        
    data = request.get_json()
    
    customer_name = data['name'] 
    customer_address = data['address']

    my_customer = stripe.Customer.create(
        name= customer_name,
        address= customer_address
        )
    
    ephemeralKey = stripe.EphemeralKey.create(
        customer=my_customer['id'],
        stripe_version='2020-08-27',
    )

    paymentIntent = stripe.PaymentIntent.create(
        amount=1099,
        currency='usd',
        customer=my_customer['id']
    )
    
    return jsonify(
        paymentIntent=paymentIntent.client_secret,
        ephemeralKey=ephemeralKey.secret,
        customer=my_customer.id,
        publishableKey= stripe_publishable_key
        )

if __name__ == '__main__':
    app.run()