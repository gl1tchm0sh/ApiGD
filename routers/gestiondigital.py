from fastapi import APIRouter
from classes import ConnectionBroker
import pandas as pd
import json


router = APIRouter(
    prefix='/gestiondigital',
    tags=['Core'] #Divisor para la documentacion
)

@router.get('/')
def test_router():
    return {"data":"This is a test"}

@router.post('/comprobante/')
def test_router(apikey,comprobante_id):

    conn_manager = ConnectionBroker()
    conn_manager.set_active_connection(apikey)
    query_str = """ SELECT 
                        inv.type           AS TIPO,
                        inv.Title          AS TITULO,
                        inv.cn             AS NUMERO,
                        inv.invoicenum     AS PUNTOVENTA,
                        DATE_FORMAT(inv.DATE, '%Y%m%d')           AS FECHA,
                        inv.subtotal       AS SUBTOTAL,
                        inv.discount_type  AS TIPO_DESCUENTO,
                        inv.discount_Value AS DESCUENTO_VALOR,
                        inv.discount       AS DESCUENTO ,
                        inv.tax            AS IVA,
                        inv.total          AS TOTAL,
                        inv.status         AS STATUS,
                        inv.currency       AS MONEDA,
                        inv.aid            AS PROVEEDOR,
                        inv.cae            AS CAE,
                        inv.fcae           AS FECHACAE,
                        inv.otrosimpuestos AS OTROSIMPUESTOS,
                        inv.ID             AS ID,
                        items.*
                    FROM 
                        """ + f"{conn_manager.active_connection_data.bd}.sys_invoices inv" + """
                    LEFT JOIN (
                            SELECT
                                invoiceid      AS TRID,
                                userid         AS PROVEEDOR,
                                itemcode       AS CODIGOITEM,
                                substring(description,locate('>',description)+1, locate('<',description,2)-1- locate('>',description)) AS DESCRIPCION,
                            
                                qty            AS CANTIDAD,
                                taxed          AS IMPUESTO,
                                tax_rate       AS IMPUESTOTASA,
                                taxamount     AS IMPUESTOMONTO,
                                discount_type  AS TIPO_DESCUENTO,
                                discoUnt_amount AS DESCUENTO,
                                total          AS TOTAL_I
                            FROM
                                """ + f"{conn_manager.active_connection_data.bd}.sys_invoiceitems) items on inv.ID = items.trid where inv.id ={comprobante_id}"
                    
    fetch_data = conn_manager.execute_query(query_str)
    column_names = ['TIPO','TITULO','NUMERO',
                    'PUNTOVENTA','FECHA','SUBTOTAL',
                    'TIPO_DESCUENTO','DESCUENTO_VALOR',
                    'DESCUENTO','IVA','TOTAL','STATUS',
                    'MONEDA','PROVEEDOR','CAE',
                    'FECHACAE','OTROSIMPUESTOS','ID',
                    'TRID','PROVEEDOR','CODIGOITEM','DESCRIPCION',
                    'CANTIDAD','IMPUESTO','IMPUESTOTASA',
                    'IMPUESTOMONTO','TIPO_DESCUENTO','DESCUENTO','TOTAL_I']

    df = pd.DataFrame(fetch_data, columns=column_names).fillna(0)
    to_broadcast = format_json(df)
    
    return to_broadcast


def format_json(df:pd.DataFrame):
    headers =   ['TIPO','TITULO','NUMERO',
                    'PUNTOVENTA','FECHA','SUBTOTAL',
                    'TIPO_DESCUENTO','DESCUENTO_VALOR',
                    'DESCUENTO','IVA','TOTAL','STATUS',
                    'MONEDA','PROVEEDOR','CAE',
                    'FECHACAE','OTROSIMPUESTOS','ID']
    
    df_headers = df[headers]
    df_items = df[df.columns.difference(headers).tolist()]

    df_headers_reoriented = df_headers.to_dict(orient='records')
    df_items_reoriented = df_items.to_dict(orient='records')

    df_headers_formatted = {linea['ID'] : {'cabecera' : linea} for linea in df_headers_reoriented}
    df_items_formatted = {linea['TRID'] : {'items' : list()} for linea in df_items_reoriented}
    df_items_formatted_append = [df_items_formatted[linea['TRID']]['items'].append(linea) for linea in df_items_reoriented]
    df_merge = dict()
    
    for key in df_headers_formatted.keys() | df_items_formatted.keys():
        df_merge[key] = {**df_headers_formatted.get(key, {}), **df_items_formatted.get(key, {})}

    df_resampled = pd.DataFrame(df_merge)
    to_broadcast = json.loads(df_resampled.to_json())
    return to_broadcast

