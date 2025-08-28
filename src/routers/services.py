from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from heroicons.jinja import heroicon_micro, heroicon_mini, heroicon_outline, heroicon_solid
from sqlmodel import Session, select

import utils
from database import get_session
from models import Service, AppSetting
from services import ServiceCRUD

# Create router for service-related endpoints
router = APIRouter(prefix="/services", tags=["services"])

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
def render_services_page(
    request: Request,
    session: SessionDependency
) -> HTMLResponse:
    """
    Renders the services page.

    Parameters:
    - request: Request - The incoming HTTP request object.
    - session: SessionDependency - A SQLModel session dependency for database access.

    Returns:
    - HTMLResponse: If successful, the HTML content of the services page in the body of the response, with HTTP status code 200 (OK).
    """
    all_services = session.exec(select(Service)).all()
    theme = session.get(AppSetting, "0000").setting_value
    colorTheme = session.get(AppSetting, "0001").setting_value
    return templates.TemplateResponse(
        request=request,
        name="services.html",
        context={"services": all_services, "theme": theme, "colorTheme": colorTheme}
    )

@router.post("/add_service")
def add_service(
    session: SessionDependency,
    name: str = Form(...),
    unit_price: str = Form(..., alias="unit-price"),
    description: str | None = Form(...)
) -> RedirectResponse:
    """
    Creates a new service.

    Parameters:
    - session: SessionDependency - A SQLModel session dependency for database access.
    - name: str - The name of the service.
    - unit_price: str - The unit price of the service.
    - description: str | None - The description of the service.

    Returns:
    - RedirectResponse: If successful, a redirect response to the services page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Validate the new service data
    new_service = utils.call_service_or_422(
        ServiceCRUD.validate_data,
        Service(
            name=name,
            description=description,
            unit_price=unit_price
        )
    )
    # Create the new service in the database
    create_status = utils.call_service_or_500(ServiceCRUD.create, new_service, session)

    return RedirectResponse(url="/services/", status_code=303)

@router.post("/edit_service")
def edit_service(
    session: SessionDependency,
    new_name: str = Form(..., alias="name"),
    new_description: str | None = Form(..., alias="description"),
    new_unit_price: str = Form(..., alias="unit-price"),
    service_id: int = Form(..., alias="service-id")
) -> RedirectResponse:
    """
    Edits attributes of an existing service.

    Parameters:
    - session: SessionDependency - A SQLModel session dependency for database access.
    - new_name: str - The new name of the service.
    - new_description: str | None - The new description of the service.
    - new_unit_price: str - The new unit price of the service.
    - service_id: int - The unique ID of the service to edit.

    Returns:
    - RedirectResponse: If successful, a redirect response to the services page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Validate the updated service data
    updated_service = utils.call_service_or_422(
        ServiceCRUD.validate_data,
        Service(
            name=new_name,
            description=new_description,
            unit_price=new_unit_price
        )
    )
    # Get the existing service from the database
    existing_service = utils.call_service_or_404(ServiceCRUD.get, service_id, session)
    # Update the existing service's attributes with the updated service's data
    update_status = utils.call_service_or_500(ServiceCRUD.update, existing_service, updated_service, session)

    return RedirectResponse(url="/services/", status_code=303)

@router.post("/remove_service")
def remove_service(
    session: SessionDependency,
    service_id: int = Form(..., alias="service-id")
) -> RedirectResponse:
    """
    Removes an existing service.

    Parameters:
    - session: SessionDependency - A SQLModel session dependency for database access.
    - service_id: int - The unique ID of the service to remove.

    Returns:
    - RedirectResponse: If successful, a redirect response to the services page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    delete_status = utils.call_service_or_500(ServiceCRUD.delete, service_id, session)

    return RedirectResponse(url="/services/", status_code=303)

@router.get("/api/all")
async def api_get_all_services(session: SessionDependency):
    all_services = session.exec(select(Service)).all()
    return all_services
