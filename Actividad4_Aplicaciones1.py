

#GRUPO
#JUAN DAVID CORRALES
#HUGO PALACIOS
#VICTOR TAMAYO


import plotly.express                as px
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash, callback, html, dcc
import os
import json

#Grafica el Mapa punto A
def grafico_mapa_muertes(df,geojson):
    #Data for Map
    dff = df.copy()
    dff=dff.groupby('DEPARTAMENTO').size().reset_index(name='Muertes')
    
    Map_Fig = px.choropleth_mapbox(
        dff,
        locations="DEPARTAMENTO",
        featureidkey="properties.NOMBRE_DPT",
        color="Muertes",
        geojson=geojson,
        zoom=3,
        mapbox_style="carto-positron",
        center={"lat": 4.570868, "lon": -74.2973328},
        color_continuous_scale="Viridis",
        opacity=0.5,
        )
    Map_Fig.update_layout(title="Muertes COVID-19 por Departamento en 2021", paper_bgcolor="#F8F9F9")
    return Map_Fig

# Gráfico de barras: 5 ciudades con mayor índice de muertes en 2021 . Punto B
def grafico_barras(df):
    dff=df.copy()
    df2=dff['MUNICIPIO'].value_counts().nlargest(5).reset_index(name='Muertes')
    figure=px.bar(df2, x='Muertes',y='MUNICIPIO', color='MUNICIPIO', title="Top 5 Ciudades con mayor índice de muertes en 2021")
    return figure

# Gráfico circular: Total de casos confirmados, sospechosos y descartados en 2021 Punto C

def grafico_circular(df):
    dff=df.copy()
    figure=px.pie(dff, names='COVID-19', title="Distribución de Casos COVID-19 en 2021", hole=.3, color_discrete_sequence=px.colors.sequential.RdBu)
    return figure

# Gráfico de línea: Muertes confirmadas por mes en 2020 y 2021 Punto D
def grafico_linea(df):
    dff=df.copy()
    #Filtramos los datos y agrupamos por intervalos de tiempo de final de mes 
    dff=dff[dff['COVID-19'] == 'CONFIRMADO'].set_index('FECHA DEFUNCIÓN').resample('ME').size().reset_index(name='Muertes')
    figure=px.line(dff, x='FECHA DEFUNCIÓN', y='Muertes', title="Muertes Confirmadas por Mes")
    return figure

# Gráfico de Histograma de frecuencias de muertes por edades quinquenales en 2020 Punto E
def grafico_histograma(df):
    dff=df.copy()
    #Organizamos los Daros 
    dff=dff.sort_values(by='EDAD FALLECIDO',ascending=True)
    figure=px.histogram(dff, x='EDAD FALLECIDO',nbins=36,title="Frecuencia de Muertes por Edad")
    
    return figure


# Cargamos el archivo a un dataframe con sus respectivo tipo de dato
df = pd.read_excel("data/Anexo4.Covid-19_CE_15-03-23.xlsx", dtype={'COVID-19':'category','DEPARTAMENTO':'string', 'MUNICIPIO':'string',
                                                              'AREA DEFUNCIÓN':'category','TIPO DEFUNCIÓN':'category',
                                                              'SEXO FALLECIDO':'category','ESTADO CONYUGAL FALLECIDO':'category','EDAD FALLECIDO':'category','NIVEL EDUCATIVO FALLECIDO':'category',
                                                              'RÉGIMEN SEGURIDAD':'category','PROBABLE MANERA MUERTE':'category','EXPEDIDO POR':'category','RECIBIÓ ASISTENCIA MEDICA':'category',
                                                              }
                   
                   )


#modificamos el tipo de dato para la fechas
df['FECHA DEFUNCIÓN']=pd.to_datetime(df['FECHA DEFUNCIÓN'], errors='coerce')
df['FECHA REGISTRO']=pd.to_datetime(df['FECHA REGISTRO'], errors='coerce')


#Cargamos la informacion de la cordenadas de los departamentos de colombia
DATA_DIR = "data/"
col_path = os.path.join(DATA_DIR, "colombiageo.json")
with open(col_path) as geo:
    geojson = json.loads(geo.read())

#Diccionario para normalizar nombres con la informacion del geofile
Departamento_dict ={'ATLÁNTICO':'ATLANTICO',
'CÓRDOBA':'CORDOBA',
'BOGOTÁ, D.C.':'BOGOTA',
'BOLÍVAR':'BOLIVAR',
'QUINDÍO':'QUINDIO',
'BOYACÁ':'BOYACA',
'CAQUETÁ':'CAQUETA',
'CHOCÓ':'CHOCO',
'GUAINÍA':'GUAINIA',
 'ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA':'SAN ANDRES Y PROVIDENCIA',
'VAUPÉS':'VAUPES'}

#Reemplazar nombres de departamentos
df['DEPARTAMENTO'] = df['DEPARTAMENTO'].replace(Departamento_dict)
#Quitamos los ultimos 3 caracteres de la edad
df['EDAD FALLECIDO']=df['EDAD FALLECIDO'].str[:-3]

#Volvemos la Edad un numero, y reemplazamos los que no tienen datos por NaN
df['EDAD FALLECIDO']=df['EDAD FALLECIDO'].replace('',np.nan)
df['EDAD FALLECIDO']=df['EDAD FALLECIDO'].astype(float)

#Informacion del año 2020
df_2020 = df[df['FECHA DEFUNCIÓN'].dt.year == 2020]
#Informacion del año 2021
df_2021 = df[df['FECHA DEFUNCIÓN'].dt.year == 2021]
#Informacion configrmados del año 2021
df_2021_confirmados = df_2021[df_2021['COVID-19'] == 'CONFIRMADO']


#Creamos los graficos
#Punto a.
figure_mapa=grafico_mapa_muertes(df_2021_confirmados,geojson)
#Punto b.
figure_barras=grafico_barras(df_2021_confirmados)
#Punto c.
figure_circular=grafico_circular(df_2021)
#Punto d.
figure_linea=grafico_linea(df)
#Punto e.
figure_histograma=grafico_histograma(df_2020)

## Crear la app de Dash
app = Dash()
server=app.server
Titulo=html.Div([ 
    html.H1('Dashboard Actividad 4 -COVID-19',style={'textAlign' : 'center'})
     ],className="text-center")
integrantes=html.Div([html.H5('Desarrollado por: Juan David Corrales, Hugo Palacios, Victor Tamayo',style={'textAlign' : 'center'})],)


grafica_punto_a= html.Div(children=[
        html.H3('Número total de muertes confirmadas por COVID-19 por departamento en 2021'),
        dcc.Graph(id='mapa-covid', 
                  figure=figure_mapa)
    ])

grafica_punto_b=html.Div(children=[
        html.H2('Top 5 ciudades con mayor índice de muertes confirmadas por COVID-19 en 2021'),
        dcc.Graph(id='bar-top5-ciudades',
                  figure=figure_barras)
    ])
grafica_punto_c=html.Div(children=[
        html.H2('Total de casos reportados como confirmados, sospechosos y descartados en 2021'),
        dcc.Graph(id='pie-casos',
                  figure=figure_circular)
    ])
grafica_punto_d=html.Div(children=[
        html.H2('Total de muertes confirmadas por COVID-19 por mes en 2020 y 2021'),
        dcc.Graph(id='line-muertes-mensuales',
                  figure=figure_linea)
    ])
grafica_punto_e=html.Div(children=[
        html.H2('Frecuencia de muertes confirmadas por COVID-19 por edades quinquenales en 2020'),
        dcc.Graph(id='histograma-edades',
                  figure=figure_histograma)
    ])
#Main layout

app.layout=html.Div(
    [
        dbc.Row( [Titulo]),
        dbc.Row( [integrantes]),    
        html.Hr(),
        dbc.Row( [grafica_punto_a]),
        dbc.Row( [ 
            dbc.Col([grafica_punto_b],width = 6 ),
            dbc.Col([grafica_punto_c],width = 6)

               ]),
        dbc.Row( [ 
            dbc.Col([grafica_punto_d],width = 6),
            dbc.Col([grafica_punto_e],width = 6)
               ])
       
    ]
    
)



# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=False)
