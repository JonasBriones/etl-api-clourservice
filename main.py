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

            #print(df.columns)
            json_string = df.to_dict(orient="records")
        return {
            "status": "OK",
            "filename": filename,
            "records": json_string,
            "total": len(json_string)
        }
    
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
