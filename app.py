import openai
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import os 
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import openai
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredPDFLoader

load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY', 'sk-9azBt6Dd8j7p5z5Lwq2S9EhmkVX48GtN2Kt2t3GJGN94SQ2')

persist_directory = 'ai_paper1'
embeddings = OpenAIEmbeddings()

if not os.path.exists(persist_directory):
    print('embedding the document now')
    loader = UnstructuredPDFLoader('ai_paper.pdf', mode="elements")
    pages = loader.load_and_split()

    vectordb = Chroma.from_documents(documents=pages, embedding=embeddings, persist_directory=persist_directory)
    vectordb.persist()

vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

def generate_response(prompt):
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": prompt}
    ])
    response = completion.choices[0].message.content
    return response

st.title("🤖 pwang_szn bot")

if 'generated' not in st.session_state:
    st.session_state['generated'] = ['i am ready to help you ser']

if 'past' not in st.session_state:
    st.session_state['past'] = ['hey there!']

def get_text():
    input_text = st.text_input("", key="input")
    return input_text 

def search_chroma(query):
    result_docs = vectordb.similarity_search(query)

    chain = load_qa_chain(ChatOpenAI(temperature=0), chain_type="stuff")
    output = chain({"input_documents": result_docs, "question": query})

    return output['output_text']

user_input = get_text()
if user_input:
    output = search_chroma(user_input)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
