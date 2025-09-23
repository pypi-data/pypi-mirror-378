# Government Scheme MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for accessing and managing Indian Government Schemes database. This server provides tools for searching, creating, and managing government benefit schemes with comprehensive eligibility filtering.

## Features

-   **Health Check**: Verify server connectivity and API status
-   **Scheme Search**: Advanced filtering by demographics, geography, income, and eligibility criteria
-   **Scheme Management**: Create and retrieve government scheme records
-   **Comprehensive Filtering**: Support for age, gender, income, employment status, social categories, disabilities, and more

## Installation

### From PyPI (when published)

```bash
pip install gov-scheme-mcp
```

### From Source

```bash
git clone https://github.com/magicstack-llp/gov-scheme-mcp-py
cd gov-scheme-mcp
pip install -e .
```

## Usage

### As an MCP Server

The server can be used with any MCP-compatible client:

```bash
gov-scheme-mcp
```

### Environment Variables

-   `GOV_API_URL`: Base URL for the government schemes API (default: `http://localhost:3000`)

## Available Tools

### `health()`

Check server health and API connectivity.

**Returns**: JSON with connection status and API endpoint information.

### `create_scheme(...)`

Create a new government scheme record with comprehensive metadata.

**Parameters**:

-   `code`: Unique scheme identifier
-   `name`: Scheme name
-   `description`: Detailed description
-   `department`: Government department
-   `category`: Program domain (education, health, agriculture, etc.)
-   `benefit_type`: Type of benefit (cash, subsidy, scholarship, loan, insurance, pension, grant, in-kind)
-   `url`: Official scheme URL
-   `contact`: Contact information
-   Demographics: `min_age`, `max_age`, `genders`
-   Economic: `income_min`, `income_max`, `employment_status`
-   Social: `social_categories`, `marital_statuses`, `religions`, `disabilities`
-   Geographic: `states`, `districts`, `urban_rural`
-   Requirements: `required_documents`, `caste_required`, `domicile_required`
-   Status: `is_active`

### `read_scheme(id)`

Fetch a single scheme by numeric ID.

**Parameters**:

-   `id`: Numeric scheme ID

### `search_schemes(...)`

Search schemes with advanced filtering capabilities.

**Parameters**:

-   `q`: Text search in name/description
-   `age`: User age for eligibility filtering
-   `income`: User income level
-   `gender`: Gender filter (male, female, other)
-   `employmentStatus`: Employment status (unemployed, farmer, student, salaried, entrepreneur)
-   `disabilities`: Disability categories (visual, hearing, mobility, intellectual, multiple, other)
-   `socialCategories`: Social categories (SC, ST, OBC, EWS, GENERAL)
-   `maritalStatus`: Marital status (single, married, divorced, widowed)
-   `religion`: Religious affiliation
-   `state`: State/UT name
-   `district`: District name
-   `urbanRural`: Area type (urban, rural)
-   `profession`: Professional category
-   `casteRequired`: Filter by caste certificate requirement
-   `domicileRequired`: Filter by domicile certificate requirement
-   `category`: Scheme category filter
-   `benefitType`: Benefit type filter
-   `active`: Active schemes only
-   `limit`: Maximum results (default: 100)
-   `offset`: Result offset (default: 0)

## Configuration for MCP Clients

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
	"mcpServers": {
		"gov-scheme-mcp": {
			"command": "gov-scheme-mcp",
			"env": {
				"GOV_API_URL": "https://your-api-server.com"
			}
		}
	}
}
```

### Other MCP Clients

Configure the server command as `gov-scheme-mcp` with the appropriate environment variables.

## Development

### Setup

```bash
git clone https://github.com/magicstack-llp/gov-scheme-mcp-py
cd gov-scheme-mcp
pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

### Code Formatting

```bash
black src/
isort src/
```

### Type Checking

```bash
mypy src/
```

## API Requirements

This MCP server requires a compatible government schemes API with the following endpoints:

-   `GET /`: Health check endpoint
-   `POST /api/schemes`: Create new scheme
-   `GET /api/schemes/{id}`: Retrieve scheme by ID
-   `POST /api/schemes/search`: Search schemes with filters

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run the test suite
6. Submit a pull request

## Support

For issues and questions:

-   Open an issue on [GitHub](https://github.com/magicstack-llp/gov-scheme-mcp-py/issues)
-   Check the [documentation](https://github.com/magicstack-llp/gov-scheme-mcp-py#readme)

## Related Projects

-   [Model Context Protocol](https://modelcontextprotocol.io)
-   [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
