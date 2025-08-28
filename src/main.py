import os
from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from heroicons.jinja import heroicon_micro, heroicon_mini, heroicon_outline, heroicon_solid
from fastapi_tailwind import tailwind
from sqlmodel import SQLModel, Session

from routers import clients, services, invoices, settings
from database import sqlite_engine, get_session
from models import Client, Service, ClientQuoteProfile, Invoice, AppSetting

@asynccontextmanager
async def lifespan(app: FastAPI):
    ### Do on Startup ###
    # Create database tables if they don't exist
    SQLModel.metadata.create_all(sqlite_engine)

    # Start Tailwind CSS compiler process
    process = tailwind.compile(
        StaticFiles(directory = "static").directory + "/css/output.css",
        tailwind_stylesheet_path = "./static/css/input.css"
    )

    # Populate AppSettings table with default settings, if they do not exist already
    project_root_abs_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_app_settings = [
        # 0000 series: General App Settings
        AppSetting(id="0000", category="general", setting_name="theme", setting_value="light"),
        AppSetting(id="0001", category="general", setting_name="color-theme", setting_value="blue-400"),
        # 1000 series: Client Settings
        # 2000 series: Service Settings
        # 3000 series: Invoice Settings
        AppSetting(id="3000", category="invoices", setting_name="pdf-save-to-path", setting_value=project_root_abs_dir_path)
    ]

    with Session(sqlite_engine) as session:
        for default_setting in default_app_settings:
            setting = session.get(AppSetting, default_setting.id)
            if not setting:
                session.add(default_setting)
                session.commit()

    yield
    ### Do on Shutdown ###
    # Stop Tailwind CSS compiler process
    process.terminate()

# Create FastAPI app with lifespan context manager
app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Attach routers
app.include_router(clients.router)
app.include_router(services.router)
app.include_router(invoices.router)
app.include_router(settings.router)

# Create Jinja2 templates object for rendering HTML from the templates directory
templates = Jinja2Templates(directory="./templates")
templates.env.globals.update(
    {
        "heroicon_micro": heroicon_micro,
        "heroicon_mini": heroicon_mini,
        "heroicon_outline": heroicon_outline,
        "heroicon_solid": heroicon_solid,
    }
)

SessionDependency = Annotated[Session, Depends(get_session)]

@app.get("/", response_class=HTMLResponse)
async def render_dashboard_page(
    request: Request,
    session: SessionDependency
) -> HTMLResponse:
    """
    Renders the dashboard page. This is the primary page of the application.

    Parameters:
    - request: Request - The incoming HTTP request object.
    - session: SessionDependency - A SQLModel session dependency for database access.

    Returns:
    - HTMLResponse: The rendered HTML content of the dashboard page.
    """
    theme = session.get(AppSetting, "0000").setting_value
    colorTheme = session.get(AppSetting, "0001").setting_value
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"theme": theme, "colorTheme": colorTheme}
    )