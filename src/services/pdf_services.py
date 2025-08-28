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
        services: List[Dict[str, Any]],
        grand_total: Decimal
    ) -> tuple[bool, str]:
        try:
            table_body_rows = ""
            for service in services:
                table_body_rows += f"""
                    <tr style="height:24px; padding-top:5px; font-size:12px; border:1px solid #000">
                        <td style="padding-left:4px; text-align:left;">{service.get("service_name", "")}</td>            
                        <td style="text-align:center;">{service.get("quantity", "")}</td>
                        <td style="text-align:center;">{service.get("per_unit", "")}</td>
                        <td style="text-align:center;">{service.get("unit_price", "")}</td>
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
                                {f"""<td style="text-align:right; font-size:12px;">Invoice No.: {invoice_no}</td>""" if file_type == "invoice" else "<td></td>"}
                            </tr>
                            <tr>
                                <td style="text-align:left; font-size:12px;">{client.business_name}</td>
                                {f"""<td style="text-align:right; font-size:12px;">Issue Date: {datetime.now().strftime("%m/%d/%Y")}</td>""" if file_type == "invoice" else "<td></td>"}
                            </tr>
                            <tr><td style="font-size:12px;">{client.street_address}</td></tr>
                            <tr><td style="font-size:12px;">{client.city + ", " + client.state + " " + client.zip_code}</td></tr>
                        </table>

                        <!-- Services Table -->
                        <table width="100%" style="border-collapse:collapse;">
                            <thead>
                                <tr style="height:24px; padding-top:4px; font-size:14px; background-color:#d4d4d8; border:1px solid #000;">
                                    <th width="40%" style="text-align:center;">DESCRIPTION</th>
                                    <th width="10%" style="text-align:center;">QUANTITY</th>
                                    <th width="10%" style="text-align:center;">PER UNIT</th>
                                    <th width="20%" style="text-align:center;">UNIT PRICE (USD)</th>
                                    <th width="20%" style="text-align:center;">TOTAL PRICE (USD)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {table_body_rows}
                                <!-- Grand Total Row -->
                                <tr style="border:none;">
                                    <td style="border:none;"></td>
                                    <td style="border:none;"></td>
                                    <td style="border:none;"></td>
                                    <td style="height:24px; padding-top:5px; text-align:center; font-size:14px; font-weight:bold; border:1px solid #000;">Total (USD)</td>
                                    <td style="height:24px; padding-top:5px; text-align:center; font-size:12px; border:1px solid #000;">{grand_total}</td>
                                </tr>
                            </tbody>
                        </table>
                    </body>
                </html>
            """
        except Exception as e:
            # TODO - log error
            return False, str(e)

        return True, html_source

    @staticmethod
    def save_pdf(
        html_source: str,
        pdf_save_path: str,
        file_type: str,
        invoice_no: str | None,
        client_name: str | None
    ) -> tuple[bool, str]:
        filename = f"invoice_{invoice_no}" if file_type == "invoice" else f"quote_{client_name.replace(" ", "_")}"

        with open(f"{pdf_save_path}/{filename}.pdf", "w+b") as result_file:
            pisa_status = pisa.pisaDocument(src=html_source, dest=result_file, log_warn=True)
        
            if pisa_status.err:
                # TODO - log error
                return False, "Failed to generate PDF."
            
            return True, "PDF generated successfully."