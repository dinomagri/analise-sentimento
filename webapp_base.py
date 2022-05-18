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
import spacy


spacy.cli.download('pt_core_news_sm')

nltk.download('stopwords')
nltk.download('rslp')


# Initial setup
st.set_page_config(layout="wide", page_icon=u"\U0001F916", page_title='Analisador de Sentimento')

# Esse pedação de código irá esconder o menu do Streamlit
# hide_streamlit_style = """
# <style>
#   #MainMenu {visibility: hidden;}
#   footer {visibility: hidden;}
# </style>
# """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True) 



nlp = spacy.load('pt_core_news_sm')

import re
import nltk

stopwords_nltk = nltk.corpus.stopwords.words("portuguese")
stopwords = spacy.lang.pt.stop_words.STOP_WORDS

def preprocessing(texto):

    for sn in stopwords_nltk:
        stopwords.add(sn)

    # Deixa o texto em minúsculo
    texto = texto.lower()

    # retira nome do usuário: @labdata
    texto = re.sub(r"@[A-Za-z0-9$-_@.&+]+", '', texto)

    texto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # retira espaços em branco extras no meio do texto, no começo e no fim
    texto = re.sub(r" +", ' ', texto).strip()

    # substituir emoticons por texto
    emoticons = {
        ':)': 'emocaopositiva',
        ':d': 'emocaopositiva',
        '=)': 'emocaopositiva',
        '=(': 'emocaonegativa',
        ':(': 'emocaonegativa',
        ':|': 'emocaoneutra'
    }

    for emoticon in emoticons:
        texto = texto.replace(emoticon, emoticons[emoticon])

    doc = nlp(texto.lower())

    lista_de_tokens_tratados = []
    for token in doc:
        if (token.text not in stopwords) and (not token.is_punct) and (not token.like_email) and (not token.like_url):
            lista_de_tokens_tratados.append(token.lemma_)

    return lista_de_tokens_tratados


def tratar_texto(texto):
    return preprocessing(texto)


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
    cliente_api = language.LanguageServiceClient()
    documento = language.Document(
        content=texto,
        type_=language.Document.Type.PLAIN_TEXT,
        language='pt-BR'
    )
    sentimento = cliente_api.analyze_sentiment(
        document=documento, 
        encoding_type='UTF32'
    ).document_sentiment

    ...


def predict_local(texto):
    ...

def  plot_emoji(resultado, classe):
    if classe == 'negativo':
        emoji = u'\U0001f641'
        st.error(resultado.format(emoji))
    elif classe == 'positivo':
        emoji = u'\U0001f642'
        st.success(resultado.format(emoji))
    elif classe == 'neutro':
        emoji = u'\U0001f610'
        st.warning(resultado.format(emoji))


def predict_text(texto, thr=0.1, predict_type='local'):
    ...


def compare_predict_text(texto, thr=0.1, predict_type='local'):
    ...


def delete_previous_rules_from_streaming(stream_client):
    ...


def add_rules(track_topics, language='pt'):
    ...


class DadosPublicosTwitter(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        ...

    
    def on_error(self, error):
        st.write('[ERROR]', error)
        return False


########################################
# Função principal para criar o Webapp #
########################################
def main():
    st.title('Analisador de Sentimento')
    ...


if __name__ == '__main__':
    pickle_in = open(f'models/best_model0.pickle', 'rb')
    classifier = pickle.load(pickle_in)

    main()


