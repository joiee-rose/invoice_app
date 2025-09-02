from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, select
from sqlalchemy import func

from database import get_session
from models import Client, Service, ClientQuoteProfile, Quote, Invoice, AppSetting

SessionDependency = Annotated[Session, Depends(get_session)]

class ClientCRUD:
    @staticmethod
    def validate_data(data: Client) -> tuple[bool, str, Client | None]:
        try:
            Client.model_validate(data)
            return True, "Validation successful.", data
        except Exception as e:
            return False, str(e), None
        
    @staticmethod
    def create(
        data: Client,
        session: Session
    ) -> tuple[bool, str, Client | None]:
        is_valid, message, client = ClientCRUD.validate_data(data)
        if not is_valid:
            return False, message, None
        
        session.add(data)
        session.commit()
        session.refresh(data)

        return True, "Client created successfully.", client
    
    @staticmethod
    def get(
        id: int,
        session: Session
    ) -> tuple[bool, str, Client | None]:
        client = session.get(Client, id)
        if not client:
            return False, "Client not found.", None
        return True, "Client found.", client

    @staticmethod
    def update(
        client: Client,
        data: Client,
        session: Session
    ) -> tuple[bool, str, Client | None]:
        try:
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
            session.refresh(client)

            return True, "Client updated successfully.", client
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def delete(id: int, session: Session) -> tuple[bool, str, Client | None]:
        client = session.get(Client, id)
        if not client:
            return False, "Client not found.", None

        session.delete(client)
        session.commit()

        return True, "Client deleted successfully.", client

class ServiceCRUD:
    @staticmethod
    def validate_data(data: Service) -> tuple[bool, str, Service | None]:
        try:
            Service.model_validate(data)
            return True, "Validation successful.", data
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
    def delete(id: int, session: Session ) -> tuple[bool, str, Service | None]:
        service = session.get(Service, id)
        if not service:
            return False, "Service not found.", None

        session.delete(service)
        session.commit()

        return True, "Service deleted successfully.", service

class ClientQuoteProfileCRUD:
    @staticmethod
    def validate_data(
        data: ClientQuoteProfile
    ) -> tuple[bool, str, ClientQuoteProfile | None]:
        try:
            ClientQuoteProfile.model_validate(data)
            return True, "Validation successful.", data
        except Exception as e:
            return False, str(e), None
        
    @staticmethod
    def create(
        data: ClientQuoteProfile,
        session: Session
    ) -> tuple[bool, str, ClientQuoteProfile | None]:
        (
            is_valid,
            message,
            quote_profile,
        ) = ClientQuoteProfileCRUD.validate_data(data)
        if not is_valid:
            return False, message, None
        
        session.add(data)
        session.commit()
        session.refresh(data)

        return True, "Quote Profile created successfully.", quote_profile
    
    @staticmethod
    def get(
        id: int,
        session: Session
    ) -> tuple[bool, str, ClientQuoteProfile | None]:
        quote_profile = session.get(ClientQuoteProfile, id)
        if not quote_profile:
            return False, "Quote Profile not found.", None
        return True, "Quote Profile found.", quote_profile

    @staticmethod
    def update(
        quote_profile: ClientQuoteProfile,
        data: ClientQuoteProfile,
        session: Session
    ) -> tuple[bool, str, ClientQuoteProfile | None]:
        try:
            quote_profile.services = data.services
            quote_profile.grand_total = data.grand_total
            quote_profile.min_monthly_charge = data.min_monthly_charge

            session.add(quote_profile)
            session.commit()
            session.refresh(quote_profile)

            return True, "Quote Profile updated successfully.", quote_profile
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def delete(
        id: int,
        session: Session
    ) -> tuple[bool, str, ClientQuoteProfile | None]:
        quote_profile = session.get(ClientQuoteProfile, id)
        if not quote_profile:
            return False, "Quote Profile not found.", None

        session.delete(quote_profile)
        session.commit()

        return True, "Quote Profile deleted successfully.", quote_profile

class QuoteCRUD:
    @staticmethod
    def validate_data(data: Quote) -> tuple[bool, str, Quote | None]:
        try:
            Quote.model_validate(data)
            return True, "Validation successful.", data
        except Exception as e:
            return False, str(e), None
        
    @staticmethod
    def create(data: Quote, session: Session) -> tuple[bool, str, Quote | None]:
        is_valid, message, quote = QuoteCRUD.validate_data(data)
        if not is_valid:
            return False, message, None
        
        session.add(data)
        session.commit()
        session.refresh(data)

        return True, "Quote created successfully.", quote

    @staticmethod
    def get(id: int, session: Session) -> tuple[bool, str, Quote | None]:
        quote = session.get(Quote, id)
        if not quote:
            return False, "Quote not found.", None
        return True, "Quote found.", quote

    @staticmethod
    def update(
        quote: Quote,
        data: Quote,
        session: Session
    ) -> tuple[bool, str, Quote | None]:
        try:
            quote.quote_no = data.quote_no
            quote.issue_date = data.issue_date
            quote.pdf_html = data.pdf_html

            session.add(quote)
            session.commit()
            session.refresh(quote)

            return True, "Quote updated successfully.", quote
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def delete(id: int, session: Session) -> tuple[bool, str, Quote | None]:
        quote = session.get(Quote, id)
        if not quote:
            return False, "Quote not found.", None

        session.delete(quote)
        session.commit()
        
        return True, "Quote deleted successfully.", quote

    @staticmethod
    def count_by_client_id(
        client_id: int,
        session: Session
    ) -> tuple[bool, str, int | None]:
        try:
            statement = (
                select(func.count())
                .select_from(Quote)
                .where(Quote.client_id == client_id)
            )
            return True, "Operation successful.", session.exec(statement).one()
        except Exception as e:
            return False, str(e), None

class InvoiceCRUD:
    @staticmethod
    def validate_data(data: Invoice) -> tuple[bool, str, Invoice | None]:
        try:
            Invoice.model_validate(data)
            return True, "Validation successful.", data
        except Exception as e:
            return False, str(e), None
        
    @staticmethod
    def create(
        data: Invoice,
        session: Session
    ) -> tuple[bool, str, Invoice | None]:
        is_valid, message, invoice = InvoiceCRUD.validate_data(data)
        if not is_valid:
            return False, message, None

        session.add(data)
        session.commit()
        session.refresh(data)

        return True, "Invoice created successfully.", invoice

    @staticmethod
    def get(id: int, session: Session) -> tuple[bool, str, Invoice | None]:
        invoice = session.get(Invoice, id)
        if not invoice:
            return False, "Invoice not found.", None
        return True, "Invoice found.", invoice

    @staticmethod
    def update(
        invoice: Invoice,
        data: Invoice,
        session: Session
    ) -> tuple[bool, str, Invoice | None]:
        try:
            invoice.invoice_no = data.invoice_no
            invoice.issue_date = data.issue_date
            invoice.pdf_html = data.pdf_html

            session.add(invoice)
            session.commit()
            session.refresh(invoice)

            return True, "Invoice updated successfully.", invoice
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def delete(id: int, session: Session) -> tuple[bool, str, Invoice | None]:
        invoice = session.get(Invoice, id)
        if not invoice:
            return False, "Invoice not found.", None

        session.delete(invoice)
        session.commit()

        return True, "Invoice deleted successfully.", invoice

    @staticmethod
    def count_by_client_id(
        client_id: int,
        session: Session
    ) -> tuple[bool, str, int | None]:
        try:
            statement = (
                select(func.count())
                .select_from(Invoice)
                .where(Invoice.client_id == client_id)
            )
            return True, "Operation successful.", session.exec(statement).one()
        except Exception as e:
            return False, str(e), None

class AppSettingCRUD:
    @staticmethod
    def validate_data(data: AppSetting) -> tuple[bool, str, AppSetting | None]:
        try:
            AppSetting.model_validate(data)
            return True, "Validation successful.", data
        except Exception as e:
            return False, str(e), None
        
    @staticmethod
    def create(
        data: AppSetting,
        session: Session
    ) -> tuple[bool, str, AppSetting | None]:
        is_valid, message, app_setting = AppSettingCRUD.validate_data(data)
        if not is_valid:
            return False, message, None

        session.add(data)
        session.commit()
        session.refresh(data)
        
        return True, "App Setting created successfully.", app_setting

    @staticmethod
    def get(id: int, session: Session) -> tuple[bool, str, AppSetting | None]:
        app_setting = session.get(AppSetting, id)
        if not app_setting:
            return False, "App Setting not found.", None
        return True, "App Setting found.", app_setting

    @staticmethod
    def update(
        app_setting: AppSetting,
        data: AppSetting,
        session: Session
    ) -> tuple[bool, str, AppSetting | None]:
        try:
            app_setting.setting_value = data.setting_value

            session.add(app_setting)
            session.commit()
            session.refresh(app_setting)

            return True, "App Setting updated successfully.", app_setting
        except Exception as e:
            return False, str(e), None

    @staticmethod
    def delete(
        id: int,
        session: Session
    ) -> tuple[bool, str, AppSetting | None]:
        app_setting = session.get(AppSetting, id)
        if not app_setting:
            return False, "App Setting not found.", None

        session.delete(app_setting)
        session.commit()
        return True, "App Setting deleted successfully.", app_setting

    @staticmethod
    def get_by_setting_name(
        setting_name: str,
        session: Session
    ) -> tuple[bool, str, AppSetting | None]:
        statement = (
            select(AppSetting)
            .where(AppSetting.setting_name == setting_name)
        )
        app_setting = session.exec(statement).first()
        if not app_setting:
            return False, "App Setting not found.", None
        return True, "App Setting found.", app_setting