from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image
import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

#=================================================================#
#---------------------------FUNÇÕES-------------------------------#
#=================================================================#

def clean_code( df1 ):
    #Esta função limpa o Dataframe 
    
    #Tirando os NANs -----------------------------------------------------------------------

    sem_nan_age = ( df1["Delivery_person_Age"] != 'NaN ')

    df1 = df1.loc[sem_nan_age, :].copy()


    sem_nan_city = ( df1["City"] != 'NaN ')

    df1 = df1.loc[sem_nan_city, :].copy()


    sem_nan_festival = ( df1["Festival"] != 'NaN ')

    df1 = df1.loc[sem_nan_festival, :].copy()


    linhas_mult = df1.loc[:, 'multiple_deliveries'] != 'NaN '

    df1 = df1.loc[linhas_mult, :].copy()


    #Transformando as linhas em inteiros e decimais:----------------------------------------

    df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype( int )

    df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype( float )

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    #Transformando a coluna de Data de texto para data:-------------------------------------

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')


    #Removendo os espaços extras dos nomes de coluna:---------------------------------------

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    #Limpando a coluna de time taken:-------------------------------------------------------

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1

def average_rating(df1):
    colunas = ['Delivery_person_ID', "Delivery_person_Ratings"]

    group = 'Delivery_person_ID'

    avgrtg = df1.loc[:, colunas].groupby( group ).mean().sort_values('Delivery_person_Ratings', ascending=False).reset_index()
    
    return avgrtg


def avg_traffic(df1):
    colunas = ["Delivery_person_Ratings", "Road_traffic_density"]

    group = "Road_traffic_density"

    avgtrafic = df1.loc[df1["Road_traffic_density"] != "NaN", colunas].groupby(group).mean().sort_values('Delivery_person_Ratings', ascending=False)
    
    return avgtrafic


def average_weather(df1):
    colunas = ["Delivery_person_Ratings", "Weatherconditions"]

    avgweather = df1.loc[df1["Weatherconditions"] != "NaN", colunas].groupby("Weatherconditions").mean().sort_values('Delivery_person_Ratings', ascending=False)

    return avgweather


def ten_best(df1):
    colunas = ["Delivery_person_ID", "Time_taken(min)", "City"]

    group = ["City", "Delivery_person_ID"]

    quickest = df1.loc[:, colunas].groupby(group).mean().sort_values(["City", "Time_taken(min)"]).reset_index()

    df_aux1 = quickest.loc[quickest["City"] == "Metropolitian", :].head(10)
    df_aux2 = quickest.loc[quickest["City"] == "Urban", :].head(10)
    df_aux3 = quickest.loc[quickest["City"] == "Semi-Urban", :].head(10)

    df3 = pd.concat( [df_aux1, df_aux2, df_aux3] ).reset_index(drop=True)

    return df3


def ten_worst(df1):
    colunas = ["Delivery_person_ID", "Time_taken(min)", "City"]

    group = ["City", "Delivery_person_ID"]

    quickest = df1.loc[:, colunas].groupby(group).mean().sort_values(["City", "Time_taken(min)"], ascending=False).reset_index()

    df_aux1 = quickest.loc[quickest["City"] == "Metropolitian", :].head(10)
    df_aux2 = quickest.loc[quickest["City"] == "Urban", :].head(10)
    df_aux3 = quickest.loc[quickest["City"] == "Semi-Urban", :].head(10)

    df3 = pd.concat( [df_aux1, df_aux2, df_aux3] ).reset_index(drop=True)
    
    return df3
    
    
    
df = pd.read_csv(r"dataset/train.csv")

df1 = clean_code( df )


#Visao entregadores:-------------------------------------------------------------------------

st.header("Marketplace - Visao Entregadores")

#==============================================================================
# BARRA LATERAL
#==============================================================================

image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## Fastest delivery in town!")
st.sidebar.markdown("""---""")

st.sidebar.markdown("## Choose a deadline!")

date_slider = st.sidebar.slider( "Deadline", value=datetime(2022, 4, 13), min_value=datetime(2022, 2, 12), max_value=datetime(2022, 4, 13), format="DD-MM-YYYY" )
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect("Quais as condições de trânsito?", ['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""---""")


weather_options = st.sidebar.multiselect("Quais as condições de trânsito?", ['conditions Sunny', 'conditions Fog', 'conditions Cloudy', 'conditions Windy', 'conditions Stormy', 'conditions Sandstorms'], default=['conditions Sunny', 'conditions Fog', 'conditions Cloudy', 'conditions Windy', 'conditions Stormy', 'conditions Sandstorms'])
st.header(date_slider)

st.sidebar.markdown("""---""")
st.sidebar.markdown("### Powered by Lucas Brino")

#FILTRO DE DATA:---------------------------------------------------------------

linhas_selecionadas = df1["Order_Date"] < date_slider
df1 = df1.loc[linhas_selecionadas, :]


#FILTRO DE TRANSITO:-----------------------------------------------------------

linhas_selecionadas = df1["Road_traffic_density"].isin( traffic_options ) 
df1 = df1.loc[linhas_selecionadas, :]

#FILTRO DE CONDIÇÕES CLIMÁTICAS:-----------------------------------------------

linhas_selecionadas = df1["Weatherconditions"].isin( weather_options ) 
df1 = df1.loc[linhas_selecionadas, :]

#===================================================
# LAYOUT NO STREAMLIT
#===================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overall metrics")
        col1, col2, col3, col4 = st.columns( 4, gap="medium" )
        
        with col1:
            coluna = "Delivery_person_Age"

            velho = df1.loc[:, coluna].max()
            
            col1.metric( "Maior idade:", velho )
            
        with col2:            
            coluna = "Delivery_person_Age"

            novo = df1.loc[:, coluna].min()
            
            col2.metric("Menor idade:", novo)
        
        with col3:
            coluna = "Vehicle_condition"

            melhor = df1.loc[df1["Vehicle_condition"] != "NaN", coluna].max()
            
            col3.metric("Melhor condição de veículo:", melhor)
            
        with col4:
            coluna = "Vehicle_condition"

            pior = df1.loc[df1["Vehicle_condition"] != "NaN", coluna].min()
            
            col4.metric("Pior condição de veículo:", pior)
            
    with st.container():
        st.markdown("""---""")
        st.title("Avaliações")
        col1, col2 = st.columns( 2, gap='large' )
        
        with col1:
            st.subheader( "Avaliação média por entregador" )
            
            avgrtg = average_rating(df1)

            col1.dataframe(avgrtg, height=510, use_container_width=True)
            
        with col2:            
            st.subheader( "Avaliação média por trânsito" )
            
            avgtrafic = avg_traffic(df1)
            
            col2.dataframe(avgtrafic, width=315, use_container_width=True)
            
            st.subheader( "Avaliação média por clima" )
            
            avgweather = average_weather(df1)

            col2.dataframe(avgweather, use_container_width=True)
            
    with st.container():
        st.title( "Top 10 entregadores" )
        
        col1, col2 = st.columns( 2, gap='large' )
        with col1:
            st.markdown("### 10 Entregadores mais rápidos")
            
            df3 = ten_best(df1)

            col1.dataframe(df3, use_container_width=True)
            
        with col2:
            st.markdown("### 10 Entregadores mais lentos")
            
            df3 = ten_worst(df1)

            col2.dataframe(df3, use_container_width=True)
