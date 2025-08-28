from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from database import get_session
from models import Client, Service, ClientQuoteProfile, AppSetting

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
    def validate_data(data: Service) -> tuple[bool, str]:
        try:
            Service.model_validate(data)
            return True, data
        except Exception as e:
            return False, str(e)
        
    @staticmethod
    def create(data: Service, session: Session) -> tuple[bool, str]:
        is_valid, message = ServiceCRUD.validate_data(data)
        if not is_valid:
            return False, message
        
        session.add(data)
        session.commit()
        return True, "Service created successfully."
    
    @staticmethod
    def get(id: int, session: Session) -> tuple[bool, Service | str]:
        service = session.get(Service, id)
        return (False, "Service not found.") if not service else (True, service)

    @staticmethod
    def update(service: Service, data: Service, session: Session) -> tuple[bool, str]:
        service.name = data.name
        service.description = data.description
        service.unit_price = data.unit_price

        session.add(service)
        session.commit()
        return True, "Service updated successfully."

    @staticmethod
    def delete(id: int, session: Session) -> tuple[bool, str]:
        service = session.get(Service, id)
        if not service:
            return False, "Service not found."

        session.delete(service)
        session.commit()
        return True, "Service deleted successfully."

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
    
# TODO - class InvoiceCRUD

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
        return (False, "AppSetting not found.") if not app_setting else (True, app_setting)

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