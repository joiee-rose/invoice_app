from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from heroicons.jinja import heroicon_outline, heroicon_solid
from sqlmodel import Session, select

import utils
from database import get_session
from models import (
    Client,
    Service,
    Quote,
    ClientQuoteProfile,
    TempClientQuoteProfile,
    AppSetting
)
from services import (
    TempClientQuoteProfileCRUD,
    QuoteCRUD,
    AppSettingCRUD,
    PDFServices,
    EmailServices
)

# Create router for quote-related endpoints
router = APIRouter(prefix="/quotes", tags=["quotes"])

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
def render_quotes_page(
    request: Request,
    session: SessionDependency,
    page: int = 1
) -> HTMLResponse:
    """
    Renders the quotes page.

    Parameters:
    - request: The incoming HTTP request object.
    - session: A SQLModel session dependency for database access.
    - page: The page number to display for table pagination (default is 1).

    Returns:
    - `HTMLResponse`: The rendered HTML content of the clients page.
    """
    # Determine the number of quotes to show per page based on screen height
    per_page = utils.get_per_page("quotes")

    # Slice the list of all quotes based on the number of quotes per page
    all_quotes = session.exec(select(Quote)).all()
    total = len(all_quotes)
    start = (page - 1) * per_page
    end = start + per_page
    page_quotes = all_quotes[start:end]
    # Count the number of pages necessary to show all the quotes
    total_pages = (total + per_page - 1) // per_page

    # Convert quotes lists to JSON serializable format for use in javascript
    all_quotes_dict = jsonable_encoder(all_quotes)
    page_quotes_dict = jsonable_encoder(page_quotes)
    # Convert services list to JSON serializable format for use in javascript
    all_services_dict = jsonable_encoder(session.exec(select(Service)).all())

    # Write the clients' quote profiles to the temporary quote profiles table
    all_clients = session.exec(select(Client)).all()
    for client in all_clients:
        client_id = client.id

        # Get quote profile and temp quote profile for the client
        quote_profile = session.get(ClientQuoteProfile, client_id)
        temp_quote_profile = session.get(TempClientQuoteProfile, client_id)

        # If there is no temp quote profile, create one from the quote profile
        if temp_quote_profile is None:    
            temp_quote_profile = TempClientQuoteProfile(
                    client_id=quote_profile.client_id,
                    min_monthly_charge=quote_profile.min_monthly_charge,
                    premium_salt_upcharge=quote_profile.premium_salt_upcharge,
                    services=quote_profile.services,
                    grand_total=quote_profile.grand_total
                )

            _, temp_quote_profile = utils.call_service_or_500(
                TempClientQuoteProfileCRUD.create,
                temp_quote_profile,
                session
            )
        # Otherwise, update the temp quote profile in case the quote profile
        # has changed
        else:
            existing_temp_quote_profile = session.get(TempClientQuoteProfile, client_id)

            _, new_temp_quote_profile = utils.call_service_or_422(
                TempClientQuoteProfileCRUD.validate_data,
                TempClientQuoteProfile(
                    client_id=quote_profile.client_id,
                    min_monthly_charge=quote_profile.min_monthly_charge,
                    premium_salt_upcharge=quote_profile.premium_salt_upcharge,
                    services=quote_profile.services,
                    grand_total=quote_profile.grand_total
                )
            )

            status, temp_quote_profile = utils.call_service_or_500(
                TempClientQuoteProfileCRUD.update,
                existing_temp_quote_profile,
                new_temp_quote_profile,
                session
            )

    # Get color theme and page colors
    color_theme = session.get(AppSetting, "0001").setting_value
    colors = utils.get_colors(color_theme)

    return templates.TemplateResponse(
        request=request,
        name="quotes.html",
        context={
            "all_quotes_dict": all_quotes_dict,
            "page_quotes": page_quotes,
            "page_quotes_dict": page_quotes_dict,
            "clients": all_clients,
            "all_services_dict": all_services_dict,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "theme": session.get(AppSetting, "0000").setting_value,
            "colorTheme": color_theme,
            **colors
        }
    )

@router.post("/get_temp_client_quote_profile")
async def get_temp_client_quote_profile(
    request: Request,
    session: SessionDependency
) -> JSONResponse:
    # Extract the client id from the request body
    data = await request.json()
    client_id = data.get("client_id")
    
    # Get the temp client quote profile from the database
    get_status, temp_quote_profile = utils.call_service_or_404(
        TempClientQuoteProfileCRUD.get,
        client_id,
        session
    )

    return JSONResponse(
        content={
            "detail": get_status,
            "temp_quote_profile": {
                "client_id": temp_quote_profile.client_id,
                "min_monthly_charge": str(temp_quote_profile.min_monthly_charge),
                "premium_salt_upcharge": str(temp_quote_profile.premium_salt_upcharge),
                "services": temp_quote_profile.services,
                "grand_total": str(temp_quote_profile.grand_total)
            },
        },
        status_code=200,
    )

@router.post("/save_temp_client_quote_profile")
async def save_temp_client_quote_profile(
    request: Request,
    session: SessionDependency
):
    # Extract the data from the request body
    data = await request.json()
    client_id = data.get("client_id")
    min_monthly_charge = data.get("min_monthly_charge")
    premium_salt_upcharge = data.get("premium_salt_upcharge")
    services = data.get("services")
    grand_total = data.get("grand_total")

    # Validate the new client quote profile data
    _, new_temp_client_quote_profile = utils.call_service_or_422(
        TempClientQuoteProfileCRUD.validate_data,
        TempClientQuoteProfile(
            client_id=client_id,
            min_monthly_charge=min_monthly_charge,
            premium_salt_upcharge=premium_salt_upcharge,
            services=services,
            grand_total=grand_total
        )
    )

    # Check if client quote profile already exists
    existing_temp_client_quote_profile = session.get(
        TempClientQuoteProfile,
        client_id
    )

    if existing_temp_client_quote_profile:
        # Update the existing client quote profile's attributes with the new
        # client quote profile's data
        status, temp_client_quote_profile = utils.call_service_or_500(
            TempClientQuoteProfileCRUD.update,
            existing_temp_client_quote_profile,
            new_temp_client_quote_profile,
            session
        )
    else:
        # Create a new client quote profile in the database
        status, temp_client_quote_profile = utils.call_service_or_500(
            TempClientQuoteProfileCRUD.create,
            new_temp_client_quote_profile,
            session
        )

    return JSONResponse(
        content={
            "detail": status,
            "client_id": temp_client_quote_profile.client_id,
            "temp_quote_profile": {
                "client_id": temp_client_quote_profile.client_id,
                "min_monthly_charge": str(
                    temp_client_quote_profile.min_monthly_charge
                ),
                "premium_salt_upcharge": str(
                    temp_client_quote_profile.premium_salt_upcharge
                ),
                "services": temp_client_quote_profile.services,
                "grand_total": str(temp_client_quote_profile.grand_total)
            },
        },
        status_code=200,
    )

@router.post("/batch_send_quotes")
async def send_quotes(
    request: Request,
    session: SessionDependency
):
    # Extract the data from the request body
    data = await request.json()
    client_ids = data.get("client_ids")

    for client_id in client_ids:
        # Get the client from the database
        client = session.get(Client, client_id)
        # Get the client's temp quote profile from the database
        temp_quote_profile = session.get(TempClientQuoteProfile, client_id)

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
            min_monthly_charge=temp_quote_profile.min_monthly_charge,
            premium_salt_upcharge=temp_quote_profile.premium_salt_upcharge,
            services=temp_quote_profile.services,
            grand_total=temp_quote_profile.grand_total
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

    return JSONResponse(
        content={
            "detail": "Quotes sent successfully.",
            "redirect_to": "/quotes?page=1"
        },
        status_code=200,
    )

@router.get("/download_quote")
def download_quote(
    session: SessionDependency,
    client_id: int=Query(...),
    quote_id: int=Query(...,)
) -> RedirectResponse:
    """
    Download a previously generated and sent quote to the user's Downloads folder.

    Parameters:
    - session: SessionDependency - A SQLModel session dependency for database access.
    - client_id: int - The unique ID of the client.
    - quote_id: int - The unique ID of the quote.

    Returns:
    - RedirectResponse: If successful, a redirect response to the quotes and invoices page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 404 (NOT FOUND) if client or quote cannot be found in the database
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Get the user's download directory (windows)
    download_dir = Path.home() / "Downloads"
    
    # Get the client from the database
    client = utils.call_service_or_404(ClientCRUD.get, client_id, session)
    # Get the existing quote from the database
    existing_quote = utils.call_service_or_404(QuoteCRUD.get, quote_id, session)

    # Create and save the PDF
    pdf_status = utils.call_service_or_500(
        PDFServices.save_pdf,
        file_type="quote",
        client=client,
        invoice_no=None,
        quote_no=existing_quote.quote_no,
        html_source=existing_quote.pdf_html,
        pdf_save_path=download_dir
    )

    return RedirectResponse(url="/quotes_and_invoices/", status_code=303)

@router.post("/send_quotes")
async def send_quotes(
    request: Request,
    session: SessionDependency
):
    """
    Send quotes as a PDFs to a list of clients via their email.

    Parameters:
    - request: Request - The incoming HTTP request.
    - session: SessionDependency - A SQLModel session dependency for database access.

    Returns:
    - RedirectResponse: If successful, a redirect response to the clients page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Extract the list of client ids from the form
    form = await request.form()
    client_ids = form.get("client-ids").split(";")

    for client_id in client_ids:
        services_count = int(form.get(f"services-count_client-{client_id}"))
        services = []
        grand_total = 0

        # Extract the list of services for each client from the form
        for i in range(services_count):
            services.append({
                "service_id": form.get(f"service-{i}_client-{client_id}"),
                "service_name": form.get(f"service-name-{i}_client-{client_id}"),
                "quantity": form.get(f"quantity-{i}_client-{client_id}"),
                "per_unit": form.get(f"per-unit-{i}_client-{client_id}"),
                "unit_price": form.get(f"unit-price-{i}_client-{client_id}"),
                "total_price": form.get(f"total-price-{i}_client-{client_id}")
            })
            grand_total += Decimal(form.get(f"total-price-{i}_client-{client_id}"))

        # Get the client from the database
        client = session.get(Client, client_id)

        # Get the number of quotes existing for the client and generate a
        # quote number for the quote based on that value and the client's unique id
        num_quotes = utils.call_service_or_500(
            QuoteCRUD.count_by_client_id,
            client_id,
            session
        )
        quote_no = f"{client_id}-{str(num_quotes + 1).zfill(4)}"

        # Get the path to save quote PDFs to from app settings
        pdf_save_path = utils.call_service_or_404(
            AppSettingCRUD.get_by_setting_name,
            "quote-save-pdfs-to-path",
            session
        )

        # Generate HTML source for the quote pdf
        html_source = utils.call_service_or_500(
            PDFServices.generate_html_source,
            file_type="quote",
            client=client,
            invoice_no=None,
            quote_no=quote_no,
            services=services,
            grand_total=grand_total
        )

        # Save the PDF
        pdf_status = utils.call_service_or_500(
            PDFServices.save_pdf,
            file_type="quote",
            client=client,
            invoice_no=None,
            quote_no=quote_no,
            html_source=html_source,
            pdf_save_path=pdf_save_path,
        )

        # Send the email
        email_status = await utils.call_async_service_or_500(
            EmailServices.send_email,
            subject="M&M Quote Request",
            recipients=[client.email],
            body=textwrap.dedent(f"""\
                Dear {client.name},

                M&M Concrete Designs is a fully insured and licensed contractor based.
            """),
            subtype="plain",
            attachments=[
                {
                    "file": f'{pdf_save_path}/m&m-quote_{client.name.replace(" ", "_")}_{quote_no}.pdf',
                    "mime_type": "application/pdf",
                }
            ]
        )

        # Validate the new quote data
        new_quote = utils.call_service_or_422(
            QuoteCRUD.validate_data,
            Quote(
                client_id=client_id,
                quote_no=quote_no,
                pdf_html=html_source,
            )
        )

        # Create the new quote in the database
        create_status = utils.call_service_or_500(QuoteCRUD.create, new_quote, session)

    return RedirectResponse(url="/quotes_and_invoices/", status_code=303)
