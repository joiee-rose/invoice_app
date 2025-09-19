from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from heroicons.jinja import heroicon_outline, heroicon_solid
from sqlmodel import Session, select

import utils
from database import get_session
from models import Client, Service, Quote, AppSetting

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

    all_services = session.exec(select(Service)).all()
    all_services_dict = jsonable_encoder(all_services)

    return templates.TemplateResponse(
        request=request,
        name="quotes.html",
        context={
            "all_quotes_dict": all_quotes_dict,
            "page_quotes": page_quotes,
            "page_quotes_dict": page_quotes_dict,
            "clients": session.exec(select(Client)).all(),
            "all_services_dict": all_services_dict,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "theme": session.get(AppSetting, "0000").setting_value,
            "colorTheme": session.get(AppSetting, "0001").setting_value
        }
    )

@router.post("/batch_send_quotes")
async def send_quotes(
    request: Request,
    session: SessionDependency
):
    pass

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
