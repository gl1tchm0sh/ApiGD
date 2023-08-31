from pydantic import BaseModel
import mysql.connector
import pandas as pd
from config import settings


class ApiKey(BaseModel):
    apikey : str

class ConnData(BaseModel):
    apikey  :   str
    empresa :   str
    servidor:   str
    puerto  :   str
    usuario :   str
    passwd  :   str
    bd      :   str

    def __str__(self):
        return f"Datos de conexión para:\n\tEmpresa: {self.empresa}\n\tUsuario: {self.usuario}"
    
    def parse_data_tuple(data):
        return ConnData(apikey   =   data[0][1],
                        empresa  =   data[0][2],
                        servidor =   data[0][3],
                        puerto   =   str(data[0][4]),
                        usuario  =   data[0][5],
                        passwd   =   data[0][6],
                        bd       =   data[0][7]
                        )

class ConnectionBroker():
    BASE_CONNECTION_DATA = ConnData(apikey =    '',
                                    empresa =   'Gestiondigital',
                                    servidor =  settings.SERVIDOR,
                                    puerto =    settings.PUERTO,
                                    usuario =   settings.USUARIO,
                                    passwd =    settings.PASSWD,
                                    bd =        settings.BD
                            )
    
    def __init__(self):
        self._base_connection = self.connect_to_mysql(self.BASE_CONNECTION_DATA)
        self._active_connection_data = None
        self._active_connection = None
    
    @property
    def base_connection(self):
        return self._base_connection

    @base_connection.setter
    def base_connection(self, connection):
        self._base_connection = connection
    
    @property
    def active_connection_data(self):
        return self._active_connection_data
    
    @active_connection_data.setter
    def active_connection_data(self,ConnData:ConnData):
        self._active_connection_data = ConnData
    
    @property
    def active_connection(self):
        return self._active_connection
    
    @active_connection.setter
    def active_connection(self,connection):
        self._active_connection = connection

    def connect_to_mysql(self, ConnData:ConnData):
        try:
            db_connection = mysql.connector.connect(
                            host    =   ConnData.servidor,
                            port    =   ConnData.puerto,
                            database=   ConnData.bd,
                            user    =   ConnData.usuario,
                            password=   ConnData.passwd
                            )
            return db_connection
        except Exception as error:
           print('Connection failed')
           print(error)

    def set_active_connection(self,apikey:str):
        # Seleccionar la conexion segun el campo apikey, 
        # hacer el select pertinente al base_connection
        fetch_query = f"select * from config where apikey = '{apikey}'"
        print(apikey)
        new_connection_data_tuple = self.execute_query(fetch_query)
        new_connection_data = ConnData.parse_data_tuple(new_connection_data_tuple)
        self.active_connection_data = new_connection_data

        new_connection = self.connect_to_mysql(new_connection_data)
        self.active_connection = new_connection
        print(f'New connection established: {self.active_connection_data}')

    def execute_query(self, query_string):
        conn = self.base_connection if self._active_connection == None else self.base_connection
        cur = conn.cursor()
        cur.execute(query_string)
        data = cur.fetchall()
        cur.close()
        return data


if __name__ == '__main__':
    conn = ConnectionBroker()
    print('Connected')
    conn.set_active_connection('x')
    
    query_str = """select  inv.type, 
                    inv.title, 
                    inv.cn, 
                    inv.date, 
                    inv.subtotal, 
                    inv.tax, 
                    inv.total, 
                    inv.status 
                    from cloudnex2.sys_invoices inv"""
    fetch = conn.execute_query(query_str)

    column_names = ['type','title','cn','date','subtotal','tax','total','status']
    df = pd.DataFrame(fetch, columns=column_names)
    df.to_json()
    print(df)