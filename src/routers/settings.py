from typing import Annotated, Any

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from heroicons.jinja import heroicon_micro, heroicon_mini, heroicon_outline, heroicon_solid
from requests import session
from sqlmodel import Session, select

import utils
from database import get_session
from models import AppSetting
from services import ServiceCRUD

# Create router for settings-related endpoints
router = APIRouter(prefix="/settings", tags=["settings"])

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

@router.get("/", response_class=HTMLResponse)
def render_settings_page(
    request: Request,
    session: SessionDependency
) -> HTMLResponse:
    """
    Renders the settings page.

    Parameters:
    - request: Request - The incoming HTTP request object.
    - session: SessionDependency - A SQLModel session dependency for database access.

    Returns:
    - HTMLResponse: If successful, the HTML content of the settings page in the body of the response, with HTTP status code 200 (OK).
    """
    all_app_settings = session.exec(select(AppSetting)).all()
    theme = session.get(AppSetting, "0000").setting_value
    colorTheme = session.get(AppSetting, "0001").setting_value
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={"app_settings": all_app_settings, "theme": theme, "colorTheme": colorTheme}
    )

@router.post("/save_settings")
async def save_app_settings(
    request: Request,
    session: SessionDependency,
) -> RedirectResponse:
    try:
        form = await request.form()

        all_app_settings = session.exec(select(AppSetting)).all()
        for app_setting in all_app_settings:
            if app_setting.id in form:
                app_setting.setting_value = form.get(app_setting.id)
                session.add(app_setting)
        session.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return RedirectResponse(url="/settings/", status_code=303)