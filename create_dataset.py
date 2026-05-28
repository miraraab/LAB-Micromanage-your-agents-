from dotenv import load_dotenv
load_dotenv()

from langsmith import Client

client = Client()

# 15 Customer Support FAQ Beispiele
examples = [
    {"question": "How do I reset my password?", 
     "answer": "Go to the login page, click 'Forgot Password', enter your email, and follow the instructions sent to you."},
    {"question": "How can I cancel my subscription?", 
     "answer": "Go to Account Settings > Subscription > Cancel Plan. Cancellation takes effect at the end of the billing period."},
    {"question": "What payment methods do you accept?", 
     "answer": "We accept Visa, Mastercard, American Express, and PayPal."},
    {"question": "How do I contact customer support?", 
     "answer": "You can reach us via live chat on our website, email at support@company.com, or phone Mon-Fri 9am-5pm."},
    {"question": "Can I get a refund?", 
     "answer": "Yes, we offer full refunds within 30 days of purchase. Contact support with your order number."},
    {"question": "How do I update my billing information?", 
     "answer": "Go to Account Settings > Billing > Update Payment Method and enter your new details."},
    {"question": "Why was my account suspended?", 
     "answer": "Accounts are suspended for violations of our Terms of Service or failed payments. Contact support for details."},
    {"question": "How do I change my email address?", 
     "answer": "Go to Account Settings > Profile > Edit Email. A confirmation will be sent to your new address."},
    {"question": "Is my data secure?", 
     "answer": "Yes, we use 256-bit SSL encryption and are fully GDPR compliant. Your data is never sold to third parties."},
    {"question": "How do I download my invoice?", 
     "answer": "Go to Account Settings > Billing > Invoice History and click Download next to the relevant invoice."},
    {"question": "Can I use the service on multiple devices?", 
     "answer": "Yes, you can use your account on up to 3 devices simultaneously with a standard plan."},
    {"question": "How do I upgrade my plan?", 
     "answer": "Go to Account Settings > Subscription > Upgrade Plan and select your desired tier."},
    {"question": "What happens to my data if I cancel?", 
     "answer": "Your data is retained for 30 days after cancellation, then permanently deleted unless you reactivate."},
    {"question": "How do I enable two-factor authentication?", 
     "answer": "Go to Account Settings > Security > Enable 2FA and follow the setup instructions."},
    {"question": "Do you offer a free trial?", 
     "answer": "Yes, we offer a 14-day free trial with full access. No credit card required."},
]

# Dataset erstellen
dataset_name = "customer-support-faq-v1"

# Prüfen ob bereits existiert
existing = [d for d in client.list_datasets() if d.name == dataset_name]
if existing:
    print(f"⚠️  Dataset '{dataset_name}' existiert bereits – wird übersprungen")
else:
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Customer support FAQ examples for LLM evaluation"
    )

    client.create_examples(
        inputs=[{"question": e["question"]} for e in examples],
        outputs=[{"answer": e["answer"]} for e in examples],
        dataset_id=dataset.id
    )
    print(f"✅ Dataset erstellt: {dataset_name}")
    print(f"✅ {len(examples)} Beispiele hochgeladen")