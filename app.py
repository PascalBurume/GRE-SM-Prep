import streamlit as st
import urllib.request
import json
import os
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AZURE_ENDPOINT_KEY = os.environ['AZURE_ENDPOINT_KEY'] = 'aZFiM9I1PBDXIChIgTed3cEcSWWGDmkz'

def allowSelfSignedHttps(allowed):
    # Bypass the server certificate verification on the client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

def StudyMaterials():
    allowSelfSignedHttps(True)
    
    # Streamlit UI components
    st.title('📖  Study Materials Assistant!🌐')
    
    
    col1, col2, col3 = st.columns(3)
    col2.image('images/stm.png', width=300, )
    # Display flashcards
    flashcards = [
        ["How is the Analytical Writing section scored and what are the criteria?", 
         "How is the GRE General Test structured and what is the timing for each section?",
         "What are some common pitfalls to avoid in the Quantitative Reasoning section?"]
    ]

    col1, col2, col3 = st.columns(3)

    for i, col in enumerate([col1, col2, col3]):
        for card in flashcards:
            if card[i]:
                col.markdown(f"""
                <div style="padding: 10px; margin: 10px; height: 150px; display: flex; align-items: center; justify-content: center; background-color: #f0f0f5; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);">
                    <p style="font-family: Arial, sans-serif; font-size: 14px; text-align: center;">{card[i]}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Initialize chat history
    if "study_materials_chat_history" not in st.session_state:
        st.session_state.study_materials_chat_history = []
    st.sidebar.title(" 🌐 Study Materials  ")
    st.sidebar.info("This is a chat interface to help you with your GRE preparation. You can ask questions and get answers from the assistant.")
   
    if st.sidebar.button("Clean Up Chat"):
        st.session_state.study_materials_chat_history = []
        
    # Display chat history
    for interaction in st.session_state.study_materials_chat_history:
        if interaction["inputs"]["chat_input"]:
            with st.chat_message("user"):
                st.write(interaction["inputs"]["chat_input"])
        if interaction["outputs"]["chat_output"]:
            with st.chat_message("assistant"):
                st.write(interaction["outputs"]["chat_output"])

    # React to user input
    if user_input := st.chat_input("Get ready for your GRE preparation..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(user_input)

        # Query API
        data = {"chat_history": st.session_state.study_materials_chat_history, 'chat_input': user_input}
        body = json.dumps(data).encode('utf-8')
        url = 'https://gre-sm-copilot.swedencentral.inference.ml.azure.com/score'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {AZURE_ENDPOINT_KEY}',
            'azureml-model-deployment': 'gre-sm-copilot'
        }
        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)
            response_data = json.loads(response.read().decode('utf-8'))

            # Check if 'chat_output' key exists in the response_data
            if 'chat_output' in response_data:
                with st.chat_message("assistant"):
                    st.markdown(response_data['chat_output'])

                st.session_state.study_materials_chat_history.append(
                    {"inputs": {"chat_input": user_input},
                     "outputs": {"chat_output": response_data['chat_output']}}
                )

            else:
                st.error("The response data does not contain a 'chat_output' key.")

        except urllib.error.HTTPError as error:
            st.error(f"The request failed with status code: {error.code}")
            

if __name__ == "__main__":
    StudyMaterials()
