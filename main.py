from fastapi import FastAPI, File, Request, HTTPException
import pandas as pd
import base64
from io import BytesIO
import json

app = FastAPI()

@app.get("/")
async def main():
    print("*** INICIO DE LA API ***")
    return {
        "status": "OK",
        "mensaje": "Inicio de la api"
    }

@app.post("/upload")
async def upload(request: Request):
    print("*** Inicio del servicio ****")
    try:       
        data = await request.json()

        file_base64 = data.get("file")
        filename = data.get("filename")

        if not file_base64:
            raise HTTPException(status_code=400, detail="No file received")

        # decodificar archivo
        file_bytes = base64.b64decode(file_base64)

        if not filename.endswith((".json", ".xlsx", ".xml")):
            raise HTTPException(status_code=400, detail="Formato no permitido")

        #TRANSFORMAMOS EL ARCHIVO
        if filename.endswith(".xlsx"):
            df = pd.read_excel(BytesIO(file_bytes))
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            df['title'] = df['number']

            columnas_deseadas = [
                'title',
                'state', 
                'assigned_to',
                'short_description',
                'priority',
                'short_description',
                'task_type',
                'description',
                'assignment_group',
                'work_notes'
            ]

            # Filtrar solo las columnas que existen en el DataFrame
            columnas_existentes = [col for col in columnas_deseadas if col in df.columns]
            df_filtrado = df[columnas_existentes]
            df_filtrado['work_notes'] = df_filtrado['work_notes'].fillna('')
            df_filtrado['assigned_to'] = df_filtrado['assigned_to'].fillna('SIN ASIGNAR')
            
            records_list = df_filtrado.to_dict(orient='records')
        return {
            "status": "OK",
            "filename": filename,
            "records": records_list,
            "total": len(records_list)
        }
    
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
