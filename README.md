# Análise de Sentimento

Implantação de modelos de análise de sentimento utilizando a Google Cloud Platform.

## Webapp

O objetivo desse projeto é comparar o uso de modelos criados com diversas etapas de pré-processamento de processamento de linguagem natural com o uso da [API Google Natural Language](https://cloud.google.com/natural-language?hl=pt-br).

A base de treinamento contém tweets sobre um determinado tema e iremos utilizar a API Streaming do Twitter para recuperar dados em tempo real e realizar a classificação de novos tweets in positivo, neutro e negativo.

Existem dois tutoriais de implantação:

* [Tutorial para execução Web App localmente no Windows 10 com Python](tutoriais/tutorial-execucao-webapp-windows-10-python.md)
* [Tutorial para execução Web App na GCP - Google Cloud Plataform](tutoriais/tutorial-execucao-webapp-gcp.md)


## Estrutura de diretórios

- `models/`: Contém o melhor modelo criado durante as aulas
- `keys/`: Necessário fazer o upload da chave de acesso a API Google Natural Language
- `webapp.py`: Contém a aplicação Streamlit


## Requisitos

- Ter realizado o tutorial de criação das chaves de desenvolvedor da API do Twitter
- Ter criado a conta no Google Cloud Platform
- Ter habilitado o serviço da API Google Natural Language


## Tecnologias utilizadas

1. [Python](https://www.python.org/): Linguagem de Programação
2. [Numpy](https://numpy.org/): Processamento de Dados
3. [Pandas](https://pandas.pydata.org/): Processamento de Dados
4. [Scikit-learn](https://scikit-learn.org/stable/): Machine Learning
5. [Streamlit](https://streamlit.io/): construção de Web Apps
6. [Git](https://git-scm.com/): versionamento de código
7. [Github](https://github.com/): repositório de código

