import streamlit as st
import boto3
import os
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from geopy.geocoders import Nominatim
import json
from dotenv import load_dotenv
load_dotenv(override=True)
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from typing import List
from langchain.prompts import ChatPromptTemplate


from pydantic import BaseModel, Field
from typing import List

class Report(BaseModel):
    """Patient symptom described during a doctor's call."""

    description: str = Field(description="Detailed description of the ecological problem report")
    severity: str = Field(description="Severity (from 0 to 10) of the ecological problem, e.g. severity 9 or 10 in case of big open-air dump")
   

model = ChatOpenAI(temperature=0).bind_tools([Report])
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """
            You are an assistant that helps a busy doctor who needs to quickly review and document symptoms described by patients during calls.
            Your task is to carefully listen to the patient's description and extract all relevant symptoms.
            For each symptom mentioned, provide the name of the symptom, a brief description, the duration for which the symptom has been present, its severity, and any additional notes or observations.
            The final output should be a comprehensive and well-structured list of symptoms with all necessary details.
            If the conversation is not inherent with the patient problem just return an empty list. 
        """),
        ("user", "{input}")
    ]
)
parser = JsonOutputToolsParser()
chain = prompt | model | parser

def get_lat_long(address):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Function that processes the input and returns the JSON structure
def process_report(input_text):
    try:
        response = chain.invoke({"input": input_text})
        return response
    except Exception as e:
        st.error(f"An error occurred while processing the input: {e}")
        return None

# Streamlit app
def main():
    st.title("Segnalazione Danni Ecologici in Città")

    # Campo per l'indirizzo
    address = st.text_input("Inserisci l'indirizzo del danno ecologico:")

    # Campo per il caricamento della foto
    uploaded_file = st.file_uploader("Carica una foto del danno", type=["jpg", "jpeg", "png"])

    if st.button("Process Symptoms"):
        if input_text.strip():
            # Process the input through the function
            symptoms_json = process_report(input_text)

            # Check if the response is valid
            if symptoms_json is not None:
                if len(symptoms_json) == 0:
                    st.error("Nessun sintomo individuato.")
                else:
                    try:
                        # Display the extracted symptoms
                        st.subheader("Extracted Symptoms")
                        for symptom in symptoms_json:
                            st.write(f"**Symptom Names:** {', '.join(symptom['args']['names'])}")
                            st.write(f"**Description:** {symptom['args']['description']}")
                            st.write(f"**Duration:** {symptom['args']['duration']}")
                            st.write(f"**Severity:** {symptom['args']['severity']}")
                            st.write(f"**Notes:** {symptom['args']['notes']}")
                            st.write("---")
                    except KeyError as e:
                        st.error(f"Invalid JSON structure: missing key {e}")
            else:
                st.error("Failed to process the input.")
        else:
            st.warning("Please enter a description of symptoms before processing.")

if __name__ == "__main__":
    main()
