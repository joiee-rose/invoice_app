import textwrap
from typing import Annotated, List, Dict, Any
from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from heroicons.jinja import heroicon_micro, heroicon_mini, heroicon_outline, heroicon_solid
from sqlmodel import Session, select
from xhtml2pdf import pisa

import utils
from database import get_session
from models import Client, Invoice, AppSetting
from services import PDFServices, EmailServices

# Create router for client-related endpoints
router = APIRouter(prefix="/invoices", tags=["invoices"])

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
def render_invoices_page(
    request: Request,
    session: SessionDependency
) -> HTMLResponse:
    """
    Renders the invoices page.

    Parameteres:
    - request: Request - The incoming HTTP request object.
    - session: SessionDependency - A SQLModel session dependency for database access.

    Returns:
    - HTMLResponse: If successful, the HTML content of the invoices page in the body of the response, with HTTP status code 200 (OK).
    """
    theme = session.get(AppSetting, "0000").setting_value
    colorTheme = session.get(AppSetting, "0001").setting_value
    return templates.TemplateResponse(
        request=request,
        name="invoices.html",
        context={"theme": theme, "colorTheme": colorTheme}
    )

@router.post("/send_invoice")
async def send_invoice(
    request: Request,
    session: SessionDependency,
    client_id: int = Form(..., alias="client-id"),
    services_count: int = Form(..., alias="services-count")
):
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
    # Get the last used id in the invoice table
    last_invoice = session.exec(select(Invoice).order_by(Invoice.id.desc())).first()
    new_invoice_id = last_invoice.id + 1 if last_invoice else 1

    # Generate HTML source for the quote pdf
    html_source = utils.call_service_or_500(
        PDFServices.generate_html_source,
        file_type="invoice",
        client=client,
        invoice_no=str(new_invoice_id).zfill(4),
        services=services,
        grand_total=grand_total
    )
    # Save the PDF
    pdf_status = utils.call_service_or_500(
        PDFServices.save_pdf,
        html_source=html_source,
        pdf_save_path=pdf_save_path,
        file_type="invoice",
        invoice_no=str(new_invoice_id).zfill(4),
        client_name=client.name
    )
    # Send the email
    email_status = await utils.call_async_service_or_500(
        EmailServices.send_email,
        subject="Quote Request",
        recipients=[client.email],
        body=textwrap.dedent(f"""\
            Dear {client.name},

            Please find attached invoice {str(new_invoice_id).zfill(4)} for ________ services provided by ________.
        """),
        subtype="plain",
        attachments=[
            {
                "file": f"{pdf_save_path}/invoice_{str(new_invoice_id).zfill(4)}.pdf",
                "mime_type": "application/pdf",
            }
        ]
    )

    # TODO - insert record into database
 
    return RedirectResponse(url="/clients/", status_code=303)