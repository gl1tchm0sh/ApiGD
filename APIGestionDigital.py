from fastapi import FastAPI, status 
#status es para los codigos de estado (404, 401 etc)
from fastapi.params import Body
from classes import ConnData, ApiKey, ConnectionBroker
from routers import gestiondigital, auth
import pandas as pd
import json
from fastapi.middleware.cors import CORSMiddleware
#uvicorn APIGestionDigital:app --reload  
# 5:05:25 environment variables
# 11:24:14 git
# 12:05 deploy   12:30:43



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(gestiondigital.router)
app.include_router(auth.router)


@app.post('/comprobantes') # Agregar response_model = modelo para modificar el response con un pydantic basemodel
def get_connection_data(apikey:str):    
    conn_manager = ConnectionBroker()
    conn_manager.set_active_connection(apikey)
    query_str = """select  inv.type, 
                    inv.title, 
                    inv.cn, 
                    inv.date, 
                    inv.subtotal, 
                    inv.tax, 
                    inv.total, 
                    inv.status 
                    from
                    """ + f"{conn_manager.active_connection_data.bd}.sys_invoices inv"
    fetch_data = conn_manager.execute_query(query_str)
    column_names = ['type','title','cn','date','subtotal','tax','total','status']
    df = pd.DataFrame(fetch_data, columns=column_names)
    
    print(json.loads(df.to_json()))
    return json.loads(df.to_json())

