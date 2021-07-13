from google.cloud import language
import streamlit as st
import numpy as np
import pandas as pd
import time
import pickle
import nltk
import re
import string
import os
import tweepy

nltk.download('stopwords')
nltk.download('rslp')

# Initial setup
st.set_page_config(layout="wide", page_icon=u"\U0001F916", page_title='Analisador de Sentimento')

# Esse pedação de código irá esconder o menu do Streamlit
# hide_streamlit_style = """
# <style>
# 	#MainMenu {visibility: hidden;}
# 	footer {visibility: hidden;}
# </style>
# """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True) 



def stemmed_palavra(palavra):
	stemmer = nltk.stem.RSLPStemmer()
	return stemmer.stem(palavra)


def tratar_texto(texto):
    string_sem_url = re.sub(r"http\S+", "", texto)
    string_sem_user = re.sub(r"@\S+", "", string_sem_url)
    string_sem_rt = re.sub(r"rt+", "", string_sem_user)
    palavras_separadas_pontuacao = re.sub("(\\W)"," \\1 ", string_sem_rt)
    palavras = []
    for plvr in re.split("\\s+", palavras_separadas_pontuacao):
        if plvr not in string.punctuation and plvr not in nltk.corpus.stopwords.words('portuguese'):
            plvr_stemm = stemmed_palavra(plvr)
            palavras.append(plvr_stemm)
    
    return palavras


def set_google_api_key():
    key = 'GOOGLE_APPLICATION_CREDENTIALS'
    if not os.getenv(key) or not os.path.isfile(os.environ['GOOGLE_APPLICATION_CREDENTIALS']):
        st.error('Chave Google API não encontrada, faça o UPLOAD da chave utilizando o botão abaixo.')
        file_upload = st.file_uploader('Faça o UPLOAD da chave recuperada do Console do Google', type=['json'])
        if file_upload is not None:
            with open(f'keys/{file_upload.name}', 'wb') as fo:
                fo.write(file_upload.getbuffer())
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f'keys/{file_upload.name}'
            st.info(f"Chave Google API salva em: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")
    else:
        st.info(f"Chave Google API encontrada: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")


def predict_google(texto, thr=0.1):
    ...


def predict_local(texto):
    ...


def predict_text(texto, thr=0.1, predict_type='local'):
    ...


def compare_predict_text(texto, thr=0.1, predict_type='local'):
    ...



class DadosPublicosTwitter(tweepy.StreamListener):
    def on_status(self, tweet):
        ...

    
    def on_error(self, error):
        ...


########################################
# Função principal para criar o Webapp #
########################################
def main():
    st.title('Analisador de Sentimento')
    ...






if __name__ == '__main__':
    pickle_in = open(f'models/best_model.pickle', 'rb')
    classifier = pickle.load(pickle_in)

    main()


