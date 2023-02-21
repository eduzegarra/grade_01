# -*- coding: utf-8 -*-

# **Proyecto Papa Sostenible: Integración, Limpieza y Análisis Exploratorio**

## Librerías externas necesarias

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## **1. Lectura e integración de base de datos**

## Leemos primer libro del archivo Excel (volumen) asignado a objeto "vol" """

ruta = 'C:/Users/EDUARDO/Downloads/'

vol = pd.read_excel(ruta+'base_completa_1997_2021.xls', sheet_name='volumen')

vol.rename(columns={'m_1':'m_01','m_2':'m_02','m_3':'m_03','m_4':'m_04','m_5':'m_05','m_6':'m_06',
                    'm_7':'m_07','m_8':'m_08', 'm_9':'m_09'}, inplace=True)

# Leemos segundo libro (precios) asignado a objeto "pre"

pre = pd.read_excel(ruta+'base_completa_1997_2021.xls', sheet_name='precio')
pre.head()

pre.rename(columns={'m_1':'m_01','m_2':'m_02','m_3':'m_03','m_4':'m_04','m_5':'m_05','m_6':'m_06',
                    'm_7':'m_07','m_8':'m_08', 'm_9':'m_09'}, inplace=True)

## La columna 'Variable' identifica la provincia, cambiamos el nombre de la columna"""

vol.rename(columns={'Variable':'provincia'}, inplace=True)

## Las columnas m_01 a m_12 denotan meses. Necesitamos convertir al mes como una variable, para tener en cada fila una observacion, pasar base en formato ancho a largo (wide to long) usando el método **melt**"""

vol_long=pd.melt(vol,id_vars=['producto','year','provincia'], 
                var_name='mes', value_name='volumen')

## Lo mismo con la base de precios

pre_long=pd.melt(pre,id_vars=['producto','year'], 
                var_name='mes', value_name='precio')

### Damos una mirada a cada una de estas bases de datos

## primero el asunto de los valores "missing" (sin información)

pre_long.isna().sum()
## 963 valores missing
vol_long.isna().sum()
## 29187 valores missing

pre_long.dropna(inplace=True)
vol_long.dropna(inplace=True)

plt.figure(figsize=(9,5))
vol_long[vol_long['year']<=2020].groupby(vol_long.year)['volumen'].count().plot()
rr=np.arange(1997,2022,1)
plt.xticks(rr,rotation=45, fontsize='small')
plt.title('Número de observaciones de volumen por año', fontsize='xx-large')
plt.show()

plt.figure(figsize=(9,5))
vol_long[vol_long['year']<=2020].groupby(vol_long.year)['provincia'].nunique().plot()
rr=np.arange(1997,2022,1)
plt.xticks(rr,rotation=45, fontsize='small')
plt.title('Número de provincias por año en base volumen', fontsize='xx-large')
plt.show()

plt.figure(figsize=(9,5))
vol_long.groupby(vol_long.year)['producto'].nunique().plot()
rr=np.arange(1997,2022,1)
plt.xticks(rr,rotation=45, fontsize='small')
plt.title('Número de variedades por año en base volumen', fontsize='xx-large')
plt.show()

## Evaluamos base de precios con missing values (NaN)
# pre_long.precio.isna().sum()
# Hay 963 observaciones en base de precios con precio=NaN.  Decidimos eliminarlas"""
# pre_long.dropna(subset=['precio'],inplace=True)
# pre_long.precio.isna().sum()

plt.figure(figsize=(9,5))
pre_long[pre_long['year']<=2020].groupby(pre_long.year)['precio'].count().plot()
rr=np.arange(1997,2022,1)
plt.xticks(rr,rotation=45, fontsize='small')
plt.title('Número de observaciones por año en base precios', fontsize='xx-large')
plt.show()

## Bases 'vol_long' y 'pre_long' tienen una estructura similar y variables en comun y pueden ser integradas (usando método **merge**)

df_base=vol_long.merge(pre_long, on=['producto','year','mes'], how='left')
df_base

## En objeto generado como **df_base** en cada fila tenemos una observación que identifica la variedad, el año, la provincia, el mes así como el volumen y precio
## Notar que la variable precio corresponde a la variedad y mes, pero no varía por provincia de origen (el precio se forma en MML)
## Creamos variable 'ym' que identifica año y mes por observacion


df_base['ym']=df_base['year'].astype(str)+df_base['mes']

df_base.sort_values('ym', ascending=True)

## **2. Evaluación y limpieza de la base de datos**

## Creamos un objeto con el numero de observaciones con valor en el volumen transado por mes, uso del método **groupby** en Pandas

observ=df_base.groupby(df_base.ym)['volumen'].count()
plt.figure(figsize=(9,5))
plt.scatter(observ.index, observ, marker='.')
plt.xticks(rotation=90, fontsize='xx-small')
plt.title("Observaciones por mes en base volumen", fontsize='xx-large')
plt.show()

# df_base1 = df_base[(df_base['ym'] != '1997m_09')]

df_base.volumen.isna().sum()

## La base df_base ha pasado por un primer proceso
## de limpieza e integración: 
    # (i) convertimos bases en formato ancho a largo
    # (ii) eliminamos valores NaN en bases de volumen y precios
    # (iii) juntamos bases de volumen y precios
    # (iv) cambiamos algunos nombres de variables
    
df_base.describe(include='all')

## Esta es una primera base "limpia" y "ordenada" con la que se puede iniciar el análisis exploratorio.

## **3. Primer análisis exploratorio**

## Veremos el comportamiento de las variedades (su dinámica)

df_base.rename(columns={'producto':'variedad'}, inplace=True)

### Miramos precio y volumen por variedad usando **groupby**"""

df_base.groupby(df_base['variedad']).agg({'precio':['count','mean','min','max'], 'year':'min'})
df_base.groupby(df_base['variedad']).agg({'volumen':['count','mean','min','max'], 'year':'min'})

## Miramos la evolución de la oferta anual de algunas variedades

## 3.1.  Dinámica de oferta y precios

### Papa Blanca

plt.figure(figsize=(8,5))
vol_blanca=df_base[['year','volumen']][df_base.variedad=="Papa Blanca"].groupby('year').sum()
plt.bar(vol_blanca.index,vol_blanca.volumen)
plt.title("Papa Blanca: Volumen", fontsize='xx-large')
plt.xticks(vol_blanca.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
pre_blanca=df_base[['year','precio']][df_base.variedad=="Papa Blanca"].groupby('year').mean()
plt.plot(pre_blanca.index,pre_blanca.precio)
plt.title("Papa Blanca: Precio", fontsize='xx-large')
plt.xticks(pre_blanca.index,rotation=45, fontsize='small')
plt.show()

### Papa Yungay"""

plt.figure(figsize=(8,5))
vol_yungay=df_base[['year','volumen']][df_base.variedad=="Papa Yungay"].groupby('year').sum()
plt.bar(vol_yungay.index,vol_yungay.volumen)
plt.title("Papa Yungay: Volumen", fontsize='xx-large')
plt.xticks(vol_blanca.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
pre_yungay=df_base[['year','precio']][df_base.variedad=="Papa Yungay"].groupby('year').mean()
plt.plot(pre_yungay.index,pre_yungay.precio)
plt.title("Papa Yungay: Precio", fontsize='xx-large')
plt.xticks(pre_blanca.index,rotation=45, fontsize='small')
plt.show()

### Papa Huayro

plt.figure(figsize=(8,5))
vol_huayro=df_base[['year','volumen']][df_base.variedad=="Papa Huayro"].groupby('year').sum()
plt.bar(vol_huayro.index,vol_huayro.volumen)
plt.title("Papa Huayro: Volumen")
plt.xticks(vol_huayro.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
pre_huayro=df_base[['year','precio']][df_base.variedad=="Papa Huayro"].groupby('year').mean()
plt.plot(pre_huayro.index,pre_huayro.precio)
plt.title("Papa Huayro: Precio", fontsize='xx-large')
plt.xticks(pre_huayro.index,rotation=45, fontsize='small')
plt.show()

### Papa Canchan"""

plt.figure(figsize=(8,5))
vol_canchan=df_base[['year','volumen']][df_base.variedad=="Papa Canchan"].groupby('year').sum()
plt.bar(vol_canchan.index,vol_canchan.volumen)
plt.title("Papa Canchan: Volumen", fontsize='xx-large')
plt.xticks(vol_blanca.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
pre_canchan=df_base[['year','precio']][df_base.variedad=="Papa Canchan"].groupby('year').mean()
plt.plot(pre_canchan.index,pre_canchan.precio)
plt.title("Papa Canchan: Precio", fontsize='xx-large')
plt.xticks(pre_blanca.index,rotation=45, fontsize='small')
plt.show()

### Papa Amarilla

plt.figure(figsize=(8,5))
vol_amarilla=df_base[['year','volumen']][df_base.variedad=="Papa Amarilla"].groupby('year').sum()
plt.bar(vol_amarilla.index,vol_amarilla.volumen)
plt.title("Papa Amarilla: Volumen", fontsize='xx-large')
plt.xticks(vol_amarilla.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
pre_amarilla=df_base[['year','precio']][df_base.variedad=="Papa Amarilla"].groupby('year').mean()
plt.plot(pre_amarilla.index,pre_amarilla.precio)
plt.title("Papa Amarilla: Precio", fontsize='xx-large')
plt.xticks(pre_amarilla.index,rotation=45, fontsize='small')
plt.show()

### Papa Color"""

plt.figure(figsize=(8,5))
vol_color=df_base[['year','volumen']][df_base.variedad=="Papa Color"].groupby('year').sum()
plt.bar(vol_color.index,vol_color.volumen)
plt.title("Papa Color: Volumen", fontsize='xx-large')
plt.xticks(vol_color.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
pre_color=df_base[['year','precio']][df_base.variedad=="Papa Color"].groupby('year').mean()
plt.plot(pre_color.index,pre_color.precio)
plt.title("Papa Color: Precio", fontsize='xx-large')
plt.xticks(pre_color.index,rotation=45, fontsize='small')
plt.show()

### Papa Unica"""

plt.figure(figsize=(8,5))
vol_unica=df_base[['year','volumen']][df_base.variedad=="Papa Unica"].groupby('year').sum()
plt.bar(vol_unica.index,vol_unica.volumen)
plt.title("Papa Unica: Volumen", fontsize='xx-large')
plt.xticks(vol_blanca.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
pre_unica=df_base[['year','precio']][df_base.variedad=="Papa Unica"].groupby('year').mean()
plt.plot(pre_unica.index,pre_unica.precio)
plt.title("Papa Unica: Precio", fontsize='xx-large')
plt.xticks(pre_color.index,rotation=45, fontsize='small')
plt.show()

### Papa Peruanita"""

plt.figure(figsize=(8,5))
vol_peruanita=df_base[['year','volumen']][df_base.variedad=="Papa Peruanita"].groupby('year').sum()
plt.bar(vol_peruanita.index,vol_peruanita.volumen)
plt.title("Papa Peruanita: Volumen", fontsize='xx-large')
plt.xticks(vol_color.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
pre_peruanita=df_base[['year','precio']][df_base.variedad=="Papa Peruanita"].groupby('year').mean()
plt.plot(pre_peruanita.index,pre_peruanita.precio)
plt.title("Papa Peruanita: Precio", fontsize='xx-large')
plt.xticks(pre_color.index,rotation=45, fontsize='small')
plt.show()

## Papa Perricholi"""

plt.figure(figsize=(8,5))
vol_perricholi=df_base[['year','volumen']][df_base.variedad=="Papa Perricholi"].groupby('year').sum()
plt.bar(vol_perricholi.index,vol_perricholi.volumen)
plt.title("Papa Perricholi: Volumen", fontsize='xx-large')
plt.xticks(vol_color.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
pre_perricholi=df_base[['year','precio']][df_base.variedad=="Papa Perricholi"].groupby('year').mean()
plt.plot(pre_perricholi.index,pre_perricholi.precio)
plt.title("Papa Perricholi: Precio", fontsize='xx-large')
plt.xticks(pre_color.index,rotation=45, fontsize='small')
plt.show()

## Papa Huamantanga

plt.figure(figsize=(8,5))
vol_huamantanga=df_base[['year','volumen']][df_base.variedad=="Papa Huamantanga"].groupby('year').sum()
plt.bar(vol_huamantanga.index,vol_huamantanga.volumen)
plt.title("Papa Huamantanga: Volumen", fontsize='xx-large')
plt.xticks(vol_color.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
pre_huamantanga=df_base[['year','precio']][df_base.variedad=="Papa Huamantanga"].groupby('year').mean()
plt.plot(pre_huamantanga.index,pre_huamantanga.precio)
plt.title("Papa Huamantanga: Precio", fontsize='xx-large')
plt.xticks(pre_color.index,rotation=45, fontsize='small')
plt.show()

plt.figure(figsize=(8,5))
plt.plot(pre_yungay.index,pre_yungay.precio,label='Yungay')
plt.plot(pre_blanca.index,pre_blanca.precio, label='Blanca')
plt.plot(pre_canchan.index,pre_canchan.precio, label='Canchan')
plt.plot(pre_color.index,pre_color.precio, label='Color')
plt.plot(pre_perricholi.index,pre_perricholi.precio, label='Perricholi')
plt.title("Papa Blanca, Yungay, Canchan, Color, Perricholi: Precio", fontsize='large')
plt.xticks(pre_blanca.index,rotation=45, fontsize='small')
plt.legend()
plt.show()

plt.figure(figsize=(8,5))
plt.plot(pre_huayro.index,pre_huayro.precio, label='Huayro')
plt.plot(pre_amarilla.index,pre_amarilla.precio, label='Amarilla')
plt.plot(pre_peruanita.index,pre_peruanita.precio, label='Peruanita')
plt.plot(pre_huamantanga.index,pre_huamantanga.precio, label='Huamantanga')
plt.title("Papa Huayro, Amarilla, Peruanita y Huamantanga", fontsize='x-large')
plt.xticks(pre_blanca.index,rotation=45, fontsize='small')
plt.legend()
plt.show()

plt.figure(figsize=(8,5))
plt.plot(pre_blanca.index,pre_blanca.precio, label='Blanca')
plt.plot(pre_amarilla.index,pre_amarilla.precio, label='Amarilla')
plt.title("Papa Blanca y Amarilla", fontsize='x-large')
plt.xticks(pre_blanca.index,rotation=45, fontsize='small')
plt.legend()
plt.show()

## 3.2. Análisis de provincias de origen

### Papa Blanca

prv_blanca=df_base[['provincia','volumen']][df_base.variedad=="Papa Blanca"].groupby('provincia').sum()
prv_blanca.sort_values(by='volumen', ascending=False).head(20)

### Papa Amarilla"""

prv_amarilla=df_base[['provincia','volumen']][df_base.variedad=="Papa Amarilla"].groupby('provincia').sum()
prv_amarilla.sort_values(by='volumen', ascending=False).head(20)

## 3.3. Peso relativo de las provincias

## Creamos variable de valor (precio*volumen) para cada observación. Esta variable está en millones de soles

df_base['valor']=(df_base['volumen']*df_base['precio'])/1000

df_base.valor.describe()

vv_valor=pd.DataFrame(df_base[df_base['year']<=2020].groupby('year')['valor'].sum())

plt.figure(figsize=(8,5))
plt.bar(vv_valor.index,vv_valor.valor)
plt.suptitle("Valor de transacciones de Papa 1997-2020",fontsize='x-large')
plt.title("Millones de soles")
plt.xticks(vv_valor.index,rotation=45, fontsize='small')
plt.show()

## Generamos ranking de provincias de acuerdo a valor total de papa enviada a Lima entre 1997 y mayo 2021"""

rank_prov=df_base.groupby(df_base.provincia)['valor'].sum()

prov_19=rank_prov.sort_values(ascending=False)[0:19].sum()

prov_resto=rank_prov.sort_values(ascending=False)[19:121].sum()

prov_19/(prov_19+prov_resto)

## 19 provincias generan el 96.4% del valor total de la papa enviada a Lima, entonces tiene sentido acotar la base solamente a esas 20 provincias"""

rank_prov.sort_values(ascending=False)[0:19]

df_base2=df_base[df_base["provincia"].isin(['Huanuco','Huamanga','Huancayo','Tarma','Ambo','Pasco','Jauja',
          'Barranca','Huaral','Ica','Nazca','Arequipa','Andahuaylas','Canete', 'Huaura', 'Lima', 
          'Huancavelica', 'Tayacaja', 'Junin'])]

df_base2.provincia.unique()

df_base2.describe(include='all')

## 3.4. Análisis por región natural de origen"""

df_base2['costa']=df_base2['provincia'].isin(['Huaral','Lima','Barranca',
                'Nazca','Canete','Huaura','Arequipa','Ica']).astype('int')

## Peso de cada región en valor de producción por variedad"""

v_costa=df_base2[df_base2['costa']==1].groupby('variedad')['valor'].sum()
v_sierra=df_base2[df_base2['costa']==0].groupby('variedad')['valor'].sum()
v_total=v_costa+v_sierra
r_costa=(v_costa/v_total)*100

plt.figure(figsize=(9,5))
plt.bar(r_costa.index,r_costa)
plt.xticks(rotation=75)
plt.title("Porcentaje oferta de costa", fontsize='xx-large')
plt.show()

plt.figure(figsize=(9,5))
ll_costa=df_base2[(df_base2.costa==1) & (df_base2.year<=2020)].groupby('year')['valor'].sum()
ll_sierra=df_base2[(df_base2.costa==0) & (df_base2.year<=2020)].groupby('year')['valor'].sum()
plt.plot(ll_costa.index, ll_costa, label='Costa')
plt.plot(ll_sierra.index, ll_sierra, label='Sierra')
plt.legend(fontsize='large')
plt.suptitle('Valor de transacciones 1997-2020 por region natural', fontsize='xx-large')
plt.title('Millones de soles por año')
plt.xticks(ll_costa.index, rotation=45)
plt.show

plt.figure(figsize=(12,5))
mm_costa=df_base2[df_base2.costa==1].groupby('ym')['valor'].sum()
mm_sierra=df_base2[df_base2.costa==0].groupby('ym')['valor'].sum()
plt.plot(mm_costa.index, mm_costa, label='Costa')
plt.plot(mm_sierra.index, mm_sierra, label='Sierra')
plt.legend(fontsize='large')
plt.suptitle('Valor de transacciones 1997-2020 por region natural', fontsize='xx-large')
plt.title('Millones de soles por mes')
rr=mm_costa.index[np.arange(0,len(mm_costa),11)]
plt.xticks(rr, rotation=90, fontsize='small')
plt.show

## La base **df_base2** puede ser utilizada para el modelamiento 
## y análisis del mercado de papa (en sus distintas variedades) 
## de Lima Metropolitana.

df_base2.describe(include='all')

df_base2.to_excel(ruta+'df_base2.xlsx')
