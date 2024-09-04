import streamlit as st
from langchain.chains import TransformChain
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain import globals
from langchain_core.runnables import chain
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
import tempfile
import os
import base64
from dotenv import load_dotenv
load_dotenv(override=True)

# Set verbose
globals.set_debug(True)

def save_uploaded_image(uploaded_file):
    """Salva l'immagine caricata in una directory temporanea e restituisce il percorso."""
    if uploaded_file is not None:
        # Creazione di un file temporaneo nella directory temporanea
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
            temp_file.write(uploaded_file.read())
            return temp_file.name
    else:
        return None

def load_image(inputs: dict) -> dict:
    """Load image from file and encode it as base64."""
    image_path = inputs["image_path"]
  
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    image_base64 = encode_image(image_path)
    return {"image": image_base64}

load_image_chain = TransformChain(
    input_variables=["image_path"],
    output_variables=["image"],
    transform=load_image
)

@chain
def image_model(inputs: dict) -> str | list[str] | dict:
 """Invoke model with image and prompt."""
 model = ChatOpenAI(temperature=0.1, model="gpt-4o", max_tokens=1024)
 msg = model.invoke(
             [HumanMessage(
             content=[
             {"type": "text", "text": inputs["prompt"]},
             {"type": "text", "text": parser.get_format_instructions()},
             {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{inputs['image']}"}},
             ])]
             )
 return msg.content

def get_image_informations(image_path: str) -> dict:
   vision_prompt = """
      Data l'immagine, fornisci le seguenti informazioni:
      - Descrizione dettagliata della foto e del relativo problema ecologico. Fornire informazioni solo sul problema ecologico, non sull'ambiente circostante e non aggiungere altri commenti. Se la foto non riguarda un problema ecologico resituisci il messaggio "La foto non riguarda un problema ecologico". 
      - Gravità (da 0 a 10) del problema ecologico, ad esempio gravità 9 o 10 in caso di grande discarica a cielo aperto . Se la foto non riguarda un problema ecologico resituisci 0. 
      """
   vision_chain = load_image_chain | image_model | parser
   return vision_chain.invoke({'image_path': f'{image_path}', 
                               'prompt': vision_prompt})

class Report(BaseModel):
    """Informazioni su un'immagine."""
    descrizione: str = Field(description="Descrizione dettagliata del rapporto sul problema ecologico. Fornire informazioni solo sul problema ecologico, non sull'ambiente circostante e non aggiungere altri commenti")
    gravità: int = Field(description="Gravità (da 0 a 10) del problema ecologico, ad esempio gravità 9 o 10 in caso di grande discarica a cielo aperto")

parser = PydanticOutputParser(pydantic_object=Report)


def get_lat_long(address):
    #TODO
    pass

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
    image_path = save_uploaded_image(uploaded_file)

    if st.button("Send"):
        result = get_image_informations(image_path)
    
    #Save on DB 
        print(result.descrizione)
        print(result.gravità)
    # #TODO

if __name__ == "__main__":
    main()
