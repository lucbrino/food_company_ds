from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image
import folium
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
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
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    #Limpando a coluna de time taken:-------------------------------------------------------

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    
    return df1


df = pd.read_csv(r"dataset/train.csv")

df1 = clean_code(df)


def distance_mean(df1):
    colunas = ["Restaurant_latitude", "Restaurant_longitude", "Delivery_location_latitude", "Delivery_location_longitude"]

    df1['distance'] = df1.loc[df1['City'] != 'NaN', colunas].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

    local_medio = np.round(df1['distance'].mean(), 2)

    return local_medio
            

def mean_time_festival(df1, festival, op):
    
    '''
        Esta função calcula o tempo medio e desvio padrão do tempo de entrega com festival.
        Parametros de entrada:
            Input:
                -df: Dataframe com os dados necessarios para o calculo
                -op: Tipo de operação a ser aplicada
                    -'avgtime': Calcula o tempo medio
                    -'stdtime': Calcula o desvio padrao
            Output:
                Dataframe com duas colunas e uma linha
    '''
    
    df_aux = ( df1.loc[:, ["Time_taken(min)", "Festival"]]
                          .groupby('Festival')
                          .agg( {"Time_taken(min)": ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2 )
    
    return df_aux


def std_time_festival(df1, festival, op):
    
    df_aux = ( df1.loc[:, ["Time_taken(min)", "Festival"]]
                          .groupby('Festival')
                          .agg( {"Time_taken(min)": ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2 )
    
    return df_aux


def no_festival_mean(df1, festival, op):
    df_aux = ( df1.loc[:, ["Time_taken(min)", "Festival"]]
                  .groupby('Festival')
                  .agg( {"Time_taken(min)": ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    medio_n_festival = np.round( df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2 )
    
    return medio_n_festival


def no_festival_deviation(df1, festival, op):
    df_aux = ( df1.loc[:, ["Time_taken(min)", "Festival"]]
                          .groupby('Festival')
                          .agg( {"Time_taken(min)": ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    std_no_festival = np.round( df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2 )

    return std_no_festival
            
    
def mean_time_per_city(df1):
    colunas = ["City", "Time_taken(min)"]

    df_aux = df1.loc[df1['City'] != 'NaN', colunas].groupby('City').agg( {'Time_taken(min)': ['mean', 'std'] } )

    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = go.Figure()

    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'],error_y=dict( type='data', array=df_aux['std_time'] ) ) ) 

    fig.update_layout( barmode='group' )
    
    return fig
    

def mean_distance_per_city(df1):
    colunas = ["Restaurant_latitude", "Restaurant_longitude", "Delivery_location_latitude", "Delivery_location_longitude"]

    df1['distance'] = df1.loc[df1['City'] != 'NaN', colunas].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

    local_medio = df1.loc[df1['City'] != 'NaN', ['City', 'distance']].groupby('City').mean().reset_index()

    fig = go.Figure( data=[ go.Pie (labels=local_medio['City'], values=df1['distance'], pull=[0, 0.1, 0] ) ] )

    fig.update_traces(texttemplate="%{value:.1f}")
    
    return fig
    
    
def mean_time_per_traffic_type(df1):
    colunas = ["City", "Road_traffic_density", "Time_taken(min)"]

    linhas = (df1["City"] != "NaN") & (df1["Road_traffic_density"] != "NaN")

    df_aux = df1.loc[linhas, colunas].groupby(["City", "Road_traffic_density"]).agg( {'Time_taken(min)': ['mean', 'std'] } )

    df_aux.columns = ['avgtime', 'stdtime']

    df_aux = df_aux.reset_index()

    fig = px.sunburst( df_aux, path=["City", "Road_traffic_density"], values='avgtime',
                       color='stdtime', color_continuous_scale='RdBu',
                       color_continuous_midpoint=np.average(df_aux['stdtime']) )

    return fig
    

def mean_time_city_order_type(df1):
    colunas = ["City", "Type_of_order", "Time_taken(min)"]

    linha = df1["City"] != "NaN"

    df_aux = ( df1.loc[:, ["Time_taken(min)", "City", "Type_of_order"]]
                      .groupby(['City', 'Type_of_order'])
                      .agg( {"Time_taken(min)": ['mean', 'std']} ) )

    df_aux.columns = ['avgtime', 'stdtime']
    df_aux = df_aux.reset_index()

    std_festival = df_aux.loc[:, ['City', 'Type_of_order', 'avgtime', 'stdtime']]
    
    return std_festival
    


#Visao entregadores:-------------------------------------------------------------------------

st.header("Marketplace - Visao dos Restaurantes")


#==============================================================================
# BARRA LATERAL
#==============================================================================

image = Image.open( "logo.png" )
st.sidebar.image( image, width=120 )

st.sidebar.markdown("# Curry Company")
st.sidebar.markdown("## Fastest delivery in town!")
st.sidebar.markdown("""---""")

st.sidebar.markdown("## Choose a deadline!")

date_slider = st.sidebar.slider( "Deadline", value=datetime(2022, 4, 13), min_value=datetime(2022, 2, 12), max_value=datetime(2022, 4, 13), format="DD-MM-YYYY" )
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect("Quais as condições de trânsito?", ['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""---""")


weather_options = st.sidebar.multiselect("Quais as condições de clima?", ['conditions Sunny', 'conditions Fog', 'conditions Cloudy', 'conditions Windy', 'conditions Stormy', 'conditions Sandstorms'], default=['conditions Sunny', 'conditions Fog', 'conditions Cloudy', 'conditions Windy', 'conditions Stormy', 'conditions Sandstorms'])


st.sidebar.markdown("""---""")
city_options = st.sidebar.multiselect("Qual tipo de cidade?", ['Urban', 'Semi-Urban', 'Metropolitian'], default=['Urban', 'Semi-Urban', 'Metropolitian'])

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

#FILTRO DE TIPO DE CIDADE:------------------------------------------------

linhas_selecionadas = df1["City"].isin( city_options ) 
df1 = df1.loc[linhas_selecionadas, :]

#===================================================
# LAYOUT NO STREAMLIT
#===================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overall metrics")
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1:
                       
            unicos = df1.loc[:, "Delivery_person_ID"].unique()

            col1.metric('Entregadores únicos:', len(unicos))
            
            
        with col2:
                        
            local_medio = distance_mean(df1)

            col2.metric('Distância média restaurantes/entrega em Km:', local_medio)
            
            
        with col3:
            medio_festival = mean_time_festival(df1, 'Yes', 'avg_time')
            
            col3.metric('Tempo médio com festival:', medio_festival)
            
        with col4:
            std_festival = std_time_festival(df1, 'Yes', 'std_time')
            
            col4.metric('Desvio padrão com festival', std_festival)
        
        
        with col5:
            medio_n_festival = no_festival_mean(df1, 'No', 'avg_time')
            
            col5.metric('Tempo médio de entrega sem festival', medio_n_festival)
            
        
        with col6:         
            std_festival = no_festival_deviation(df1, 'No', 'std_time')
            
            col6.metric('Desvio padrão sem festival', std_festival)
    
    
    with st.container():
        st.markdown('''---''')
        st.title('Tempo médio de entrega com desvio padrão por cidade em minutos:')
            
        fig = mean_time_per_city(df1)

        st.plotly_chart( fig, use_container_width = True )
        
        
    with st.container():
        st.markdown('''---''')
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown('### Média entre restaurante/residências por cidade em Km:')
        
            fig = mean_distance_per_city(df1)

            st.plotly_chart(fig, use_container_width = True )
            
        
        with col2:
           
            st.markdown('### Gráfico com tempo médio e desvio padrão por cidade e tipo de trânsito:')
            
            fig = mean_time_per_traffic_type(df1)
            st.plotly_chart(fig, use_container_width = True )
    
    
    with st.container():
        st.markdown('''---''')
        st.title('Tempo médio de entrega com desvio padrão por cidade e tipo de pedido')  
        
        std_festival = mean_time_city_order_type(df1)
        st.dataframe(std_festival, use_container_width = True )
