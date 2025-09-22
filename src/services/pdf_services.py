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
        min_monthly_charge: Decimal,
        premium_salt_upcharge: Decimal,
        services: List[Dict[str, Any]],
        grand_total: Decimal,
    ) -> tuple[bool, str, str | None]:
        """
        Generates the HTML used by xhtml2pdf to render the quote or invoice PDF.

        Parameters:
        - file_type: The type of the file being generated (e.g., "invoice" or "quote").
        - client: The client for whom the invoice or quote is being generated.
        - invoice_no: The invoice number (if applicable).
        - quote_no: The quote number (if applicable).
        - services: A list of services included in the invoice or quote.
        - grand_total: The grand total amount for the invoice or quote.
        - min_monthly_charge: The minimum monthly charge for the quote.
        - include_service_disclosure: Whether to include service disclosure in the quote.

        Returns:
        - tuple[bool, str]:
            - bool - A success flag (true or false)
            - str - The generated HTML source as a string (if bool is true), or an error message (if bool is false).
        """
        try:
            # Generate the services table from the services list
            table_body_rows = ""
            for service in services:
                table_body_rows += f"""
                    <tr style="height:24px; padding-top:5px; font-size:12px; border:1px solid #000">
                        <td style="padding-left:4px; text-align:left;">{service.get("service_name", "")}</td>            
                        <td style="text-align:center;">{service.get("quantity", "")}</td>
                        <td style="text-align:center;">{service.get("per_unit", "")}</td>
                        <td style="text-align:center;">{Decimal(service.get("unit_price", "")).quantize(Decimal("0.00"))}</td>
                        <td style="text-align:center;">{Decimal(service.get("tax", "")).quantize(Decimal("0.00"))}</td>
                        <td style="text-align:center;">{Decimal(service.get("total_price", "")).quantize(Decimal("0.00"))}</td>
                    </tr>
                """

            # Client Information
            client_info = ""
            if (client.name == client.business_name):
                client_info = f"""
                    <table width="100%" style="border:none; margin-bottom:24px;">
                        <tr>
                            <td style="text-align:left; font-size:12px;">{client.name}</td>
                            {f'<td style="text-align:right; font-size:12px;">Invoice No.: {invoice_no}</td>' if file_type == "invoice" else f'<td style="text-align:right; font-size:12px;">Quote No.: {quote_no}</td>'}
                        </tr>
                        <tr>
                            <td style="text-align:left; font-size:12px;">{client.street_address}</td>
                            <td style="text-align:right; font-size:12px;">Issue Date: {datetime.now().strftime("%m/%d/%Y")}</td>
                        </tr>
                        <tr><td style="font-size:12px;">{client.city + ", " + client.state + " " + client.zip_code}</td></tr>
                    </table>
                """
            else:
                client_info = f"""
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
                """

            # Service Disclosure
            service_disclosure = ""
            if (file_type == "quote"):
                service_disclosure = f"""
                    <div style="font-size:12px;">
                        <h2 style="font-size:14px;">Service Disclosure</h2>
                        <p>2" Trigger (with a tolerance of 0.5")</p>
                        <ul>
                            <li>Snow accumulations less than the threshold will receive the deice services. In the event of sleet, ice, or wet roads with freezing temperatures, we will provide deice services.</li>
                        </ul>
                        <p>Over the 2" Trigger</p>
                        <ul>
                            <li>We will plow and shovel, then provide deice services.</li>
                            <li>Black top surfaces will receive rock salt.</li>
                                <ul>
                                    <li>
                                        For temperatures below 17 degrees, black top surfaces will receive premium salt, as rock salt rapidly loses effectiveness every degree below 17 degrees. Premium salt will reduce the number of visits needed, therefore saving you money in the long run.
                                        The upcharge cost for when the premium salt is used will be ${Decimal(premium_salt_upcharge).quantize(Decimal("0.00"))}.
                                    </li>
                                </ul>
                            <li>Concrete surfaces will receive calcium chloride.</li>
                        </ul>
                        <div style="font-size:12px;">
                            <p>Service period is from 11/1/2025 to 3/31/2026.</p>
                        </div>
                        <div style="font-size:12px;">
                            <p>There will be a minimum monthly charge of ${Decimal(min_monthly_charge).quantize(Decimal("0.00"))} if this price is not exceeded by normal services. This minimum covers our costs in a period where we do not need to provide any services, but we still have trucks equipped and ready to go, salt piles and supplies stocked, and employees on call.</p>
                        </div>
                    </div>
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
                        {client_info}

                        <!-- Services Table -->
                        <table width="100%" style="border-collapse:collapse; margin-bottom:24px;">
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

                        <!-- Service Disclosure -->
                        {service_disclosure}
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