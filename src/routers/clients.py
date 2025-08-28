import textwrap
from typing import Annotated
from decimal import Decimal

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from heroicons.jinja import heroicon_micro, heroicon_mini, heroicon_outline, heroicon_solid
from sqlmodel import Session, select

import utils
from database import get_session
from models import Client, ClientQuoteProfile, AppSetting
from services import ClientCRUD, ClientQuoteProfileCRUD, PDFServices, EmailServices

# Create router for client-related endpoints
router = APIRouter(prefix="/clients", tags=["clients"])

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
def render_clients_page(
    request: Request,
    session: SessionDependency
) -> HTMLResponse:
    """
    Renders the clients page.

    Parameters:
    - request: Request - The incoming HTTP request object.
    - session: SessionDependency - A SQLModel session dependency for database access.

    Returns:
    - HTMLResponse: If successful, the HTML content of the clients page in the body of the response, with HTTP status code 200 (OK).
    """
    all_clients = session.exec(select(Client)).all()
    theme = session.get(AppSetting, "0000").setting_value
    colorTheme = session.get(AppSetting, "0001").setting_value
    return templates.TemplateResponse(
        request=request, 
        name="clients.html", 
        context={"clients": all_clients, "theme": theme, "colorTheme": colorTheme}
    )

@router.post("/add_client")
def create_client(
    session: SessionDependency,
    name: str = Form(...),
    business_name: str = Form(..., alias="business-name"),
    street_address: str = Form(..., alias="street-address"),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(..., alias="zip-code"),
    email: str = Form(...),
    phone: str = Form(...)
) -> RedirectResponse:
    """
    Creates a new client.

    Parameters:
    - session: SessionDependency - A SQLModel session dependency for database access.
    - name: str - The name of the client.
    - business_name: str - The business name of the client.
    - street_address: str - The street address of the client.
    - city: str - The city of the client.
    - state: str - The state of the client.
    - zip_code: str - The zip code of the client.
    - email: str - The email address of the client.
    - phone: str - The phone number of the client.

    Returns:
    - RedirectResponse: If successful, a redirect response to the clients page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Validate the new client data
    new_client = utils.call_service_or_422(
        ClientCRUD.validate_data,
        Client(
            name=name,
            business_name=business_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_code=zip_code,
            email=email,
            phone=phone
        )
    )
    # Create the new client in the database
    create_status = utils.call_service_or_500(ClientCRUD.create, new_client, session)

    return RedirectResponse(url="/clients/", status_code=303)

@router.post("/edit_client")
def edit_client(
    session: SessionDependency,
    new_name: str = Form(..., alias="name"),
    new_business_name: str = Form(..., alias="business-name"),
    new_street_address: str = Form(..., alias="street-address"),
    new_city: str = Form(..., alias="city"),
    new_state: str = Form(..., alias="state"),
    new_zip_code: str = Form(..., alias="zip-code"),
    new_email: str = Form(..., alias="email"),
    new_phone: str = Form(..., alias="phone"),
    client_id: int = Form(..., alias="client-id")
) -> RedirectResponse:
    """
    Edits attributes of an existing client.

    Parameters:
    - session: SessionDependency - A SQLModel session dependency for database access.
    - new_name: str - The name of the client.
    - new_business_name: str - The business name of the client.
    - new_street_address: str - The street address of the client.
    - new_city: str - The city of the client.
    - new_state: str - The state of the client.
    - new_zip_code: str - The zip code of the client.
    - new_email: str - The email address of the client.
    - new_phone: str - The phone number of the client.
    - client_id: int - The unique ID of the client to edit.

    Returns:
    - RedirectResponse: If successful, a redirect response to the clients page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Validate the updated client data
    updated_client = utils.call_service_or_422(
        ClientCRUD.validate_data,
        Client(
            name=new_name,
            business_name=new_business_name,
            street_address=new_street_address,
            city=new_city,
            state=new_state,
            zip_code=new_zip_code,
            email=new_email,
            phone=new_phone
        )
    )
    # Get the existing client from the database
    existing_client = utils.call_service_or_404(ClientCRUD.get, client_id, session)
    # Update the existing client's attributes with the updated client's data
    update_status = utils.call_service_or_500(ClientCRUD.update, existing_client, updated_client, session)

    return RedirectResponse(url="/clients/", status_code=303)

@router.post("/remove_client")
def remove_client(
    session: SessionDependency,
    client_id: int = Form(..., alias="client-id")
) -> RedirectResponse:
    """
    Removes an existing client.

    Parameters:
    - session: SessionDependency - A SQLModel session dependency for database access.
    - client_id: int - The unique ID of the client to remove.

    Returns:
    - RedirectResponse: If successful, a redirect response to the clients page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    delete_status = utils.call_service_or_500(ClientCRUD.delete, client_id, session)

    return RedirectResponse(url="/clients/", status_code=303)

@router.post("/save_quote_profile")
async def save_client_quote_profile(
    request: Request,
    session: SessionDependency,
    client_id: int = Form(..., alias="client-id"),
    services_count: int = Form(..., alias="services-count")
) -> RedirectResponse:
    """
    Save the client's quote profile. If a quote profile already exists for this client, it will be updated.

    Parameters:
    - request: Request - The incoming HTTP request.
    - session: SessionDependency - A SQLModel session dependency for database access.
    - client_id: int - The unique ID of the client.
    - services_count: int - The number of services in the quote profile.

    Returns:
    - RedirectResponse: If successful, a redirect response to the clients page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Extract the list of services from the form
    form = await request.form()
    services = []
    grand_total = 0
    for i in range(services_count):
        services.append({
            "service_id": form.get(f"service-{i}"),
            "service_name": form.get(f"service-name-{i}"),
            "quantity": form.get(f"quantity-{i}"),
            "per_unit": form.get(f"per-unit-{i}"),
            "unit_price": form.get(f"unit-price-{i}"),
            "total_price": form.get(f"total-price-{i}")
        })
        grand_total += Decimal(form.get(f"total-price-{i}")) 

    # Validate the new client quote profile data
    new_client_quote_profile = utils.call_service_or_422(
        ClientQuoteProfileCRUD.validate_data,
        ClientQuoteProfile(
            client_id=client_id,
            services=services,
            grand_total=grand_total
        )
    )
    # Check if client quote profile already exists
    existing_client_quote_profile = session.get(ClientQuoteProfile, client_id)
    if existing_client_quote_profile:
        # Update the existing client quote profile's attributes with the new client quote profile's data
        update_status = utils.call_service_or_500(ClientQuoteProfileCRUD.update, existing_client_quote_profile, new_client_quote_profile, session)
    else:
        # Create a new client quote profile in the database
        create_status = utils.call_service_or_500(ClientQuoteProfileCRUD.create, new_client_quote_profile, session)

    return RedirectResponse(url="/clients/", status_code=303)

@router.post("/send_quote")
async def send_quote(
    request: Request,
    session: SessionDependency,
    client_id: int = Form(..., alias="client-id"),
    services_count: int = Form(..., alias="services-count")
):
    """
    Send a quote as a PDF to the client via email.

    Parameters:
    - request: Request - The incoming HTTP request.
    - session: SessionDependency - A SQLModel session dependency for database access.
    - client_id: int - The unique ID of the client.
    - services_count: int - The number of services in the quote.

    Returns:
    - RedirectResponse: If successful, a redirect response to the clients page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Extract the list of services from the form
    form = await request.form()
    services = []
    grand_total = 0
    for i in range(services_count):
        services.append({
            "service_id": form.get(f"service-{i}"),
            "service_name": form.get(f"service-name-{i}"),
            "quantity": form.get(f"quantity-{i}"),
            "per_unit": form.get(f"per-unit-{i}"),
            "unit_price": form.get(f"unit-price-{i}"),
            "total_price": form.get(f"total-price-{i}")
        })
        grand_total += Decimal(form.get(f"total-price-{i}"))
    # Get the client from the database
    client = session.get(Client, client_id)
    # TODO - Get the path to save invoice PDFs to from app settings
    pdf_save_path = "../"

    # Generate HTML source for the quote pdf
    html_source = utils.call_service_or_500(
        PDFServices.generate_html_source,
        file_type="quote",
        client=client,
        invoice_no=None,
        services=services,
        grand_total=grand_total
    )
    # Save the PDF
    pdf_status = utils.call_service_or_500(
        PDFServices.save_pdf,
        html_source=html_source,
        pdf_save_path=pdf_save_path,
        file_type="quote",
        invoice_no=None,
        client_name=client.name
    )
    # Send the email
    email_status = await utils.call_async_service_or_500(
        EmailServices.send_email,
        subject="Quote Request",
        recipients=[client.email],
        body=textwrap.dedent(f"""\
            Dear {client.name},

            This is a quote :)))
        """),
        subtype="plain",
        attachments=[
            {
                "file": f"../quote_{client.name.replace(" ", "_")}.pdf",
                "mime_type": "application/pdf",
            }
        ]
    )
    
    return RedirectResponse(url="/clients/", status_code=303)

@router.get("/api/quote_profile/{client_id}", response_class=HTMLResponse)
async def api_get_client_quote_profile(
    session: SessionDependency,
    client_id: int
) -> HTMLResponse:
    try:
        client_quote_profile = session.get(ClientQuoteProfile, client_id)
        if not client_quote_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client has no quote profile."
            )
        return HTMLResponse(content=client_quote_profile.model_dump_json(), status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )