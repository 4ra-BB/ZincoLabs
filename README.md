# De Lead a Deal: Uso de datos abiertos para predecir la conversión de leads en clientes

Este repositorio contiene el código y recursos desarrollados en el Trabajo de Fin de Máster (TFM) “De Lead a Deal: cómo usar datos de una empresa disponibles en internet para evaluar la probabilidad de transformarlo en cliente”, realizado en la Universidad Complutense de Madrid (Máster NTIC, 2024–2025).

El objetivo principal es ayudar a ZincoLabs a identificar qué leads tienen más probabilidades de convertirse en clientes, utilizando ciencia de datos, machine learning y aplicaciones productivizadas.

Elementos del repositorio:

1. Datos: La base de daots se encuentran en el archivo technographics.cvs , dentro de la carpeta data
2. Códigos de modelado de datos: La creación del modelado de datos se encuentra en el archivo notebook.ipynb. En este archivo se realiza el descubirmiento exploratorio de datos y de efecto de las diferentes variables, hasta la productivización de un modelo productivo.
3. Códigos de app: Para utilizar el modelo productivizado, se utiliza una app, la cual está creada en el archivo app.py, dentro de la carpeta app. Esta carpeta incluye además un documento api.py, con los códigos para conectar las diferentes plataformas, y un archivo modelo_practico_optimizado.pkl, con el modelo creado en notebook.ipynb.

Cómo usar el repositorio:
Para poder replicar correctamente los archivos disponibles en el repositorio, es necesario seguir los siguientes pasos:
1. Descargar technographics.csv
2. Descargar notebook.ipynb y abrirlo en un programa para ejeutar el código, idealmente Jupyter Notebook o Goolge Collab.
3. Abrir el código en el apartado 1.2 (Preparación del entorno > Importación de datos), y modificar el camino para ubicar el archivo technographics.cvs.
4. Ejeutar el código completo.
5. Abrir la app utilizando el siguiente enlace: https://zincolabs-lead2deal.streamlit.app/
6. Completar los campos con la información requerida, y analizar el resultado.
