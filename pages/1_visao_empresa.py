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
    
    
def order_by_date( df1 ):
    #FUNÇÃO PARA FIGURA
    
    cols = ["ID", "Order_Date"]

    df_aux = df1.loc[:, cols].groupby( "Order_Date" ).count().reset_index()

    fig = px.bar( df_aux, x="Order_Date", y="ID" )

    return fig
    
    
def traffic_order_share( df1 ):
    # Deliveries by traffic density          
        
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    fig = px.pie(df_aux, values="ID", names="Road_traffic_density")
    
    return fig
    
    
def road_density_by_city( df1 ):
    # DELIVERIES BY TRAFFIC DENSITY BY CITY
    
    colunas = ["ID", "City", "Road_traffic_density"]

    group = ["City", "Road_traffic_density"]

    df_aux = df1.loc[:, colunas].groupby(group).count().reset_index()

    df_aux = df_aux.loc[df_aux["City"] != "NaN", :]
    df_aux = df_aux.loc[df_aux["Road_traffic_density"] != "NaN", :]

    fig = px.scatter(df_aux, x="City", y="Road_traffic_density", size="ID", color="City")
    
    return fig


def orders_by_week( df1 ):
    #PEDIDOS POR SEMANA:
    
    df1["week_of_year"] = df1["Order_Date"].dt.strftime( '%U' )
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

    
def order_share_by_week( df1 ):    
    
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    df_aux = pd.merge( df_aux1, df_aux2, how='inner', on='week_of_year')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    
    return fig


def country_map( df1 ):
    
    colunas = ["City", "Road_traffic_density", "Delivery_location_latitude", "Delivery_location_longitude"]

    group = ["City", "Road_traffic_density"]

    df_aux = df1.loc[:, colunas].groupby(group).median().reset_index()

    df_aux = df_aux.loc[df_aux["City"] != "NaN", :]
    df_aux = df_aux.loc[df_aux["Road_traffic_density"] != "NaN", :]

    m = folium.Map(location=[18.573935, 76.316999], zoom_start=7, control_scale=True)

    for i in range(0, len(df_aux)):
        folium.Marker(location=[df_aux.iloc[i]["Delivery_location_latitude"], df_aux.iloc[i]["Delivery_location_longitude"]],
                      popup=df_aux.iloc[i][["City", "Road_traffic_density"]]).add_to(m)
        
    folium_static( m, width=1024, height=600 )       
        
    return None    


df = pd.read_csv(r"dataset/train.csv")

df1 = clean_code( df )


#================================================================================# 
#-------------------------------Visao empresa------------------------------------#
#================================================================================#

st.header("Marketplace - Visao Empresa")

#================================================================================#
#--------------------------------BARRA LATERAL-----------------------------------#
#================================================================================#

image = Image.open( "logo.png" )
st.sidebar.image( image, width=120 )

st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## Fastest delivery in town!")
st.sidebar.markdown("""---""")

st.sidebar.markdown("## Choose a deadline!")

date_slider = st.sidebar.slider( "Deadline", value=datetime(2022, 4, 13), min_value=datetime(2022, 2, 12), max_value=datetime(2022, 4, 13), format="DD-MM-YYYY" )
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect("Quais as condições de trânsito?", ['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High', 'Jam'])
st.header(date_slider)

st.sidebar.markdown("""---""")
st.sidebar.markdown("### Powered by Lucas Brino")

#FILTRO DE DATA:---------------------------------------------------------------

linhas_selecionadas = df1["Order_Date"] < date_slider
df1 = df1.loc[linhas_selecionadas, :]


#FILTRO DE TRANSITO:-----------------------------------------------------------

linhas_selecionadas = df1["Road_traffic_density"].isin( traffic_options ) 
df1 = df1.loc[linhas_selecionadas, :]


#===================================================
# LAYOUT NO STREAMLIT
#===================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('# Orders by day:')

        fig = order_by_date( df1 )
        
        st.plotly_chart(fig, use_container_width=True)
    
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('# Pedidos por tipo de trânsito')
            
            fig = traffic_order_share( df1 )
            
            st.plotly_chart( fig, use_container_width=True )
            
            
        with col2:
            st.markdown('# Pedidos por cidade e tipo de trânsito')
            
            fig  = road_density_by_city( df1 )
                        
            st.plotly_chart( fig, use_container_width=True )
    
    
with tab2:
    with st.container():
        st.markdown('# Orders by week')

        fig = orders_by_week( df1 )

        st.plotly_chart( fig, use_container_width=True )
        
        
    with st.container():
        
        fig = order_share_by_week( df1 )
        
        st.plotly_chart( fig, use_container_width=True )
        
        
with tab3:
    st.markdown('# Country Maps') 
    
    country_map( df1 )
        
     
