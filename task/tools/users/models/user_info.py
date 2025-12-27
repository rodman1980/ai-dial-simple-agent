# User information data models for the user service API
# Defines Pydantic models for user creation, updates, and nested address/credit card data.
# Used for request/response validation and serialization with the mock user service.

from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    """Physical address information for a user.
    
    Attributes:
        country: Country name
        city: City name
        street: Street name and number
        flat_house: Apartment or house identifier
    """
    country: str
    city: str
    street: str
    flat_house: str


class CreditCard(BaseModel):
    """Payment card information for a user.
    
    Attributes:
        num: Credit card number
        cvv: Card security code (3-4 digits)
        exp_date: Expiration date (typically MM/YY format)
    """
    num: str
    cvv: str
    exp_date: str


class UserCreate(BaseModel):
    """Schema for creating a new user in the service.
    
    All required fields must be provided; optional fields can be omitted.
    This model is used to validate incoming POST requests to the user service.
    
    Attributes:
        name: User's first name (required)
        surname: User's last name (required)
        email: User's email address (required)
        phone: User's phone number (optional)
        date_of_birth: Birth date as string (optional)
        address: Full address details (optional, nested Address model)
        gender: Gender identity (optional)
        company: Current employer name (optional)
        salary: Annual salary amount (optional)
        about_me: Short bio or description (required)
        credit_card: Payment card information (optional, nested CreditCard model)
    """
    name: str
    surname: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[Address] = None
    gender: Optional[str] = None
    company: Optional[str] = None
    salary: Optional[float] = None
    about_me: str
    credit_card: Optional[CreditCard] = None


class UserUpdate(BaseModel):
    """Schema for updating an existing user's information.
    
    All fields are optional, allowing partial updates where only modified fields
    are sent. This model is used to validate incoming PATCH/PUT requests.
    
    Attributes:
        name: User's first name (optional for update)
        surname: User's last name (optional for update)
        email: User's email address (optional for update)
        phone: User's phone number (optional for update)
        date_of_birth: Birth date as string (optional for update)
        address: Full address details (optional, nested Address model)
        gender: Gender identity (optional for update)
        company: Current employer name (optional for update)
        salary: Annual salary amount (optional for update)
        credit_card: Payment card information (optional, nested CreditCard model)
    """
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[Address] = None
    gender: Optional[str] = None
    company: Optional[str] = None
    salary: Optional[float] = None
    credit_card: Optional[CreditCard] = None