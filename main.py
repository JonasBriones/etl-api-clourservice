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
            df['assigned_to'] = df['assigned_to'].fillna('SIN ASIGNAR')
            df['waiting_for'] = df['assigned_to'].fillna('')
            # 1. Encontrar qué columnas tienen NaN
            nan_columns = df.columns[df.isna().any()].tolist()
            print(f"Columnas con NaN: {nan_columns}")
            
            # 2. Contar NaN por columna
            for col in nan_columns:
                nan_count = df[col].isna().sum()
                print(f"  - {col}: {nan_count} valores NaN")
            
            # 3. Ver registros específicos con NaN
            for col in nan_columns:
                problematic_rows = df[df[col].isna()].index.tolist()
                print(f"  - {col}: filas problemáticas {problematic_rows[:5]}")  # primeras 5
            
            # 4. Mostrar ejemplo de un registro problemático
            if len(problematic_rows) > 0:
                first_problem_row = problematic_rows[0]
                print(f"\nEjemplo de registro problemático (fila {first_problem_row}):")
                problem_record = df.iloc[first_problem_row][nan_columns].to_dict()
                print(json.dumps(problem_record, indent=2, default=str))
            
            # 5. Reemplazar NaN por None
            df = df.where(pd.notnull(df), None)
            
            records_list = df.to_dict(orient='records')
        return {
            "status": "OK",
            "filename": filename,
            "records": records_list,
            "total": len(df)
        }
    
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
