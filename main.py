import os
from fastapi import FastAPI, Request, WebSocket, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Подключение к SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./click_data.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Определение моделей базы данных
class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    clicks = Column(Integer, default=0)


class User(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(Integer, nullable=True)


class ClickStats(Base):
    __tablename__ = "click_stats"
    id = Column(Integer, primary_key=True, index=True)
    total_clicks = Column(Integer, default=0)


# Создание таблиц, если они еще не созданы
Base.metadata.create_all(bind=engine)


# Зависимость для сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Настройки WebSocket и инкремента
count = 0
active_connections = []


@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    global count
    await websocket.accept()
    active_connections.append(websocket)

    # Создаем уникальный идентификатор для каждого пользователя
    session_id = str(uuid.uuid4())

    # Получаем или создаем общее количество кликов
    click_stat = db.query(ClickStats).first()
    if not click_stat:
        click_stat = ClickStats(total_clicks=count)
        db.add(click_stat)
        db.commit()
    count = click_stat.total_clicks

    # Создаем запись для сессии пользователя
    user_session = UserSession(session_id=session_id)
    db.add(user_session)
    db.commit()

    await websocket.send_json({"type": "count", "value": count, "session_clicks": user_session.clicks})

    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "increment":
                # Увеличиваем общий счетчик и сохраняем в базе
                count += 1
                click_stat.total_clicks = count
                db.commit()

                # Обновляем количество кликов пользователя
                user_session.clicks += 1
                db.commit()

                # Отправляем обновление всем пользователям
                for connection in active_connections:
                    await connection.send_json({
                        "type": "count",
                        "value": count,
                        "session_clicks": user_session.clicks
                    })
    except Exception as e:
        print("Client disconnected:", e)
    finally:
        active_connections.remove(websocket)


# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")
