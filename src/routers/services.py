from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from heroicons.jinja import heroicon_outline, heroicon_solid
from sqlmodel import Session, select

import utils
from database import get_session
from models import Service, AppSetting
from services import ServiceCRUD

# Create router for service-related endpoints
router = APIRouter(prefix="/services", tags=["services"])

# Create Jinja2 templates object for rendering HTML from the templates
# directory
templates = Jinja2Templates(directory="./templates")
templates.env.globals.update(
    {
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
    - request: The incoming HTTP request object.
    - session: A SQLModel session dependency for database access.

    Returns:
    - `HTMLResponse`: The rendered HTML content of the services page.
    """
    return templates.TemplateResponse(
        request=request,
        name="services.html",
        context={
            "services": session.exec(select(Service)).all(),
            "theme": session.get(AppSetting, "0000").setting_value,
            "colorTheme": session.get(AppSetting, "0001").setting_value
        }
    )

@router.post("/add_service")
def add_service(
    session: SessionDependency,
    name: str = Form(...),
    unit_price: str = Form(..., alias="unit-price"),
    description: str | None = Form(...)
) -> JSONResponse:
    """
    Creates a new service.

    Parameters:
    - session: A SQLModel session dependency for database access.
    - name: The name of the service.
    - unit_price: The unit price of the service.
    -description: The description of the service, if applicable.

    Returns:
    - `JSONResponse`: A JSON object containing a status message, status code, 
    and the newly created service object if the operation is successful.

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Validate the new service data
    validate_status, new_service = utils.call_service_or_422(
        ServiceCRUD.validate_data,
        Service(
            name=name,
            description=description,
            unit_price=unit_price
        )
    )
    
    # Create the new service in the database
    create_status, service = utils.call_service_or_500(
        ServiceCRUD.create,
        new_service,
        session
    )

    return JSONResponse(
        content={
            "detail": create_status,
            "service": {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "unit_price": str(service.unit_price),
            },
        },
        status_code=200,
    )

@router.post("/edit_service")
def edit_service(
    session: SessionDependency,
    new_name: str = Form(..., alias="name"),
    new_description: str | None = Form(..., alias="description"),
    new_unit_price: str = Form(..., alias="unit-price"),
    service_id: int = Form(..., alias="service-id")
) -> JSONResponse:
    """
    Edits attributes of an existing service.

    Parameters:
    - session: A SQLModel session dependency for database access.
    - new_name: The new name of the service.
    - new_description: The new description of the service.
    - new_unit_price: The new unit price of the service.
    - service_id: The unique ID of the service to edit.

    Returns:
    - `JSONResponse`: A JSON object containing a status message, status code, 
    and the edited service object if the operation is successful.

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 404 (NOT FOUND) if the service to edit does not exist in the database
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Validate the updated service data
    validate_status, updated_service = utils.call_service_or_422(
        ServiceCRUD.validate_data,
        Service(
            name=new_name,
            description=new_description,
            unit_price=new_unit_price
        )
    )

    # Get the existing service from the database
    get_status, existing_service = utils.call_service_or_404(
        ServiceCRUD.get,
        service_id,
        session
    )

    # Update the existing service's attributes with the updated service's data
    update_status, updated_service = utils.call_service_or_500(
        ServiceCRUD.update,
        existing_service,
        updated_service,
        session
    )

    return JSONResponse(
        content={
            "detail": update_status,
            "service": {
                "id": updated_service.id,
                "name": updated_service.name,
                "description": updated_service.description,
                "unit_price": str(updated_service.unit_price),
            },
        },
        status_code=200,
    )

@router.post("/remove_service")
def remove_service(
    session: SessionDependency,
    service_id: int = Form(..., alias="service-id")
) -> JSONResponse:
    """
    Removes an existing service.

    Parameters:
    - session: A SQLModel session dependency for database access.
    - service_id: The unique ID of the service to remove.

    Returns:
    - `JSONResponse`: A JSON object containing a status message, status code, 
    and the removed service object's unique id if the operation is successful.

    Raises:
    - HTTPException:
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    delete_status, service = utils.call_service_or_500(
        ServiceCRUD.delete,
        service_id,
        session
    )

    return JSONResponse(
        content={
            "detail": delete_status,
            "service": {
                "id": service.id,
            }
        },
        status_code=200,
    )

@router.get("/api/all")
async def api_get_all_services(session: SessionDependency):
    all_services = session.exec(select(Service)).all()
    return all_services