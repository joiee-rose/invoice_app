from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, select
from sqlalchemy import func

from database import get_session
from models import Client, Service, ClientQuoteProfile, Quote, Invoice, AppSetting

SessionDependency = Annotated[Session, Depends(get_session)]

class ClientCRUD:
    @staticmethod
    def validate_data(data: Client) -> tuple[bool, str]:
        try:
            Client.model_validate(data)
            return True, data
        except Exception as e:
            return False, str(e)
        
    @staticmethod
    def create(data: Client, session: Session) -> tuple[bool, str]:
        is_valid, message = ClientCRUD.validate_data(data)
        if not is_valid:
            return False, message
        
        session.add(data)
        session.commit()
        return True, "Client created successfully."
    
    @staticmethod
    def get(id: int, session: Session) -> tuple[bool, Client | str]:
        client = session.get(Client, id)
        return (False, "Client not found.") if not client else (True, client)

    @staticmethod
    def update(client: Client, data: Client, session: Session) -> tuple[bool, str]:
        client.name = data.name
        client.business_name = data.business_name
        client.street_address = data.street_address
        client.city = data.city
        client.state = data.state
        client.zip_code = data.zip_code
        client.email = data.email
        client.phone = data.phone

        session.add(client)
        session.commit()
        return True, "Client updated successfully."

    @staticmethod
    def delete(id: int, session: Session) -> tuple[bool, str]:
        client = session.get(Client, id)
        if not client:
            return False, "Client not found."

        session.delete(client)
        session.commit()
        return True, "Client deleted successfully."

class ServiceCRUD:
    @staticmethod
    def validate_data(
        data: Service
    ) -> tuple[bool, str, Service | None]:
        try:
            Service.model_validate(data)
            return True, "Validated fields.", data
        except Exception as e:
            return False, str(e), None
        
    @staticmethod
    def create(
        data: Service,
        session: Session
    ) -> tuple[bool, str, Service | None]:
        is_valid, message, service = ServiceCRUD.validate_data(data)
        if not is_valid:
            return False, message, None
        
        session.add(data)
        session.commit()
        session.refresh(data)

        return True, "Service created successfully.", service
    
    @staticmethod
    def get(
        id: int,
        session: Session
    ) -> tuple[bool, str, Service | None]:
        service = session.get(Service, id)
        if not service:
            return False, "Service not found.", None
        return True, "Service found.", service

    @staticmethod
    def update(
        service: Service,
        data: Service,
        session: Session
    ) -> tuple[bool, str, Service | None]:
        try:
            service.name = data.name
            service.description = data.description
            service.unit_price = data.unit_price

            session.add(service)
            session.commit()
            session.refresh(service)

            return True, "Service updated successfully.", service
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def delete(id: int, session: Session) -> tuple[bool, str, Service | None]:
        service = session.get(Service, id)
        if not service:
            return False, "Service not found.", None

        session.delete(service)
        session.commit()

        return True, "Service deleted successfully.", service

class ClientQuoteProfileCRUD:
    @staticmethod
    def validate_data(data: ClientQuoteProfile) -> tuple[bool, str]:
        try:
            ClientQuoteProfile.model_validate(data)
            return True, data
        except Exception as e:
            return False, str(e)
        
    @staticmethod
    def create(data: ClientQuoteProfile, session: Session) -> tuple[bool, str]:
        is_valid, message = ClientQuoteProfileCRUD.validate_data(data)
        if not is_valid:
            return False, message
        
        session.add(data)
        session.commit()
        return True, "ClientQuoteProfile created successfully."
    
    @staticmethod
    def get(id: int, session: Session) -> tuple[bool, ClientQuoteProfile | str]:
        client_quote_profile = session.get(ClientQuoteProfile, id)
        return (False, "ClientQuoteProfile not found.") if not client_quote_profile else (True, client_quote_profile)

    @staticmethod
    def update(client_quote_profile: ClientQuoteProfile, data: ClientQuoteProfile, session: Session) -> tuple[bool, str]:
        client_quote_profile.services = data.services
        client_quote_profile.grand_total = data.grand_total

        session.add(client_quote_profile)
        session.commit()
        return True, "ClientQuoteProfile updated successfully."

    @staticmethod
    def delete(id: int, session: Session) -> tuple[bool, str]:
        client_quote_profile = session.get(ClientQuoteProfile, id)
        if not client_quote_profile:
            return False, "ClientQuoteProfile not found."

        session.delete(client_quote_profile)
        session.commit()
        return True, "ClientQuoteProfile deleted successfully."

class QuoteCRUD:
    @staticmethod
    def validate_data(data: Quote) -> tuple[bool, str]:
        try:
            Quote.model_validate(data)
            return True, data
        except Exception as e:
            return False, str(e)
        
    @staticmethod
    def create(data: Quote, session: Session) -> tuple[bool, str]:
        is_valid, message = QuoteCRUD.validate_data(data)
        if not is_valid:
            return False, message
        
        session.add(data)
        session.commit()
        return True, "Quote created successfully."
    
    @staticmethod
    def get(id: int, session: Session) -> tuple[bool, Quote | str]:
        quote = session.get(Quote, id)
        return (False, "Quote not found.") if not quote else (True, quote)

    @staticmethod
    def update(quote: Quote, data: Quote, session: Session) -> tuple[bool, str]:
        quote.quote_no = data.quote_no
        quote.issue_date = data.issue_date
        quote.pdf_html = data.pdf_html

        session.add(quote)
        session.commit()
        return True, "Quote updated successfully."

    @staticmethod
    def delete(id: int, session: Session) -> tuple[bool, str]:
        quote = session.get(Quote, id)
        if not quote:
            return False, "Quote not found."

        session.delete(quote)
        session.commit()
        return True, "Quote deleted successfully." 

    @staticmethod
    def count_by_client_id(client_id: int, session: Session) -> int:
        try:
            statement = select(func.count()).select_from(Quote).where(Quote.client_id == client_id)
            return True, session.exec(statement).one()
        except Exception as e:
            return False, str(e)

class InvoiceCRUD:
    @staticmethod
    def validate_data(data: Invoice) -> tuple[bool, str]:
        try:
            Invoice.model_validate(data)
            return True, data
        except Exception as e:
            return False, str(e)
        
    @staticmethod
    def create(data: Invoice, session: Session) -> tuple[bool, str]:
        is_valid, message = InvoiceCRUD.validate_data(data)
        if not is_valid:
            return False, message
        
        session.add(data)
        session.commit()
        return True, "Invoice created successfully."
    
    @staticmethod
    def get(id: int, session: Session) -> tuple[bool, Invoice | str]:
        invoice = session.get(Invoice, id)
        return (False, "Invoice not found.") if not invoice else (True, invoice)

    @staticmethod
    def update(invoice: Invoice, data: Invoice, session: Session) -> tuple[bool, str]:
        invoice.invoice_no = data.invoice_no
        invoice.issue_date = data.issue_date
        invoice.pdf_html = data.pdf_html

        session.add(invoice)
        session.commit()
        return True, "Invoice updated successfully."

    @staticmethod
    def delete(id: int, session: Session) -> tuple[bool, str]:
        invoice = session.get(Invoice, id)
        if not invoice:
            return False, "Invoice not found."

        session.delete(invoice)
        session.commit()
        return True, "Invoice deleted successfully." 

    @staticmethod
    def count_by_client_id(client_id: int, session: Session) -> int:
        try:
            statement = select(func.count()).select_from(Invoice).where(Invoice.client_id == client_id)
            return True, session.exec(statement).one()
        except Exception as e:
            return False, str(e)

class AppSettingCRUD:
    @staticmethod
    def validate_data(data: AppSetting) -> tuple[bool, str]:
        try:
            AppSetting.model_validate(data)
            return True, data
        except Exception as e:
            return False, str(e)
        
    @staticmethod
    def create(data: AppSetting, session: Session) -> tuple[bool, str]:
        is_valid, message = AppSettingCRUD.validate_data(data)
        if not is_valid:
            return False, message
        
        session.add(data)
        session.commit()
        return True, "AppSetting created successfully."
    
    @staticmethod
    def get(id: int, session: Session) -> tuple[bool, AppSetting | str]:
        app_setting = session.get(AppSetting, id)
        return (False, "AppSetting not found.") if not app_setting else (True, app_setting.setting_value)

    @staticmethod
    def update(app_setting: AppSetting, data: AppSetting, session: Session) -> tuple[bool, str]:
        app_setting.setting_value = data.setting_value

        session.add(app_setting)
        session.commit()
        return True, "AppSetting updated successfully."

    @staticmethod
    def delete(id: int, session: Session) -> tuple[bool, str]:
        app_setting = session.get(AppSetting, id)
        if not app_setting:
            return False, "AppSetting not found."

        session.delete(app_setting)
        session.commit()
        return True, "AppSetting deleted successfully."

    @staticmethod
    def get_by_setting_name(setting_name: str, session: Session) -> tuple[bool, AppSetting | str]:
        statement = select(AppSetting).where(AppSetting.setting_name == setting_name)
        app_setting = session.exec(statement).first()
        return (False, "AppSetting not found.") if not app_setting else (True, app_setting.setting_value)