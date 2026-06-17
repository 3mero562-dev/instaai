import os
from openai import OpenAI
from sqlalchemy.orm import Session
import models

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("OPENAI_KEY =", os.getenv("OPENAI_API_KEY"))

def generate_ai_reply(user: models.User, message_text: str, db: Session):
    # Fetch user-specific context from DB
    products = db.query(models.Product).filter(models.Product.user_id == user.id).all()
    faqs = db.query(models.FAQ).filter(models.FAQ.user_id == user.id).all()

    # Format products and FAQs for the AI context
    product_list = "\n".join([f"- {p.name}: {p.price} (Description: {p.description})" for p in products])
    faq_list = "\n".join([f"Q: {f.question}\nA: {f.answer}" for f in faqs])

    # Construct the System Prompt
    system_prompt = f"""
    You are an AI customer service assistant for a business on Instagram.
    
    BUSINESS DESCRIPTION:
    {user.business_description or "A professional business."}
    
    AI INSTRUCTIONS:
    {user.ai_instructions or "Be polite and helpful."}
    
    AVAILABLE PRODUCTS:
    {product_list if product_list else "Ask for specific product details."}
    
    FREQUENTLY ASKED QUESTIONS (FAQs):
    {faq_list if faq_list else "Provide general assistance."}
    
    GUIDELINES:
    1. Respond in the same language as the customer (Arabic or English).
    2. If the user wants to buy a product, encourage them and provide details.
    3. If you cannot answer a specific question based on the info provided, politely ask them to wait for a human agent.
    4. Keep responses concise and suitable for Instagram DM.
    5. Support RTL formatting for Arabic responses.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_text}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return None