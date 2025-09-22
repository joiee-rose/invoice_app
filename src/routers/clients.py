import textwrap
from typing import Annotated
from decimal import Decimal

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from heroicons.jinja import heroicon_outline, heroicon_solid
from sqlmodel import Session, select

import utils
from database import get_session
from models import Client, Service, ClientQuoteProfile, Quote, AppSetting
from services import (
    ClientCRUD,
    ClientQuoteProfileCRUD,
    QuoteCRUD,
    AppSettingCRUD,
    PDFServices,
    EmailServices
)

# Create router for client-related endpoints
router = APIRouter(prefix="/clients", tags=["clients"])

# Create Jinja2 templates object for rendering HTML from the templates
templates = Jinja2Templates(directory="./templates")
templates.env.globals.update(
    {
        "heroicon_outline": heroicon_outline,
        "heroicon_solid": heroicon_solid,
    }
)

SessionDependency = Annotated[Session, Depends(get_session)]

@router.get("/", response_class=HTMLResponse)
def render_clients_page(
    request: Request,
    session: SessionDependency,
    page: int = 1
) -> HTMLResponse:
    """
    Renders the clients page.

    Parameters:
    - request: The incoming HTTP request object.
    - session: A SQLModel session dependency for database access.
    - page: The page number to display for table pagination (default is 1).

    Returns:
    - `HTMLResponse`: The rendered HTML content of the clients page.
    """
    # Determine number of clients to show per page based on screen height
    per_page = utils.get_per_page("clients")

    # Slice the list of all clients based on the number of clients per page
    all_clients = session.exec(select(Client)).all()
    total = len(all_clients)
    start = (page - 1) * per_page
    end = start + per_page
    page_clients = all_clients[start:end]
    # Count the number of pages necessary to show all the clients
    total_pages = (total + per_page - 1) // per_page

    # Convert clients lists to JSON-serializable format for use in javascript
    all_clients_dict = jsonable_encoder(all_clients)
    page_clients_dict = jsonable_encoder(page_clients)

    services = session.exec(select(Service)).all()
    services_data = [
        {
            "id": service.id,
            "name": service.name,
            "unit_price": str(service.unit_price)
        }
        for service in services
    ]

    # Get color theme and page colors
    color_theme = session.get(AppSetting, "0001").setting_value
    colors = utils.get_colors(color_theme)

    return templates.TemplateResponse(
        request=request, 
        name="clients.html", 
        context={
            "all_clients_dict": all_clients_dict,
            "page_clients": page_clients,
            "page_clients_dict": page_clients_dict,
            "services": services_data,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "theme": session.get(AppSetting, "0000").setting_value,
            "colorTheme": color_theme,
            **colors
        }
    )

@router.post("/add_client")
def add_client(
    session: SessionDependency,
    name: str = Form(...),
    business_name: str = Form(..., alias="business-name"),
    street_address: str = Form(..., alias="street-address"),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(..., alias="zip-code"),
    email: str = Form(...),
    phone: str = Form(...),
    page: int = 1
) -> JSONResponse:
    """
    Creates a new client.

    Parameters:
    - session: A SQLModel session dependency for database access.
    - name: The name of the client.
    - business_name: The business name of the client.
    - street_address: The street address of the client.
    - city: The city of the client.
    - state: The state of the client.
    - zip_code: The zip code of the client.
    - email: The email address of the client.
    - phone: The phone number of the client.
    - page: The page number to display for table pagination (default is 1).

    Returns:
    - `JSONResponse`: A JSON object containing a status message, status code, 
    and the newly created client object if the operation is successful.

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Determine number of clients shown per page based on screen height
    per_page = utils.get_per_page("clients")

    # Validate the new client data
    validate_status, new_client = utils.call_service_or_422(
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
    create_status, client = utils.call_service_or_500(
        ClientCRUD.create,
        new_client,
        session
    )

    # Count total number of clients after creation
    total_clients = len(session.exec(select(Client)).all())
    # Determine the new number of pages needed
    total_pages = (total_clients + per_page - 1) // per_page

    # If creating the new client caused a new page to be added, redirect to
    # that new page or the current page if total_pages is an unexpected value
    if total_pages > page:
        page = max(total_pages, page)

    return JSONResponse(
        content={
            "detail": create_status,
            "client": {
                "id": client.id,
                "name": client.name,
                "business_name": client.business_name,
                "street_address": client.street_address,
                "city": client.city,
                "state": client.state,
                "zip_code": client.zip_code,
                "email": client.email,
                "phone": client.phone,
            },
            "redirect_to": f"/clients?page={page}",
        },
        status_code=200,
    )

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
    client_id: int = Form(..., alias="client-id"),
    current_page: int = Form(..., alias="current-page")
) -> JSONResponse:
    """
    Edits attributes of an existing client.

    Parameters:
    - session: A SQLModel session dependency for database access.
    - new_name: The name of the client.
    - new_business_name: The business name of the client.
    - new_street_address: The street address of the client.
    - new_city: The city of the client.
    - new_state: The state of the client.
    - new_zip_code: The zip code of the client.
    - new_email: The email address of the client.
    - new_phone: The phone number of the client.
    - client_id: The unique ID of the client to edit.
    - current_page: The current page of clients being viewed in the table.

    Returns:
    - `JSONResponse`: A JSON object containing a status message, status code, 
    and the edited client object if the operation is successful.

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 404 (NOT FOUND) if the service to edit does not exist in the database
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Validate the updated client data
    validate_status, updated_client = utils.call_service_or_422(
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
    get_status, existing_client = utils.call_service_or_404(
        ClientCRUD.get,
        client_id,
        session
    )

    # Update the existing client's attributes with the updated client's data
    update_status, updated_client = utils.call_service_or_500(
        ClientCRUD.update,
        existing_client,
        updated_client,
        session
    )

    return JSONResponse(
        content={
            "detail": update_status,
            "client": {
                "id": updated_client.id,
                "name": updated_client.name,
                "business_name": updated_client.business_name,
                "street_address": updated_client.street_address,
                "city": updated_client.city,
                "state": updated_client.state,
                "zip_code": updated_client.zip_code,
                "email": updated_client.email,
                "phone": updated_client.phone,
            },
            "redirect_to": f"/clients?page={current_page}",
        },
        status_code=200,
    )

@router.post("/remove_client")
def remove_client(
    session: SessionDependency,
    client_id: int = Form(..., alias="client-id"),
    current_page: int = Form(..., alias="current-page")
) -> JSONResponse:
    """
    Removes an existing client. If the client has a client quote profile, it
    will also be removed.

    Parameters:
    - session: A SQLModel session dependency for database access.
    - client_id: The unique ID of the client to remove.
    - current_page: The current page of clients being viewed in the table.
    

    Returns:
    - `JSONResponse`: A JSON object containing a status message, status code, 
    and the removed service object's unique id if the operation is successful.

    Raises:
    - HTTPException:
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Determine number of clients shown per page based on screen height
    per_page = utils.get_per_page("clients")

    # Check if the client has a client quote profile
    existing_client_quote_profile = session.get(ClientQuoteProfile, client_id)
    # If the client has a client quote profile, delete it from the database
    if existing_client_quote_profile:
        delete_status, _ = utils.call_service_or_500(
            ClientQuoteProfileCRUD.delete,
            client_id,
            session
        )

    # Delete the client from the database
    delete_status, client = utils.call_service_or_500(
        ClientCRUD.delete,
        client_id,
        session
    )

    # Count total number of clients after deletion
    total_clients = len(session.exec(select(Client)).all())
    # Determine the new number of pages needed
    total_pages = (total_clients + per_page - 1) // per_page

    # If removing the client caused the page to be empty, redirect to the
    # previous page or the first page if total_pages is an unexpected value,
    # otherwise, stay on the current page
    if current_page > total_pages:
        current_page = max(total_pages, 1)

    return JSONResponse(
        content={
            "detail": delete_status,
            "client": {
                "id": client.id,
            },
            "redirect_to": f"/clients?page={current_page}",
        },
        status_code=200,
    )

@router.post("/save_quote_profile")
async def save_client_quote_profile(
    request: Request,
    session: SessionDependency,
    client_id: int = Form(..., alias="client-id"),
    min_monthly_charge: Decimal = Form(..., alias="min-monthly-charge"),
    premium_salt_upcharge: Decimal = Form(..., alias="premium-salt-upcharge"),
) -> JSONResponse:
    """
    Save the client's quote profile. If a quote profile already exists for the 
    client, it will be updated.

    Parameters:
    - request: The incoming HTTP request.
    - session: A SQLModel session dependency for database access.
    - client_id: The unique ID of the client.
    - min_monthly_charge: The minimum monthly charge for the client.
    - premium_salt_upcharge: The premium salt up-charge cost for the client.

    Returns:
    - `JSONResponse`: A JSON object containing a status message and status code.

    Raises:
    - HTTPException:
        - 422 (UNPROCESSABLE ENTITY) for form validation errors
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Extract the list of services from the form
    form = await request.form()
    services = []
    grand_total = 0

    service_names = form.getlist("service")
    quantities = form.getlist("quantity")
    per_units = form.getlist("per-unit")
    unit_prices = form.getlist("unit-price")
    taxes = form.getlist("tax")
    total_prices = form.getlist("total-price")

    for i in range(len(service_names)):
        services.append({
            "service_name": service_names[i],
            "quantity": quantities[i],
            "per_unit": per_units[i],
            "unit_price": unit_prices[i],
            "tax": taxes[i],
            "total_price": total_prices[i]
        })
        grand_total += Decimal(form.getlist("total-price")[i]) 

    # Validate the new client quote profile data
    _, new_client_quote_profile = utils.call_service_or_422(
        ClientQuoteProfileCRUD.validate_data,
        ClientQuoteProfile(
            client_id=client_id,
            min_monthly_charge=min_monthly_charge,
            premium_salt_upcharge=premium_salt_upcharge,
            services=services,
            grand_total=grand_total
        )
    )

    # Check if client quote profile already exists
    existing_client_quote_profile = session.get(ClientQuoteProfile, client_id)

    if existing_client_quote_profile:
        # Update the existing client quote profile's attributes with the new
        # client quote profile's data
        status, client_quote_profile = utils.call_service_or_500(
            ClientQuoteProfileCRUD.update,
            existing_client_quote_profile,
            new_client_quote_profile,
            session
        )
    else:
        # Create a new client quote profile in the database
        status, client_quote_profile = utils.call_service_or_500(
            ClientQuoteProfileCRUD.create,
            new_client_quote_profile,
            session
        )

    return JSONResponse(
        content={
            "detail": status,
            "client_id": client_quote_profile.client_id,
            "quote_profile": {
                "client_id": client_quote_profile.client_id,
                "min_monthly_charge": str(
                    client_quote_profile.min_monthly_charge
                ),
                "premium_salt_upcharge": str(
                    client_quote_profile.premium_salt_upcharge
                ),
                "services": client_quote_profile.services,
                "grand_total": str(client_quote_profile.grand_total)
            },
        },
        status_code=200,
    )

@router.post("/send_quote")
async def send_quote(
    request: Request,
    session: SessionDependency,
    client_id: int = Form(..., alias="client-id"),
    min_monthly_charge: Decimal = Form(..., alias="min-monthly-charge"),
    premium_salt_upcharge: Decimal = Form(..., alias="premium-salt-upcharge"),
):
    """
    Send a quote as a PDF to the client via email.

    Parameters:
    - request: The incoming HTTP request.
    - session: A SQLModel session dependency for database access.
    - client_id: The unique ID of the client.
    - min_monthly_charge: The minimum monthly charge for the client.

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

    service_names = form.getlist("service")
    quantities = form.getlist("quantity")
    per_units = form.getlist("per-unit")
    unit_prices = form.getlist("unit-price")
    taxes = form.getlist("tax")
    total_prices = form.getlist("total-price")

    for i in range(len(service_names)):
        services.append({
            "service_name": service_names[i],
            "quantity": quantities[i],
            "per_unit": per_units[i] if per_units[i] != "-1" else "--",
            "unit_price": unit_prices[i],
            "tax": taxes[i],
            "total_price": total_prices[i]
        })
        grand_total += Decimal(form.getlist("total-price")[i]) 

    # Get the client from the database
    client = session.get(Client, client_id)

    # Get the number of quotes existing for the client and generate a quote
    # number for the quote based on that value and the client's unique id
    _, num_quotes = utils.call_service_or_500(
        QuoteCRUD.count_by_client_id,
        client_id,
        session
    )
    quote_no = f"{client_id}-{str(num_quotes + 1).zfill(4)}"

    # Get the path to save quote PDFs to from app settings (id: 3000)
    _, app_setting = utils.call_service_or_404(
        AppSettingCRUD.get,
        "3000",
        session
    )
    pdf_save_path = app_setting.setting_value

    # Generate HTML source for the quote pdf
    _, html_source = utils.call_service_or_500(
        PDFServices.generate_html_source,
        file_type="quote",
        client=client,
        invoice_no=None,
        quote_no=quote_no,
        min_monthly_charge=min_monthly_charge,
        premium_salt_upcharge=premium_salt_upcharge,
        services=services,
        grand_total=grand_total
    )

    # Save the PDF
    _ = utils.call_service_or_500(
        PDFServices.save_pdf,
        file_type="quote",
        client=client,
        invoice_no=None,
        quote_no=quote_no,
        html_source=html_source,
        pdf_save_path=pdf_save_path,
    )

    # Get the quote email body from app settings (id: 3001)
    _, app_setting = utils.call_service_or_404(
        AppSettingCRUD.get,
        "3001",
        session
    )
    quote_email_body = app_setting.setting_value

    # Replace placeholders in the email body
    # Client Name
    quote_email_body = quote_email_body.replace("{{client.name}}", client.name)
    # Client Street Address
    quote_email_body = quote_email_body.replace(
        "{{client.street_address}}",
        client.street_address
    )
    # User's Business Email
    # User's Business Phone No.

    # Send the email
    _, _ = await utils.call_async_service_or_500(
        EmailServices.send_email,
        subject="M&M Quote Request",
        recipients=[client.email],
        body=quote_email_body,
        subtype="plain",
        attachments=[
            {
                "file": (
                    f'{pdf_save_path}/m&m-quote_'
                    f'{client.name.replace(" ", "_")}_{quote_no}.pdf'
                ),
                "mime_type": "application/pdf",
            }
        ]
    )

    # Validate the new quote data
    _, new_quote = utils.call_service_or_422(
        QuoteCRUD.validate_data,
        Quote(
            client_id=client_id,
            quote_no=quote_no,
            pdf_html=html_source,
        )
    )
    
    # Create the new quote in the database
    _, quote = utils.call_service_or_500(
        QuoteCRUD.create,
        new_quote,
        session
    )
    
    return RedirectResponse(url="/clients/", status_code=303)

@router.get("/get_client_quote_profile/{client_id}", response_class=JSONResponse)
async def get_client_quote_profile(
    session: SessionDependency,
    client_id: int
) -> JSONResponse:
    # Get the client quote profile from the database
    get_status, quote_profile = utils.call_service_or_404(
        ClientQuoteProfileCRUD.get,
        client_id,
        session
    )

    return JSONResponse(
        content={
            "detail": get_status,
            "quote_profile": {
                "client_id": quote_profile.client_id,
                "min_monthly_charge": str(quote_profile.min_monthly_charge),
                "premium_salt_upcharge": str(quote_profile.premium_salt_upcharge),
                "services": quote_profile.services,
                "grand_total": str(quote_profile.grand_total)
            },
        },
        status_code=200,
    )