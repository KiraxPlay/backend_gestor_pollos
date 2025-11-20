# Backend gestor app pollos
El backend se desarrollo con Django usando arquitectura API_RESET

## Pre-Requisitos
- Tener Python instalado ver 3.13
- VSCode
- Extension Python
  
## Configuraciones iniciales
- python -m venv my_env ( mejor en este caso backendSmart) 
- my_env\Scripts\activate
- mkdir backend ( si se quiere clonar en una carpeta aparte)
- en la carpeta viene requirements.txt
- se pone el comando con el env activo pip install -r requirements.txt para instalar las librerias
- python manage.py runserver 0.0.0.0:8000
  esto se hace para que cualquier cosa corre en el puerto :8000 que seria en este caso donde estara ejecutandose la API 
