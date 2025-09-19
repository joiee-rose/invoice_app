from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from heroicons.jinja import heroicon_outline, heroicon_solid
from sqlmodel import Session, select

import utils
from database import get_session
from models import Client, Invoice, AppSetting

# Create router for invoice-related endpoints
router = APIRouter(prefix="/invoices", tags=["invoices"])

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
def render_invoices_page(
    request: Request,
    session: SessionDependency,
    page: int = 1
) -> HTMLResponse:
    # Determine the number of invocies to show per page based on screen height
    per_page = utils.get_per_page("invoices")

    # Slice the list of all invocies based on the number of invocies per page
    all_invoices = session.exec(select(Invoice)).all()
    total = len(all_invoices)
    start = (page - 1) * per_page
    end = start + per_page
    page_invoices = all_invoices[start:end]
    # Count the number of pages necessary to show all the invocies
    total_pages = (total + per_page - 1) // per_page

    # Convert invoices lists to JSON serializable format for use in javascript
    all_invoices_dict = jsonable_encoder(all_invoices)
    page_invoices_dict = jsonable_encoder(page_invoices)

    return templates.TemplateResponse(
        request=request,
        name="invoices.html",
        context={
            "all_invoices_dict": all_invoices_dict,
            "page_invoices": page_invoices,
            "page_invoices_dict": page_invoices_dict,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "theme": session.get(AppSetting, "0000").setting_value,
            "colorTheme": session.get(AppSetting, "0001").setting_value
        }
    )

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

@router.post("/send_invoices")
async def send_invoices(
    request: Request,
    session: SessionDependency
):
    """
    Send invoices as a PDFs to a list of clients via their email.

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
            AppSettingCRUD.get_by_setting_name,
            "invoice-save-pdfs-to-path",
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
            PDFServices.save_pdf,
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
                    "file": f'{pdf_save_path}/m&m-invoice_{client.name.replace(" ", "_")}_{invoice_no}.pdf',
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