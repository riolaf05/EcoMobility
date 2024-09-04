import streamlit as st
import json
from dotenv import load_dotenv
load_dotenv(override=True)
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from typing import List
from langchain.prompts import ChatPromptTemplate


from pydantic import BaseModel, Field
from typing import List

class Symptom(BaseModel):
    """Patient symptom described during a doctor's call."""

    names: List[str] = Field(description="List of symptoms described by the patient")
    description: str = Field(description="Detailed description of the symptoms and any associated information")
    duration: str = Field(description="Duration for which the symptom has been present (e.g., '2 days', '1 week')")
    severity: str = Field(description="Severity of the symptom (e.g., 'mild', 'moderate', 'severe')")
    notes: str = Field(description="Any additional notes or relevant information provided by the patient or observed by the doctor")

model = ChatOpenAI(temperature=0).bind_tools([Symptom])
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

# Function that processes the input and returns the JSON structure
def process_symptoms(input_text):
    try:
        response = chain.invoke({"input": input_text})
        return response
    except Exception as e:
        st.error(f"An error occurred while processing the input: {e}")
        return None

# Streamlit app
def main():
    st.title("Patient Symptom Extractor")

    # Input field for the patient message
    input_text = st.text_area("Enter the patient's description of symptoms:")

    if st.button("Process Symptoms"):
        if input_text.strip():
            # Process the input through the function
            symptoms_json = process_symptoms(input_text)

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
