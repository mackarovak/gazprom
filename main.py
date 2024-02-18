from typing import Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.sql import func
from fastapi.responses import HTMLResponse
from typing import Dict
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

app = FastAPI()
templates = Jinja2Templates(directory="templates")


DATABASE_URL = "postgresql://nuancce:0516@db/database_statistics"
engine = create_engine(DATABASE_URL)
conn = engine.raw_connection()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String)


class Device(Base):
    __tablename__ = "devices"

    id_device = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.user_id"))


class Statistic(Base):
    __tablename__ = "statistics"

    id_statistic = Column(Integer, primary_key=True, autoincrement=True)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    id_device = Column(Integer, ForeignKey("devices.id_device"))
    time = Column(TIMESTAMP, default=func.now())


class DataInsert(BaseModel):
    x: float
    y: float
    z: float


Base.metadata.create_all(bind=engine)


class StatisticsRequest(BaseModel):
    start_date: datetime = None
    end_date: datetime = None


class CreateUserRequest(BaseModel):
    user_name: str


class UserResponse(BaseModel):
    user_id: int
    user_name: str


def insert_user_devices(user_names):

    cur = conn.cursor()

    sql_insert_user_devices = "INSERT INTO users (user_name) VALUES (%s);"

    cur.executemany(sql_insert_user_devices, [(name,) for name in user_names])

    conn.commit()

    cur.close()


def insert_devices(device_data):

    cur = conn.cursor()

    sql_insert_devices = "INSERT INTO devices (device_name, user_id) VALUES (%s, %s);"

    cur.executemany(sql_insert_devices, device_data)

    conn.commit()

    cur.close()


user_names = ["User1", "User2"]
device_data = [("Device 1",), ("Device 2",), ("Device 3",)]

insert_user_devices(user_names)
insert_devices(
    [
        (device_name, user_id)
        for device_name, user_id in zip(device_data, range(1, len(user_names) + 1))
    ]
)


@app.on_event("shutdown")
def shutdown_event():

    conn.close()


@app.on_event("startup")
async def startup_event():

    cur = conn.cursor()

    data_to_insert = [
        (15.0, 90.0, 3.0, 3, "2022-04-09"),
        (15.0, 25.0, 35.0, 2, datetime.now()),
    ]

    for data in data_to_insert:
        cur.execute(
            "INSERT INTO statistics (x, y, z, id_device, time) VALUES (%s, %s, %s, %s, %s)",
            data,
        )

    conn.commit()

    cur.close()


@app.post("/device/{id_device}/readings")
async def insert_data(id_device: int, data: DataInsert):
    x = data.x
    y = data.y
    z = data.z
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO statistics (x, y, z, id_device) VALUES (%s, %s, %s, %s)",
        (x, y, z, id_device),
    )

    conn.commit()

    cur.close()

    return {"message": "Data inserted successfully"}


@app.get("/device/{device_id}/readings")
async def get_data(device_id: int):

    cur = conn.cursor()

    cur.execute("SELECT x, y, z FROM statistics WHERE id_device = %s", (device_id,))

    row = cur.fetchone()

    cur.close()

    if not row:
        return {"error": "No data found for the specified device_id"}

    data = {"x": row[0], "y": row[1], "z": row[2]}

    return {"data": data}


@app.get("/devices/{id}/stats/")
async def get_characteristics(
    start_date: Optional[str] = None, end_date: Optional[str] = None
):
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD."
            )

        cur = conn.cursor()
        sql_query = """
        SELECT
            MIN(x) AS min_x,
            MAX(x) AS max_x,
            COUNT(x) AS count_x,
            SUM(x) AS sum_x,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x) AS median_x,
            MIN(y) AS min_y,
            MAX(y) AS max_y,
            COUNT(y) AS count_y,
            SUM(y) AS sum_y,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY y) AS median_y,
            MIN(z) AS min_z,
            MAX(z) AS max_z,
            COUNT(z) AS count_z,
            SUM(z) AS sum_z,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY z) AS median_z
        FROM
            statistics
        WHERE
            time BETWEEN %s AND %s
        """
        cur.execute(sql_query, (start_date, end_date))
        row = cur.fetchone()
        cur.close()

        characteristics = {
            "min_x": row[0],
            "max_x": row[1],
            "count_x": row[2],
            "sum_x": row[3],
            "median_x": row[4],
            "min_y": row[5],
            "max_y": row[6],
            "count_y": row[7],
            "sum_y": row[8],
            "median_y": row[9],
            "min_z": row[10],
            "max_z": row[11],
            "count_z": row[12],
            "sum_z": row[13],
            "median_z": row[14],
        }

        return characteristics
    else:
        cur = conn.cursor()
        sql_query = """
        SELECT
            MIN(x) AS min_x,
            MAX(x) AS max_x,
            COUNT(x) AS count_x,
            SUM(x) AS sum_x,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x) AS median_x,
            MIN(y) AS min_y,
            MAX(y) AS max_y,
            COUNT(y) AS count_y,
            SUM(y) AS sum_y,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY y) AS median_y,
            MIN(z) AS min_z,
            MAX(z) AS max_z,
            COUNT(z) AS count_z,
            SUM(z) AS sum_z,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY z) AS median_z
        FROM
            statistics
        """
        cur.execute(sql_query)
        row = cur.fetchone()
        cur.close()

        characteristics = {
            "min_x": row[0],
            "max_x": row[1],
            "count_x": row[2],
            "sum_x": row[3],
            "median_x": row[4],
            "min_y": row[5],
            "max_y": row[6],
            "count_y": row[7],
            "sum_y": row[8],
            "median_y": row[9],
            "min_z": row[10],
            "max_z": row[11],
            "count_z": row[12],
            "sum_z": row[13],
            "median_z": row[14],
        }

        return characteristics


@app.post("/users/", response_model=UserResponse)
async def create_user(user_request: CreateUserRequest):

    db = SessionLocal()

    new_user = User(user_name=user_request.user_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user_response = UserResponse(user_id=new_user.user_id, user_name=new_user.user_name)

    return user_response


def analyze_statistics_by_user(user_id):

    cur = conn.cursor()

    sql_query = """
    SELECT
        MIN(x) AS min_x,
        MAX(x) AS max_x,
        COUNT(x) AS count_x,
        SUM(x) AS sum_x,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY x) AS median_x,
        MIN(y) AS min_y,
        MAX(y) AS max_y,
        COUNT(y) AS count_y,
        SUM(y) AS sum_y,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY y) AS median_y,
        MIN(z) AS min_z,
        MAX(z) AS max_z,
        COUNT(z) AS count_z,
        SUM(z) AS sum_z,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY z) AS median_z
    FROM
        statistics
    WHERE
        id_device IN (
            SELECT id_device
            FROM devices
            WHERE user_id = %s
        )
    """

    cur.execute(sql_query, (user_id,))
    row = cur.fetchone()

    cur.close()

    result = {
        "min_x": row[0],
        "max_x": row[1],
        "count_x": row[2],
        "sum_x": row[3],
        "median_x": row[4],
        "min_y": row[5],
        "max_y": row[6],
        "count_y": row[7],
        "sum_y": row[8],
        "median_y": row[9],
        "min_z": row[10],
        "max_z": row[11],
        "count_z": row[12],
        "sum_z": row[13],
        "median_z": row[14],
    }

    return result


def analyze_statistics_by_user_device(user_id, device_id=None):

    cur = conn.cursor()

    sql_query = """
    SELECT
        d.user_id,
        s.id_device,
        MIN(s.x) AS min_x,
        MAX(s.x) AS max_x,
        COUNT(s.x) AS count_x,
        SUM(s.x) AS sum_x,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY s.x) AS median_x,
        MIN(s.y) AS min_y,
        MAX(s.y) AS max_y,
        COUNT(s.y) AS count_y,
        SUM(s.y) AS sum_y,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY s.y) AS median_y,
        MIN(s.z) AS min_z,
        MAX(s.z) AS max_z,
        COUNT(s.z) AS count_z,
        SUM(s.z) AS sum_z,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY s.z) AS median_z
    FROM
        statistics s
    JOIN
        devices d ON s.id_device = d.id_device
    WHERE
        d.user_id = %s
    """

    if device_id is not None:
        sql_query += " AND s.id_device = %s"
        params = (user_id, device_id)
    else:
        params = (user_id,)

    sql_query += " GROUP BY d.user_id, s.id_device"

    cur.execute(sql_query, params)
    rows = cur.fetchall()

    cur.close()

    results = []
    for row in rows:
        result = {
            "user_id": row[0],
            "id_device": row[1],
            "min_x": row[2],
            "max_x": row[3],
            "count_x": row[4],
            "sum_x": row[5],
            "median_x": row[6],
            "min_y": row[7],
            "max_y": row[8],
            "count_y": row[9],
            "sum_y": row[10],
            "median_y": row[11],
            "min_z": row[12],
            "max_z": row[13],
            "count_z": row[14],
            "sum_z": row[15],
            "median_z": row[16],
        }
        results.append(result)

    return results


@app.get("/users/{user_id}/devices/{device_id}/stats")
async def get_user_statistics(user_id: int, device_id: Optional[int] = None):

    results = analyze_statistics_by_user_device(user_id, device_id)
    if not results:
        raise HTTPException(status_code=404, detail="No statistics found")
    return results


@app.get("/users/{user_id}/stats")
async def get_user_statistics(user_id: int):

    results = analyze_statistics_by_user(user_id)
    if not results:
        raise HTTPException(status_code=404, detail="User not found")
    return results
