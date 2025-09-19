from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
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
    session: SessionDependency,
    page: int = 1
) -> HTMLResponse:
    """
    Renders the services page.

    Parameters:
    - request: The incoming HTTP request object.
    - session: A SQLModel session dependency for database access.
    - page: The current page of services being viewed in the table.
    - per_page: The maximum number of services to show per page in the table.

    Returns:
    - `HTMLResponse`: The rendered HTML content of the services page.
    """
    # Determine number of services to show per page based on screen height
    per_page = utils.get_per_page("services")

    # Slice the list of all services based on the number of services per page
    all_services = session.exec(select(Service)).all()
    total = len(all_services)
    start = (page - 1) * per_page
    end = start + per_page
    page_services = all_services[start:end]
    # Count the number of pages necessary to show all the services
    total_pages = (total + per_page - 1) // per_page

    # Convert services lists to JSON-serializable format for use in javascript
    all_services_dict = jsonable_encoder(all_services)
    page_services_dict = jsonable_encoder(page_services)

    return templates.TemplateResponse(
        request=request,
        name="services.html",
        context={
            "all_services_dict": all_services_dict,
            "page_services": page_services,
            "page_services_dict": page_services_dict,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "theme": session.get(AppSetting, "0000").setting_value,
            "colorTheme": session.get(AppSetting, "0001").setting_value
        }
    )

@router.post("/add_service")
def add_service(
    session: SessionDependency,
    name: str = Form(...),
    unit_price: str = Form(..., alias="unit-price"),
    description: str | None = Form(...),
    page: int = 1
) -> JSONResponse:
    """
    Creates a new service.

    Parameters:
    - session: A SQLModel session dependency for database access.
    - name: The name of the service.
    - unit_price: The unit price of the service.
    - description: The description of the service, if applicable.
    - page: The current page of services being viewed in the table.
    - per_page: The maximum number of services to show per page in the table.

    Returns:
    - `JSONResponse`: A JSON object containing a status message, status code, 
    and the newly created service object if the operation is successful.

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Determine number of services shown per page based on screen height
    per_page = utils.get_per_page("services")

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

    # Count total number of services after creation
    total_services = len(session.exec(select(Service)).all())
    # Determine the new number of pages needed
    total_pages = (total_services + per_page - 1) // per_page

    # If creating the new service caused a new page to be added, redirect to
    # that new page or the current page if total_pages is an unexpected value
    if total_pages > page:
        page = max(total_pages, page)

    return JSONResponse(
        content={
            "detail": create_status,
            "service": {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "unit_price": str(service.unit_price),
            },
            "redirect_to": f"/services?page={page}",
        },
        status_code=200,
    )

@router.post("/edit_service")
def edit_service(
    session: SessionDependency,
    new_name: str = Form(..., alias="name"),
    new_description: str | None = Form(..., alias="description"),
    new_unit_price: str = Form(..., alias="unit-price"),
    service_id: int = Form(..., alias="service-id"),
    page: int = 1,
) -> JSONResponse:
    """
    Edits attributes of an existing service.

    Parameters:
    - session: A SQLModel session dependency for database access.
    - new_name: The new name of the service.
    - new_description: The new description of the service.
    - new_unit_price: The new unit price of the service.
    - service_id: The unique ID of the service to edit.
    - page: The current page of services being viewed in the table.

    Returns:
    - `JSONResponse`: A JSON object containing a status message, status code, 
    the edited service object if the operation is successful, and a redirect
    path to the same page.

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
            "redirect_to": f"/services?page={page}",
        },
        status_code=200,
    )

@router.post("/remove_service")
def remove_service(
    session: SessionDependency,
    service_id: int = Form(..., alias="service-id"),
    current_page: int = Form(..., alias="current-page")
) -> JSONResponse:
    """
    Removes an existing service.

    Parameters:
    - session: A SQLModel session dependency for database access.
    - service_id: The unique ID of the service to remove.
    - page: The current page of services being viewed in the table.
    - per_page: The maximum number of services to show per page in the table.

    Returns:
    - `JSONResponse`: A JSON object containing a status message, status code, 
    the removed service object's unique id if the operation is successful, and
    the page to redirect to.

    Raises:
    - HTTPException:
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Determine number of services shown per page based on screen height
    per_page = utils.get_per_page("services")

    # Delete the service from the database
    delete_status, service = utils.call_service_or_500(
        ServiceCRUD.delete,
        service_id,
        session
    )

    # Count total number of services after deletion
    total_services = len(session.exec(select(Service)).all())
    # Determine the new number of pages needed
    total_pages = (total_services + per_page - 1) // per_page

    # If removing the service caused the page to be empty, redirect to the
    # previous page or the first page if total_pages is an unexpected value,
    # otherwise, stay on the current page
    if current_page > total_pages:
        current_page = max(total_pages, 1)

    return JSONResponse(
        content={
            "detail": delete_status,
            "service": {
                "id": service.id,
            },
            "redirect_to": f"/services?page={current_page}",
        },
        status_code=200,
    )

@router.get("/api/all")
async def api_get_all_services(session: SessionDependency):
    all_services = session.exec(select(Service)).all()
    return all_services