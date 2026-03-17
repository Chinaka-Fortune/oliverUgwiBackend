from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.invoice import Invoice
from models.quote_request import QuoteRequest
