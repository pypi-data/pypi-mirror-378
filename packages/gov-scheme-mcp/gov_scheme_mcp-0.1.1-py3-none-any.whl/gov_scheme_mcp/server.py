"""Government Scheme MCP Server implementation."""

from typing import Any, Optional, List, Union
import httpx
import json
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("gov-scheme-mcp")

# Constants
BASE_URL = os.getenv("GOV_API_URL", "http://localhost:3000")

async def http_request(method: str, url_path: str, body: Optional[dict] = None) -> Any:
    """Make HTTP requests to the government scheme API."""
    url = url_path if url_path.startswith("http") else f"{BASE_URL}{url_path}"
    
    async with httpx.AsyncClient() as client:
        try:
            headers = {}
            if body is not None:
                headers["Content-Type"] = "application/json"
            
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=body,
                timeout=30.0
            )
            
            # Get response text
            text = await response.aread()
            text = text.decode('utf-8') if text else None
            
            # Try to parse as JSON
            data = None
            if text:
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    data = text
            
            if not response.is_success:
                error_msg = f"HTTP {response.status_code} {response.reason_phrase}"
                if data:
                    if isinstance(data, str):
                        error_msg += f": {data}"
                    else:
                        error_msg += f": {json.dumps(data)}"
                raise Exception(error_msg)
            
            return data
            
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {str(e)}")
        except Exception as e:
            raise Exception(str(e))

@mcp.tool()
async def health() -> str:
    """Check server health and API connectivity. Returns JSON with ok/api/error."""
    try:
        resp = await http_request("GET", "/")
        ok = resp and (resp.get("status") == "ok" or resp.get("name") == "gov-scheme-api")
        return json.dumps({"ok": bool(ok), "api": BASE_URL})
    except Exception as e:
        return json.dumps({"ok": False, "api": BASE_URL, "error": str(e)})

@mcp.tool()
async def create_scheme(
    code: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    department: Optional[str] = None,
    category: Optional[str] = None,
    benefit_type: Optional[str] = None,
    url: Optional[str] = None,
    contact: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    genders: Optional[List[str]] = None,
    income_min: Optional[float] = None,
    income_max: Optional[float] = None,
    employment_status: Optional[List[str]] = None,
    disabilities: Optional[List[str]] = None,
    social_categories: Optional[List[str]] = None,
    marital_statuses: Optional[List[str]] = None,
    religions: Optional[List[str]] = None,
    states: Optional[List[str]] = None,
    districts: Optional[List[str]] = None,
    urban_rural: Optional[List[str]] = None,
    professions: Optional[List[str]] = None,
    required_documents: Optional[List[str]] = None,
    caste_required: Optional[bool] = None,
    domicile_required: Optional[bool] = None,
    is_active: Optional[bool] = None
) -> str:
    """Create a new government scheme record. Pass only valid fields; unknown fields are ignored. Returns the created row as JSON.
    
    Args:
        code: Unique code for the scheme
        name: Name of the scheme
        description: Description of the scheme
        department: Department offering the scheme
        category: Program domain (education, health, agriculture, housing, women, child, senior, disability, minority, entrepreneurship, employment, skill, welfare)
        benefit_type: Type of benefit (cash, subsidy, scholarship, loan, insurance, pension, grant, in-kind)
        url: Official URL for the scheme
        contact: Contact information
        min_age: Minimum age requirement
        max_age: Maximum age requirement
        genders: List of allowed genders (male, female, other)
        income_min: Minimum income requirement
        income_max: Maximum income requirement
        employment_status: List of employment statuses (unemployed, farmer, student, salaried, entrepreneur)
        disabilities: List of applicable disabilities (visual, hearing, mobility, intellectual, multiple, other)
        social_categories: List of social categories (SC, ST, OBC, EWS, GENERAL)
        marital_statuses: List of marital statuses (single, married, divorced, widowed)
        religions: List of applicable religions
        states: List of applicable states/UTs
        districts: List of applicable districts
        urban_rural: List of area types (urban, rural)
        professions: List of applicable professions
        required_documents: List of required documents
        caste_required: Whether caste certificate is required
        domicile_required: Whether domicile certificate is required
        is_active: Whether the scheme is active
    """
    # Build data dictionary with only non-None values
    data = {}
    if code is not None: data["code"] = code
    if name is not None: data["name"] = name
    if description is not None: data["description"] = description
    if department is not None: data["department"] = department
    if category is not None: data["category"] = category
    if benefit_type is not None: data["benefit_type"] = benefit_type
    if url is not None: data["url"] = url
    if contact is not None: data["contact"] = contact
    if min_age is not None: data["min_age"] = min_age
    if max_age is not None: data["max_age"] = max_age
    if genders is not None: data["genders"] = genders
    if income_min is not None: data["income_min"] = income_min
    if income_max is not None: data["income_max"] = income_max
    if employment_status is not None: data["employment_status"] = employment_status
    if disabilities is not None: data["disabilities"] = disabilities
    if social_categories is not None: data["social_categories"] = social_categories
    if marital_statuses is not None: data["marital_statuses"] = marital_statuses
    if religions is not None: data["religions"] = religions
    if states is not None: data["states"] = states
    if districts is not None: data["districts"] = districts
    if urban_rural is not None: data["urban_rural"] = urban_rural
    if professions is not None: data["professions"] = professions
    if required_documents is not None: data["required_documents"] = required_documents
    if caste_required is not None: data["caste_required"] = caste_required
    if domicile_required is not None: data["domicile_required"] = domicile_required
    if is_active is not None: data["is_active"] = is_active
    
    if not data:
        return json.dumps({"error": "No valid fields provided"})
    
    try:
        created = await http_request("POST", "/api/schemes", data)
        return json.dumps(created)
    except Exception as e:
        return str(e)

@mcp.tool()
async def read_scheme(id: int) -> str:
    """Fetch a single scheme by numeric ID.
    
    Args:
        id: The numeric ID of the scheme to fetch
    """
    try:
        item = await http_request("GET", f"/api/schemes/{id}")
        return json.dumps(item)
    except Exception as e:
        return str(e)

@mcp.tool()
async def search_schemes(
    q: Optional[str] = None,
    age: Optional[Union[int, str]] = None,
    income: Optional[Union[float, str]] = None,
    gender: Optional[Union[str, List[str]]] = None,
    employmentStatus: Optional[Union[str, List[str]]] = None,
    disabilities: Optional[Union[str, List[str]]] = None,
    socialCategories: Optional[Union[str, List[str]]] = None,
    maritalStatus: Optional[Union[str, List[str]]] = None,
    religion: Optional[Union[str, List[str]]] = None,
    state: Optional[Union[str, List[str]]] = None,
    district: Optional[Union[str, List[str]]] = None,
    urbanRural: Optional[Union[str, List[str]]] = None,
    profession: Optional[Union[str, List[str]]] = None,
    casteRequired: Optional[Union[bool, str]] = None,
    domicileRequired: Optional[Union[bool, str]] = None,
    category: Optional[str] = None,
    benefitType: Optional[str] = None,
    active: Optional[Union[bool, str]] = None,
    limit: Optional[Union[int, str]] = 100,
    offset: Optional[Union[int, str]] = 0
) -> str:
    """Search schemes by user profile/filters. Supports various criteria for eligibility matching.
    
    Args:
        q: Text to match in name/description
        age: Age of the user
        income: Income of the user
        gender: Gender (male, female, other)
        employmentStatus: Employment status (unemployed, farmer, student, salaried, entrepreneur)
        disabilities: Disabilities (visual, hearing, mobility, intellectual, multiple, other)
        socialCategories: Social categories (SC, ST, OBC, EWS, GENERAL)
        maritalStatus: Marital status (single, married, divorced, widowed)
        religion: Religion
        state: State/UT name
        district: District name
        urbanRural: Area type (urban, rural)
        profession: Profession
        casteRequired: Whether caste certificate is required
        domicileRequired: Whether domicile certificate is required
        category: Program category
        benefitType: Type of benefit (cash, subsidy, scholarship, loan, insurance, pension, grant, in-kind)
        active: Whether to only include active schemes
        limit: Maximum number of results (default: 100)
        offset: Number of results to skip (default: 0)
    """
    # Build payload with all provided parameters
    payload = {}
    if q is not None: payload["q"] = q
    if age is not None: payload["age"] = age
    if income is not None: payload["income"] = income
    if gender is not None: payload["gender"] = gender
    if employmentStatus is not None: payload["employmentStatus"] = employmentStatus
    if disabilities is not None: payload["disabilities"] = disabilities
    if socialCategories is not None: payload["socialCategories"] = socialCategories
    if maritalStatus is not None: payload["maritalStatus"] = maritalStatus
    if religion is not None: payload["religion"] = religion
    if state is not None: payload["state"] = state
    if district is not None: payload["district"] = district
    if urbanRural is not None: payload["urbanRural"] = urbanRural
    if profession is not None: payload["profession"] = profession
    if casteRequired is not None: payload["casteRequired"] = casteRequired
    if domicileRequired is not None: payload["domicileRequired"] = domicileRequired
    if category is not None: payload["category"] = category
    if benefitType is not None: payload["benefitType"] = benefitType
    if active is not None: payload["active"] = active
    if limit is not None: payload["limit"] = limit
    if offset is not None: payload["offset"] = offset
    
    try:
        res = await http_request("POST", "/api/schemes/search", payload)
        return json.dumps(res)
    except Exception as e:
        return str(e)

def run_server():
    """Run the MCP server."""
    mcp.run(transport='stdio')