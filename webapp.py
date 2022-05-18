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
# 	#MainMenu {visibility: hidden;}
# 	footer {visibility: hidden;}
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

    plot_emoji(resultado, classe)


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

    plot_emoji(resultado, classe)


def delete_previous_rules_from_streaming(stream_client):
    rule_ids = []
    result = stream_client.get_rules()
    if result.data:
        for rule in result.data:
            print(f"rule marked to delete: {rule.id} - {rule.value}")
            rule_ids.append(rule.id)
     
    if(len(rule_ids) > 0):
        stream_client.delete_rules(rule_ids)
    else:
        print("no rules to delete")


def add_rules(track_topics, language='pt'):
    return f'{track_topics} lang:{language}'


class DadosPublicosTwitter(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        if not parar_stream:
            if hasattr(tweet, "text"):
                texto = tweet.text
                st.subheader(texto)
                #texto = preprocessing(texto)
                compare_predict_text(texto)
                compare_predict_text(texto, predict_type='google_nl_api')
            return True
        else:
            print('-----> A captura foi finalizada!')
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

        bearer_token = st.text_input('bearer_token', '')
        track_topics = st.text_input('Digite o tópico para recuperar os tweets', '')
        
        if st.button('Realizar Classificações'):
            if any(var == '' for var in (bearer_token, track_topics)):
                st.error('Todos os campos são necessários')
            else:
                
                global parar_stream
                parar_stream = st.button('Reset')

                dados_twitter = DadosPublicosTwitter(bearer_token, wait_on_rate_limit=True, max_retries=3)
                delete_previous_rules_from_streaming(dados_twitter)

                # Add new rule # https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule#list
                rule = tweepy.StreamRule(value=add_rules(track_topics))
                dados_twitter.add_rules(rule)

                dados_twitter.filter(expansions="author_id", tweet_fields="created_at")



if __name__ == '__main__':
    pickle_in = open(f'models/best_model0.pickle', 'rb')
    classifier = pickle.load(pickle_in)

    main()


