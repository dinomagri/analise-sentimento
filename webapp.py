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

    if sentimento.score > thr:
    	classe = 'positivo'
    elif sentimento.score < -thr:
    	classe = 'negativo'
    else:
    	classe = 'neutro'

    return classe, round(sentimento.score, 4), round(sentimento.magnitude, 4)


def predict_local(texto):
    classe = classifier.predict([texto])
    proba = classifier.predict_proba([texto])
    score = max(proba[0])
    return classe[0], round(score, 4)


def predict_text(texto, thr=0.1, predict_type='local'):
    if not texto:
        return st.error('É necessário digitar um texto')

    if predict_type == 'local':
        classe, score = predict_local(texto)
    elif predict_type == 'google_nl_api':
        classe, score, magnitude = predict_google(texto, thr=thr)
    else:
        raise Exception(f'\n\n\n [ERROR] endpoint {predict_type} não suportado! \n Faça as devidas correções')


    resultado = 'O sentimento identificado foi {}'
    resultado += f' - classe: {classe} - score: {score}'
    
    if predict_type == 'google_nl_api':
        resultado += f' - magnitude: {magnitude}'

    if classe == 'negativo':
        emoji = u'\U0001f641'
        st.error(resultado.format(emoji))
    elif classe == 'positivo':
        emoji = u'\U0001f642'
        st.success(resultado.format(emoji))
    elif classe == 'neutro':
        emoji = u'\U0001f610'
        st.warning(resultado.format(emoji))



def compare_predict_text(texto, thr=0.1, predict_type='local'):
    if predict_type == 'local':
        classe, score = predict_local(texto)
    elif predict_type == 'google_nl_api':
        classe, score, magnitude = predict_google(texto, thr=thr)
    else:
        raise Exception(f'\n\n\n [ERROR] endpoint {predict_type} não suportado! \n Faça as devidas correções')

    resultado = 'O sentimento identificado foi {}'
    resultado += f' - classe: {classe} - score: {score}'
    
    if predict_type == 'google_nl_api':
        resultado += f' - magnitude: {magnitude}'

    if classe == 'negativo':
        emoji = u'\U0001f641'
        st.error(resultado.format(emoji))
    elif classe == 'positivo':
        emoji = u'\U0001f642'
        st.success(resultado.format(emoji))
    elif classe == 'neutro':
        emoji = u'\U0001f610'
        st.warning(resultado.format(emoji))



class DadosPublicosTwitter(tweepy.StreamListener):
    def on_status(self, tweet):
        if not parar_stream:
            if not hasattr(tweet, "retweeted_status"):
                try:
                    texto = tweet.extended_tweet["full_text"]
                    st.subheader(texto)
                    compare_predict_text(texto)
                    compare_predict_text(texto, predict_type='google_nl_api')
                except AttributeError:
                    texto = tweet.text
                    st.subheader(texto)
                    compare_predict_text(texto)
                    compare_predict_text(texto, predict_type='google_nl_api')
            return True
        else:
            exit()
            return False

    
    def on_error(self, error):
        st.write('[ERROR]', error)
        return False


########################################
# Função principal para criar o Webapp #
########################################
def main():
    st.title('Analisador de Sentimento')
    add_selectbox = st.sidebar.selectbox('Escolha a origem dos dados', ('Local', 'Twitter'))
    
    if add_selectbox == 'Local':
        add_subselectbox = st.sidebar.selectbox('Escolha o endpoint para fazer a predição', ('Nosso melhor modelo', 'Google NL API', 'Comparar'))
        if add_subselectbox == 'Google NL API':
            set_google_api_key()

            st.header('Utilizando a API do Google Natural Language')
            texto = st.text_input('Digite o texto para ser analisado')
            if st.button('Realizar predição'):
                predict_text(texto, predict_type='google_nl_api')

        elif add_subselectbox == 'Nosso melhor modelo':
            st.header('Utilizando o nosso melhor modelo')
            texto = st.text_input('Digite o texto para ser analisado')
            if st.button('Realizar predição'):
                predict_text(texto, predict_type='local')

        elif add_subselectbox == 'Comparar':
            set_google_api_key()
            
            st.header('Comparando os modelos')
            texto = st.text_input('Digite o texto para ser analisado')
            if st.button('Realizar comparação'):
                st.subheader('Utilizando nosso modelo')
                compare_predict_text(texto)
                st.subheader('Utilizando Google Natural Language API')
                compare_predict_text(texto, predict_type='google_nl_api')
    
    elif add_selectbox == 'Twitter':
        st.header('Twitter - Fluxo constante de dados')
        st.write("Digite as informações necessárias no setup inicial para iniciar a captura dos tweets para serem classificados pelo nosso melhor modelo e também pela API do Google Natural Language. Clique em **Realizar Classificações**")
        st.subheader('Setup inicial')
        set_google_api_key()

        consumer_key = st.text_input('CONSUMER_KEY', 'adicione_aqui')
        consumer_secret = st.text_input('CONSUMER_SECRET' ,'adicione_aqui')
        access_token = st.text_input('ACCESS_TOKEN' ,'adicione_aqui')
        access_token_secret = st.text_input('ACCESS_TOKEN_SECRET' ,'adicione_aqui')
        track_topics = st.text_input('Digite o tópico para recuperar os tweets', 'Copa do Mundo')
        
        if st.button('Realizar Classificações'):
            if any(var == '' for var in (consumer_key, consumer_secret, access_token, access_token_secret, track_topics)):
                st.error('Todos os campos são necessários')
            else:
                
                global parar_stream
                parar_stream = st.button('Reset')

                autorizar = tweepy.OAuthHandler(consumer_key, consumer_secret)
                autorizar.set_access_token(access_token, access_token_secret)

                dados_twitter = DadosPublicosTwitter()
                fluxo = tweepy.Stream(autorizar, dados_twitter, tweet_mode='extended')
                fluxo.filter(track=[track_topics], languages=['pt'])




if __name__ == '__main__':
    pickle_in = open(f'models/best_model.pickle', 'rb')
    classifier = pickle.load(pickle_in)

    main()


