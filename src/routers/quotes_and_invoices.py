import os
import textwrap
from pathlib import Path
from typing import Annotated
from decimal import Decimal

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from heroicons.jinja import heroicon_micro, heroicon_mini, heroicon_outline, heroicon_solid
from sqlmodel import Session, select

import utils
from database import get_session
from models import Client, Quote, Invoice, AppSetting
from services import ClientCRUD, QuoteCRUD, InvoiceCRUD, AppSettingCRUD, PDFServices, EmailServices

# Create router for client-related endpoints
router = APIRouter(prefix="/quotes_and_invoices", tags=["quotes_and_invoices"])

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
def render_quotes_and_invoices_page(
    request: Request,
    session: SessionDependency
) -> HTMLResponse:
    """
    Renders the quotes and invoices page.

    Parameteres:
    - request: Request - The incoming HTTP request object.
    - session: SessionDependency - A SQLModel session dependency for database access.

    Returns:
    - HTMLResponse: If successful, the HTML content of the invoices page in the body of the response, with HTTP status code 200 (OK).
    """
    all_clients = session.exec(select(Client)).all()
    all_quotes = session.exec(select(Quote)).all()
    all_invoices = session.exec(select(Invoice)).all()  
    theme = session.get(AppSetting, "0000").setting_value
    colorTheme = session.get(AppSetting, "0001").setting_value
    return templates.TemplateResponse(
        request=request,
        name="quotes_and_invoices.html",
        context={"clients": all_clients, "quotes": all_quotes, "invoices": all_invoices, "theme": theme, "colorTheme": colorTheme}
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

@router.get("/download_invoice")
def download_invoice(
    session: SessionDependency,
    client_id: int=Query(...),
    invoice_id: int=Query(...,)
) -> RedirectResponse:
    """
    Download a previously generated and sent invoice to the user's Downloads folder.

    Parameters:
    - session: SessionDependency - A SQLModel session dependency for database access.
    - client_id: int - The unique ID of the client.
    - invoice_id: int - The unique ID of the invoice.

    Returns:
    - RedirectResponse: If successful, a redirect response to the quotes and invoices page with HTTP status code 303 (SEE OTHER).

    Raises:
    - HTTPException:
        - 404 (NOT FOUND) if client or invoice cannot be found in the database
        - 500 (INTERNAL SERVER ERROR) for unexpected errors
    """
    # Get the user's download directory (windows)
    download_dir = Path.home() / "Downloads"
    
    # Get the client from the database
    client = utils.call_service_or_404(ClientCRUD.get, client_id, session)
    # Get the existing invoice from the database
    existing_invoice = utils.call_service_or_404(InvoiceCRUD.get, invoice_id, session)

    # Create and save the PDF
    pdf_status = utils.call_service_or_500(
        PDFServices.save_pdf,
        file_type="invoice",
        client=client,
        invoice_no=existing_invoice.invoice_no,
        quote_no=None,
        html_source=existing_invoice.pdf_html,
        pdf_save_path=download_dir
    )

    return RedirectResponse(url="/quotes_and_invoices/", status_code=303)

@router.post("/send_invoice")
async def send_invoice(
    request: Request,
    session: SessionDependency,
    client_id: int = Form(..., alias="client-id"),
    services_count: int = Form(..., alias="services-count")
):
    """
    Send an invoice as a PDF to the client via email.

    Parameters:
    - request: Request - The incoming HTTP request.
    - session: SessionDependency - A SQLModel session dependency for database access.
    - client_id: int - The unique ID of the client.
    - services_count: int - The number of services in the invoice.

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
    # Get the number of invoices existing for the client & generate an invoice
    # number for the invoice based on that value and the client's unique id
    num_invoices = utils.call_service_or_500(
        InvoiceCRUD.count_by_client_id,
        client_id,
        session
    )
    invoice_no = f"{client_id}-{str(num_invoices + 1).zfill(4)}"
    # Get the path to save invoice PDFs to from app settings
    pdf_save_path = utils.call_service_or_404(
        AppSettingCRUD.get,
        "3000",
        session
    )

    # Generate HTML source for the invoice pdf
    html_source = utils.call_service_or_500(
        PDFServices.generate_html_source,
        file_type="invoice",
        client=client,
        invoice_no=invoice_no,
        quote_no=None,
        services=services,
        grand_total=grand_total
    )
    # Save the PDF
    pdf_status = utils.call_service_or_500(
        file_type="invoice",
        client=client,
        invoice_no=invoice_no,
        quote_no=None,
        html_source=html_source,
        pdf_save_path=pdf_save_path,
    )

    # Send the email
    email_status = await utils.call_async_service_or_500(
        EmailServices.send_email,
        subject=f"M&M Invoice {invoice_no}",
        recipients=[client.email],
        body=textwrap.dedent(f"""\
            Dear {client.name},

            (some text about the invoice)
        """),
        subtype="plain",
        attachments=[
            {
                "file": f"{pdf_save_path}/m&m-invoice_{client.name.replace(" ", "_")}_{invoice_no}.pdf",
                "mime_type": "application/pdf",
            }
        ]
    )

    # Validate the new invoice data
    new_invoice = utils.call_service_or_422(
        InvoiceCRUD.validate_data,
        Invoice(
            client_id=client_id,
            invoice_no=invoice_no,
            pdf_html=html_source
        )
    )

    # Create the new invoice in the database
    create_status = utils.call_service_or_500(InvoiceCRUD.create, new_invoice, session)

    return RedirectResponse(url="/quotes_and_invoices/", status_code=303)