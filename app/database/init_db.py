from app.database.session import engine, Base


Base.metadata.create_all(bind=engine)
