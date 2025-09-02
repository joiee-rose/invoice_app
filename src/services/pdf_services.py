import io
from decimal import Decimal
from typing import List, Dict, Any
from datetime import datetime

from xhtml2pdf import pisa

from models import Client

class PDFServices:
    @staticmethod
    def generate_html_source(
        file_type: str,
        client: Client,
        invoice_no: str | None,
        quote_no: str | None,
        services: List[Dict[str, Any]],
        grand_total: Decimal
    ) -> tuple[bool, str, str | None]:
        """
        Generates the HTML source used by xhtml2pdf to render the quote or
        invoice PDF.

        Parameters:
        - file_type: str - The type of the file being generated (e.g., "invoice" or "quote").
        - client: Client - The client for whom the invoice or quote is being generated.
        - invoice_no: str | None - The invoice number (if applicable).
        - quote_no: str | None - The quote number (if applicable).
        - services: List[Dict[str, Any]] - A list of services included in the invoice or quote.
        - grand_total: Decimal - The grand total amount for the invoice or quote.

        Returns:
        - tuple[bool, str]:
            - bool - A success flag (true or false)
            - str - The generated HTML source as a string (if bool is true), or an error message (if bool is false).
        """
        try:
            table_body_rows = ""
            for service in services:
                table_body_rows += f"""
                    <tr style="height:24px; padding-top:5px; font-size:12px; border:1px solid #000">
                        <td style="padding-left:4px; text-align:left;">{service.get("service_name", "")}</td>            
                        <td style="text-align:center;">{service.get("quantity", "")}</td>
                        <td style="text-align:center;">{service.get("per_unit", "")}</td>
                        <td style="text-align:center;">{service.get("unit_price", "")}</td>
                        <td style="text-align:center;">{service.get("tax", "")}</td>
                        <td style="text-align:center;">{service.get("total_price", "")}</td>
                    </tr>
                """

            html_source = f"""
                <html>
                    <body style="font-family:Helvetica;">
                        <!-- Header -->
                        <table width="100%" style="border:none; margin-bottom:64px;">
                            <tr>
                                <td style="text-align:left;">
                                    <h1 style="font-size: 16px;">{file_type.upper()}</h1>
                                </td>
                                <td style="text-align:right;">
                                    <img src="./static/images/m-and-m-concrete-designs-logo-250w.png" alt="M & M Concrete Designs Logo" style="width:175px; height:auto;">
                                </td>
                            </tr>
                        </table>

                        <!-- Client Information & Invoice Information -->
                        <table width="100%" style="border:none; margin-bottom:24px;">
                            <tr>
                                <td style="text-align:left; font-size:12px;">{client.name}</td>
                                {f'<td style="text-align:right; font-size:12px;">Invoice No.: {invoice_no}</td>' if file_type == "invoice" else f'<td style="text-align:right; font-size:12px;">Quote No.: {quote_no}</td>'}
                            </tr>
                            <tr>
                                <td style="text-align:left; font-size:12px;">{client.business_name}</td>
                                <td style="text-align:right; font-size:12px;">Issue Date: {datetime.now().strftime("%m/%d/%Y")}</td>
                            </tr>
                            <tr><td style="font-size:12px;">{client.street_address}</td></tr>
                            <tr><td style="font-size:12px;">{client.city + ", " + client.state + " " + client.zip_code}</td></tr>
                        </table>

                        <!-- Services Table -->
                        <table width="100%" style="border-collapse:collapse;">
                            <thead>
                                <tr style="height:24px; padding-top:4px; font-size:14px; background-color:#d4d4d8; border:1px solid #000;">
                                    <th width="30%" style="text-align:center;">SERVICE</th>
                                    <th width="10%" style="text-align:center;">QUANTITY</th>
                                    <th width="10%" style="text-align:center;">PER UNIT</th>
                                    <th width="19%" style="text-align:center;">UNIT PRICE (USD)</th>
                                    <th width="12%" style="text-align:center;">TAX (%)</th>
                                    <th width="19%" style="text-align:center;">TOTAL PRICE (USD)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {table_body_rows}
                                <!-- Grand Total Row -->
                                <tr style="border:none;">
                                    <td style="border:none;"></td>
                                    <td style="border:none;"></td>
                                    <td style="border:none;"></td>
                                    <td colspan="2" style="height:24px; padding-top:6px; text-align:center; font-size:14px; font-weight:bold; border:1px solid #000;">Total (USD)</td>
                                    <td style="height:24px; padding-top:5px; text-align:center; font-size:12px; border:1px solid #000;">{grand_total}</td>
                                </tr>
                            </tbody>
                        </table>
                    </body>
                </html>
            """
        except Exception as e:
            # TODO - log error
            return False, str(e), None

        return True, "HTML source generated successfully.", html_source

    @staticmethod
    def save_pdf(
        file_type: str,
        client: Client,
        invoice_no: str | None,
        quote_no: str | None,
        html_source: str,
        pdf_save_path: str,
    ) -> tuple[bool, str, str | None]:
        """
        Creates a PDF from a generated HTML source and saves 
        the generated PDF to the specified path.

        Parameters:
        - file_type: str - The type of the file being generated (e.g., "invoice" or "quote").
        - client: Client - The client for whom the invoice or quote is being generated.
        - invoice_no: str | None - The invoice number (if applicable).
        - quote_no: str | None - The quote number (if applicable).
        - html_source: str - The HTML source to be converted to PDF.
        - pdf_save_path: str - The path where the generated PDF should be saved.

        Returns:
        - tuple[bool, str]:
            - bool - A success flag (true or false)
            - str - A success message (if bool is true), or an error message (if bool is false).
        """
        if file_type == "invoice":
            # ex: m&m-invoice_Joie-Rose_Stangle_1-0001
            filename = f'm&m-invoice_{client.name.replace(" ", "_")}_{invoice_no}'
        else:
            # ex: m&m-quote_Joie-Rose_Stangle_1-0001
            filename = f'm&m-quote_{client.name.replace(" ", "_")}_{quote_no}'

        with open(f"{pdf_save_path}/{filename}.pdf", "w+b") as result_file:
            pisa_status = pisa.pisaDocument(
                src=html_source,
                dest=result_file,
                log_warn=True
            )
        
            if pisa_status.err:
                # TODO - log error
                return False, "Failed to generate PDF.", None
            return True, "PDF generated successfully.", f"{pdf_save_path}/{filename}.pdf"