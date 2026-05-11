from typing import Annotated
from fastapi import FastAPI, File, UploadFile, HTTPException
import pandas as pd
import base64
from io import BytesIO
import json

app = FastAPI()

@app.post("/upload")
async def upload(file: UploadFile):
    print("*** Inicio del servicio ****")
    if not file:
        return {"message": "No upload file sent"}
    else:    
        if not file.filename.endswith((".json", ".xlsx", ".xml")):
            raise HTTPException(status_code=400, detail="Formato no permitido")

        #TRANSFORMAMOS EL ARCHIVO
        if file.filename.endswith(".xlsx"):
            f = await file.read()
            df = pd.read_excel(BytesIO(f))
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            #print(df.columns)
            json_string = df.to_json(orient='records')
        return {
            "status": "OK",
            "filename": file.filename,
            "data": json_string,
            "total": len(json_string)
        }