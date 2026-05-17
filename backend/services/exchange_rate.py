import requests
from backend.core.config import settings

def get_exchange_rate(base_currency: str = "USD", target_currency: str = "COP") -> float:
    """
    Fetches the exchange rate for the target_currency based on the base_currency.
    Uses the free api.exchangerate-api.com API.
    """
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    rates = data.get("rates", {})
    if target_currency not in rates:
        raise ValueError(f"Exchange rate for {target_currency} not found in the response.")
        
    return rates[target_currency]

def get_exchange_rate_message(base_currency: str = None, target_currency: str = None) -> str:
    """
    Builds the WhatsApp message with the exchange rate.
    """
    base = base_currency or settings.base_currency
    target = target_currency or settings.target_currency
    
    try:
        rate = get_exchange_rate(base_currency=base, target_currency=target)
        # Format with 2 decimal places and comma separators
        formatted_rate = f"{rate:,.2f}"
        message = f"📈 *Daily Exchange Rate Update*\n\n1 {base} = *{formatted_rate}* {target}\n\nHave a great day!"
        return message
    except Exception as e:
        return f"⚠️ Could not fetch exchange rate for {base} to {target} today. Error: {str(e)}"
