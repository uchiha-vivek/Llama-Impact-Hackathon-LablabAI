import os
from dotenv import dotenv_values
import streamlit as st
from groq import Groq
import pdfkit  

def parse_groq_stream(stream):
    response_content = ""
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            response_content += chunk.choices[0].delta.content
            yield chunk.choices[0].delta.content
    return response_content


st.set_page_config(
    page_title="Tax Assistant 🧑‍💼",
    page_icon="💰",
    layout="centered",
)

try:
    secrets = dotenv_values(".env")  
    GROQ_API_KEY = secrets["GROQ_API_KEY"]
except Exception as e:
    
    secrets = st.secrets
    GROQ_API_KEY = secrets["GROQ_API_KEY"]

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

 
INITIAL_RESPONSE = secrets.get("INITIAL_RESPONSE", "Hello! I’m here to help with tax finalization.")
CHAT_CONTEXT = secrets.get("CHAT_CONTEXT", 
    "You are a tax assistant helping users navigate tax finalization. Offer guidance on tax forms, deductions, credits, and filing deadlines.")

 
client = Groq(api_key=GROQ_API_KEY)

 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": INITIAL_RESPONSE},
    ]

 
st.title("Welcome to Your Tax Assistant! 💰")
st.caption("Here to guide you through tax finalization with ease.")


for message in st.session_state.chat_history:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "🗨️" if role == "user" else "💼"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

 
user_prompt = st.chat_input("Ask me any tax-related question...")

 
st.sidebar.title("Additional Tools")
 
st.sidebar.subheader("Tax Estimation")
income = st.sidebar.number_input("Enter your annual income:", min_value=0, step=1000)
if income:
     
    tax_estimate = 0
    if income <= 9875:
        tax_estimate = income * 0.1
    elif income <= 40125:
        tax_estimate = 987.5 + (income - 9875) * 0.12
    elif income <= 85525:
        tax_estimate = 4617.5 + (income - 40125) * 0.22
    else:
        tax_estimate = 14605.5 + (income - 85525) * 0.24
    st.sidebar.write(f"Estimated tax owed: ${tax_estimate:,.2f}")

 
st.sidebar.subheader("Deductions Checklist")
deductions = ["Medical Expenses", "Mortgage Interest", "Student Loan Interest", "Charitable Donations"]
selected_deductions = st.sidebar.multiselect("Select applicable deductions:", deductions)
if selected_deductions:
    st.sidebar.write("You selected the following deductions:")
    for deduction in selected_deductions:
        st.sidebar.write(f"- {deduction}")

 
st.sidebar.subheader("Tax Resources")
st.sidebar.write("[IRS Tax Forms](https://www.irs.gov/forms-instructions)")
st.sidebar.write("[Tax Deadlines](https://www.irs.gov/filing/individuals/when-to-file)")

 
if st.sidebar.button("Export Chat as PDF"):
    chat_content = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history])
    pdfkit.from_string(chat_content, "Tax_Assistant_Chat.pdf")
    st.sidebar.success("Chat exported as PDF!")

 
if user_prompt:
    
    with st.chat_message("user", avatar="🗨️"):
        st.markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

     
    messages = [
        {"role": "system", "content": CHAT_CONTEXT},
        {"role": "assistant", "content": INITIAL_RESPONSE},
        *st.session_state.chat_history,
    ]

   
    with st.chat_message("assistant", avatar="💼"):
        stream = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            stream=True
        )
       
        response_content = "".join(parse_groq_stream(stream))
        st.markdown(response_content)
        
    
    st.session_state.chat_history.append({"role": "assistant", "content": response_content})
