import io
import pandas as pd
from fastapi.responses import StreamingResponse
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv
import os
from fastapi import APIRouter, Depends
router = APIRouter()

load_dotenv()
raw_info= os.getenv("DB_CONNECT_INFO")
db_connect_info = raw_info.split(",") if raw_info else []
router = APIRouter()

pool = SimpleConnectionPool( minconn=1, maxconn=30,
                             database=db_connect_info[0],
        user=db_connect_info[1],
        host=db_connect_info[2],
        password=db_connect_info[3],
        port=int(db_connect_info[4]),
                            )

def get_db():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

# IMPORTANT TO DO: ADD ERROR HANDLING AND VALIDATE TABLE_NAME AGAINST A WHITELIST TO AVOID SQL INJECTION


@router.get("/export/{table_name}") #
def export_table(table_name: str, db=Depends(get_db)):
    df = pd.read_sql(f"SELECT * FROM {table_name}", db)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=table_name, index=False)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={table_name}.xlsx"},
    )


@router.get("/export/all")
def export_all(db=Depends(get_db)):
    tables = ["employee", "zones", "projects", "stations","hours_logged"]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for tbl in tables:
            df = pd.read_sql(f"SELECT * FROM {tbl}", db)
            df.to_excel(writer, sheet_name=tbl, index=False)
    output.seek(0)
    return StreamingResponse( output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition": "attachment; filename=all_tables.xlsx"},
    )
