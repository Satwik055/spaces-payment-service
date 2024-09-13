from flask import Flask, jsonify, request, redirect
import psycopg2
import stripe

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger("main")


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
    customer_name= "Jenny Rosen",
    user_id = "23",
    customer_address = {
        "line1": "510 Townsend St",
        "postal_code": "98140",
        "city": "San Francisco",
        "state": "CA",
        "country": "US",
        }, 
    
        
    # user_id = data['user_id']
    # customer_name = data['name'] 
    # customer_address = data['address']

    
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
        
        create_payment(user_id, checkout_session.id)
        
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

@app.route('/payment-sheet', methods=['POST'])
def payment_sheet():
        
    data = request.get_json()
    
    user_id = data['user_id']
    customer_name = data['name'] 
    customer_address = data['address']


    try:
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
        
        create_payment(user_id, paymentIntent.id)
        
        
        return jsonify(
            payment_intent = paymentIntent.client_secret,
            ephemeral_key = ephemeralKey.secret,
            customer = my_customer.id,
            publishable_key = stripe_publishable_key
            )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

        


#--------Database operations-----#

def create_payment(user_id:int, payment_id:str):
    try:
        cursor.callproc('create_payment', [user_id, payment_id])
        response = cursor.fetchone()
        print(response)

    except Exception as e:
        print("Failed to insert data:", e)
        

        
        
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    endpoint_secret = "whsec_9a28113c103c239ba9a69d9f36aa09b9aa01017115e697908621c86584bd15a3"
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment_intent_id = payment_intent['id']
            
            cursor.callproc('update_payment_status', [payment_intent_id, 'COMPLETED'])
            
        elif event['type'] == 'payment_intent.canceled':
            payment_intent = event['data']['object']
            payment_intent_id = payment_intent['id']
            
            cursor.callproc('update_payment_status', [payment_intent_id, 'CANCELLED'])

        return jsonify(success=True)

    except ValueError as e:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({"error": "Invalid signature"}), 400
        
        
        
if __name__ == '__main__':
    app.run()