from sqlmodel import create_engine, Session

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
sqlite_conn_args = {"check_same_thread": False}
sqlite_engine = create_engine(sqlite_url, connect_args=sqlite_conn_args)

def get_session():
    with Session(sqlite_engine) as session:
        yield session