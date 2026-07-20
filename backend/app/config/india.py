"""
Single source of truth for the India-only job search scope.

Everything about "which country are we searching" lives here so it is not
scattered across the sources, the normalizer and the aggregator the way it
used to be.
"""

COUNTRY_NAME = "India"
COUNTRY_CODE = "IN"          # ISO-3166 alpha-2, used in normalized job records
JSEARCH_COUNTRY = "in"       # what the JSearch API expects (lowercase)
CURRENCY_SYMBOL = "₹"   # rupee

# Cities offered in the UI dropdown, mapped to their state.
# Keys are the canonical spelling we store and display.
CITY_TO_STATE = {
    "Bengaluru": "Karnataka",
    "Hyderabad": "Telangana",
    "Pune": "Maharashtra",
    "Mumbai": "Maharashtra",
    "Navi Mumbai": "Maharashtra",
    "Thane": "Maharashtra",
    "Nagpur": "Maharashtra",
    "Delhi": "Delhi",
    "New Delhi": "Delhi",
    "Gurugram": "Haryana",
    "Noida": "Uttar Pradesh",
    "Ghaziabad": "Uttar Pradesh",
    "Faridabad": "Haryana",
    "Chennai": "Tamil Nadu",
    "Coimbatore": "Tamil Nadu",
    "Madurai": "Tamil Nadu",
    "Kolkata": "West Bengal",
    "Ahmedabad": "Gujarat",
    "Surat": "Gujarat",
    "Vadodara": "Gujarat",
    "Gandhinagar": "Gujarat",
    "Jaipur": "Rajasthan",
    "Kochi": "Kerala",
    "Thiruvananthapuram": "Kerala",
    "Kozhikode": "Kerala",
    "Chandigarh": "Chandigarh",
    "Mohali": "Punjab",
    "Ludhiana": "Punjab",
    "Indore": "Madhya Pradesh",
    "Bhopal": "Madhya Pradesh",
    "Lucknow": "Uttar Pradesh",
    "Kanpur": "Uttar Pradesh",
    "Visakhapatnam": "Andhra Pradesh",
    "Vijayawada": "Andhra Pradesh",
    "Bhubaneswar": "Odisha",
    "Patna": "Bihar",
    "Ranchi": "Jharkhand",
    "Raipur": "Chhattisgarh",
    "Guwahati": "Assam",
    "Dehradun": "Uttarakhand",
    "Mysuru": "Karnataka",
    "Mangaluru": "Karnataka",
    "Nashik": "Maharashtra",
    "Rajkot": "Gujarat",
}

INDIAN_CITIES = sorted(CITY_TO_STATE.keys())
INDIAN_STATES = sorted(set(CITY_TO_STATE.values()))

# Alternate spellings and older names that job boards still publish.
# Maps lowercase variant -> canonical city name above.
CITY_ALIASES = {
    "bangalore": "Bengaluru",
    "bangaluru": "Bengaluru",
    "bengaluru urban": "Bengaluru",
    "blr": "Bengaluru",
    "bombay": "Mumbai",
    "gurgaon": "Gurugram",
    "calcutta": "Kolkata",
    "madras": "Chennai",
    "trivandrum": "Thiruvananthapuram",
    "cochin": "Kochi",
    "ernakulam": "Kochi",
    "calicut": "Kozhikode",
    "mysore": "Mysuru",
    "mangalore": "Mangaluru",
    "vizag": "Visakhapatnam",
    "pondicherry": "Puducherry",
    "baroda": "Vadodara",
    "poona": "Pune",
    "new delhi": "Delhi",
    "delhi ncr": "Delhi",
    "ncr": "Delhi",
    "greater noida": "Noida",
    "secunderabad": "Hyderabad",
}

# Region-scope tiers. Lower is a better regional match; results are ordered by
# this first and by semantic score second, so exact-region jobs always lead.
TIER_EXACT_CITY = 0
TIER_SAME_STATE = 1
TIER_ELSEWHERE = 2

# Tokens that indicate a listing is India-wide / remote rather than a specific city.
REMOTE_TOKENS = {"remote", "anywhere", "work from home", "wfh", "india"}


def canonical_city(value: str) -> str:
    """
    Resolves a free-form city string to its canonical spelling.
    Returns '' when the value does not look like a city we know.
    """
    if not value:
        return ""
    cleaned = " ".join(value.strip().lower().split())
    if cleaned in CITY_ALIASES:
        return CITY_ALIASES[cleaned]
    for city in CITY_TO_STATE:
        if city.lower() == cleaned:
            return city
    return value.strip()


def state_for_city(city: str) -> str:
    """Returns the state a canonical city sits in, or '' if unknown."""
    return CITY_TO_STATE.get(canonical_city(city), "")


def looks_indian(location: str, country: str = "") -> bool:
    """
    True when a job record appears to be located in India.

    Checked against the country field first, then the location string, so a
    listing that only says 'Bengaluru, KA' is still recognised.
    """
    haystack = f"{country} {location}".lower()
    if "india" in haystack or " in," in haystack or haystack.strip().endswith(" in"):
        return True
    for city in CITY_TO_STATE:
        if city.lower() in haystack:
            return True
    for alias in CITY_ALIASES:
        if alias in haystack:
            return True
    for state in INDIAN_STATES:
        if state.lower() in haystack:
            return True
    return False
