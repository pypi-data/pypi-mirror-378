# SBOM Upload Validator

[![PyPI version](https://badge.fury.io/py/sbom-upload-validator.svg)](https://badge.fury.io/py/sbom-upload-validator)
[![Docker Hub](https://img.shields.io/docker/pulls/stljim/sbom-upload-validator)](https://hub.docker.com/r/stljim/sbom-upload-validator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A production-ready API service for GitLab pipeline SBOM uploads to OWASP Dependency-Track with hierarchical project management, comprehensive CI/CD automation, and federal network support.

## Architecture

The system implements a three-tier hierarchy in Dependency-Track:
- **District/Business Unit** (SuperParent) - Top-level organizational unit.
- **Business Line Applications** (Parent) - Department/division under a district or business unit.
- **Project** (Child) - Actual application, application component or service with versions.

### Key Features

- **🔄 Version Management**: New SBOMs create new versions, not new projects
- **📋 CycloneDX SBOMs**: Pure CycloneDX SBOM generation and processing (no SPDX)
- **🏗️ Hierarchical Organization**: Automatic project structure management using tags and parent relationships
- **🔐 Security Scanning**: Integrated Trivy, bandit, safety, and pip-audit security analysis
- **🚀 CI/CD Automation**: Complete GitHub Actions pipeline with automated testing and deployment
- **🐳 Multi-Platform Docker**: AMD64 and ARM64 container builds with security scanning
- **📦 PyPI Publishing**: Automated package publishing with Trusted Publishers
- **🔑 Dependency-Track Authentication**: Direct integration with Dependency-Track API keys for seamless authentication
- **🏛️ Federal Ready**: Pre-configured templates for government and enterprise deployments
- **🔗 GitLab Integration**: Rich metadata with project IDs, pipeline IDs, commit SHAs, and custom tags
- **⚙️ YAML Configuration**: Bulk hierarchy initialization from YAML configuration files

## Quick Start

### Prerequisites

- Python 3.8+
- Access to OWASP Dependency-Track instance
- Dependency-Track API key

### Installation

#### Option 1: PyPI Package (Recommended)

```bash
# Install from PyPI (latest stable release)
pip install sbom-upload-validator==1.1.0

# Set environment variables
export DT_URL=http://your-dependency-track-api-url
export DT_API_KEY=your-api-key
export API_KEY_GITLAB=your-sbom-upload-api-key

# Run the service
sbom-validator --host 0.0.0.0 --port 8888
```

#### Option 2: Docker Container (Production Ready)

```bash
# Pull from Docker Hub (multi-platform: AMD64/ARM64)
docker pull stljim/sbom-upload-validator:1.1.0

# Run container
docker run -p 8888:8888 \
  -e DT_URL=http://your-dependency-track-url \
  -e DT_API_KEY=your-api-key \
  -e API_KEY_GITLAB=your-sbom-upload-api-key \
  stljim/sbom-upload-validator:1.1.0

# Or use latest tag (always points to latest stable release)
docker pull stljim/sbom-upload-validator:latest
```

#### Option 3: Source Installation (Development)

```bash
# Clone the repository
git clone https://github.com/StL-Jim/sbom-upload-validator.git
cd sbom-upload-validator

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DT_URL=http://your-dependency-track-api-url
export DT_API_KEY=your-api-key
export API_KEY_GITLAB=your-sbom-upload-api-key

# Run the service
python app.py
```

### Docker Compose (Complete Stack)

```bash
# Start complete development stack
docker compose up -d

# This includes:
# - PostgreSQL database
# - Dependency-Track API server  
# - Dependency-Track frontend
# - SBOM Upload Validator API
```

### CLI Tools (PyPI Package)

The PyPI package includes command-line tools for management:

```bash
# Start the API server
sbom-validator --host 0.0.0.0 --port 8888

# Initialize hierarchy from YAML config
dt-hierarchy-init --config dt_hierarchy_config.yaml --dry-run

# Validate configuration
dt-config-validate
```

## 🏢 Organizational Structure & Team Management

The system implements a comprehensive organizational hierarchy with team-based access control:

### Current Implementation Status
- ✅ **27 projects** across 3 districts and 7 business lines
- ✅ **24 teams** with role-based permissions
- ✅ **131 team-to-project assignments** for granular access control
- ✅ **Portfolio Access Control** enabled in Dependency-Track

### Organizational Hierarchy

```
Organization: STLS
├── Technology Operations (District)
│   ├── Software Development
│   │   ├── ci-cd-pipeline
│   │   ├── code-repository
│   │   └── testing-framework
│   ├── Infrastructure Services
│   │   ├── backup-system
│   │   ├── network-analyzer
│   │   └── server-monitor
│   └── Cybersecurity
│       ├── access-control
│       ├── threat-detection
│       └── vulnerability-scanner
├── Mission Operations (District)
│   └── Intelligence
│       ├── analysis-workbench
│       ├── collection-management
│       ├── data-fusion
│       ├── decision-support
│       ├── radio-gateway
│       ├── satellite-comms
│       ├── secure-messaging
│       └── situation-awareness
└── Support Services (District)
    ├── Human Resources
    │   ├── personnel-system
    │   ├── security-clearance
    │   └── training-tracker
    ├── Finance and Acquisition
    │   ├── budget-system
    │   ├── expense-tracker
    │   └── procurement-portal
    └── Facilities
        ├── access-badge
        ├── asset-tracker
        └── building-automation
```

### Team Structure & Access Control

#### Access Levels
1. **Organization-wide**: `Top level Organization Roll-up View` → All projects
2. **District-level**: `STLS SuperParent Roll-up View` → District-specific projects
3. **Business Line Teams**: Scoped to specific business lines

#### Team Types by Function
- **Write Teams** (`*-Write`): SBOM upload and portfolio management
- **View Teams** (`*Roll-up view`): Read-only access for reporting
- **Analysis Teams** (`*-Analysis`): Vulnerability and policy analysis
- **INFOSEC Team**: Security management and policy enforcement

### Management Commands

```bash
# Initialize complete organizational structure
python simple_hierarchy_init.py

# Assign teams to projects based on organizational rules
python assign_teams_to_projects.py

# Create teams from organizational structure
python create_dt_teams.py

# Update team permissions
python fix_team_permissions.py
```

## 📡 API Endpoints

### Upload SBOM
```bash
POST /api/v1/sbom/upload
```

Upload SBOM with metadata for GitLab pipeline integration.

**Required Fields:**
- `district` - District name (SuperParent)
- `business_line` - Business line name (Parent)  
- `project_name` - Project name (Child)
- `version` - Project version
- `sbom` - SBOM file (multipart/form-data)

**Optional Fields:**
- `gitlab_project_id` - GitLab project ID
- `gitlab_pipeline_id` - GitLab pipeline ID
- `commit_sha` - Git commit SHA
- `branch` - Git branch (default: main)
- `tags` - Comma-separated custom tags

**Example:**
```bash
curl -X POST http://localhost:8888/api/v1/sbom/upload \
  -H "X-API-Key: your-api-key" \
  -F "district=North America" \
  -F "business_line=Financial Services" \
  -F "project_name=payment-api" \
  -F "version=1.2.3" \
  -F "gitlab_project_id=123" \
  -F "commit_sha=abc123def456" \
  -F "sbom=@/path/to/sbom.json"
```

**Note:** All API endpoints (except `/health`) require authentication via the `X-API-Key` header.

### Get Project Hierarchy
```bash
GET /api/v1/projects/hierarchy?district=<name>&business_line=<name>
```

### Get Project Versions
```bash
GET /api/v1/projects/<project_name>/versions?district=<name>&business_line=<name>
```

### Health Check
```bash
GET /health
```

## 🔗 GitLab CI/CD Integration

Add this to your `.gitlab-ci.yml` for automated SBOM uploads:

```yaml
sbom_upload:
  stage: security
  script:
    - |
      curl -X POST $SBOM_VALIDATOR_URL/api/v1/sbom/upload \
        -H "X-API-Key: $SBOM_VALIDATOR_API_KEY" \
        -F "district=$DISTRICT" \
        -F "business_line=$BUSINESS_LINE" \
        -F "project_name=$CI_PROJECT_NAME" \
        -F "version=$CI_COMMIT_TAG" \
        -F "gitlab_project_id=$CI_PROJECT_ID" \
        -F "gitlab_pipeline_id=$CI_PIPELINE_ID" \
        -F "commit_sha=$CI_COMMIT_SHA" \
        -F "branch=$CI_COMMIT_REF_NAME" \
        -F "sbom=@sbom.json"
  only:
    - tags
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DT_URL` | Dependency-Track server URL | `http://127.0.0.1:8080` | Yes |
| `DT_API_KEY` | Dependency-Track API key | - | Yes |
| `API_KEY_GITLAB` | GitLab pipeline API key | - | Yes |
| `API_KEY_ADMIN` | Admin API key for management | - | No |
| `PORT` | Server port | `8888` | No |
| `FLASK_ENV` | Flask environment | `production` | No |

### Using .env File

Create a `.env` file in the project root:

```bash
DT_URL=http://your-dependency-track-url
DT_API_KEY=your-api-key
API_KEY_GITLAB=your-gitlab-pipeline-key
API_KEY_ADMIN=your-admin-key
PORT=8888
FLASK_ENV=development
```

## 🔑 Dependency-Track API Key Authentication

The SBOM upload validator uses **Dependency-Track API keys directly** for authentication - no additional API key management required!

### How It Works
- Present any valid Dependency-Track API key via the `X-API-Key` header
- The validator performs a quick validation call to your DT server (`/api/v1/project`)
- Valid keys are cached for 5 minutes to optimize performance
- No additional configuration required beyond your existing DT setup

### Usage Example
```bash
# Use your DT API key directly
curl -X POST $SBOM_VALIDATOR_URL/api/v1/sbom/upload \
  -H "X-API-Key: odt_YourDependencyTrackAPIKey_Here" \
  -F "district=North America" \
  -F "business_line=Financial Services" \
  -F "project_name=payment-api" \
  -F "version=1.2.3" \
  -F "sbom=@sbom.json"
```

### Benefits
- **Centralized Management**: Manage API keys only in Dependency-Track
- **Consistent Permissions**: Leverage DT's existing user/team system
- **Audit Trail**: All access logged in Dependency-Track
- **No Duplication**: No need to maintain separate key systems
- **Performance**: 5-minute caching reduces API calls to DT server

### Key Management Endpoints

#### `GET /api/v1/keys/validate`
Validate your current Dependency-Track API key:

```bash
curl -X GET http://localhost:8888/api/v1/keys/validate \
  -H "X-API-Key: odt_YourDTAPIKey"

# Response
{
  "valid": true,
  "key_name": "dt-user",
  "key_type": "dependency-track",
  "message": "API key is valid"
}
```

#### `GET /api/v1/keys/list`
List recently used API keys (admin access only):

```bash
curl -X GET http://localhost:8888/api/v1/keys/list \
  -H "X-API-Key: odt_YourAdminDTAPIKey"

# Response showing cached keys
{
  "total_keys": 2,
  "dt_keys": 2,
  "keys": [
    {"name": "dt-user", "type": "dependency-track", "key_prefix": "odt_NEvK..."},
    {"name": "dt-admin", "type": "dependency-track", "key_prefix": "odt_XyZ1..."}
  ]
}
```

## 🏗️ Hierarchy Configuration System

### YAML-Based Bulk Initialization

The system supports bulk initialization of organizational hierarchies using YAML configuration files, designed for federal network deployments.

#### Quick Setup

```bash
# 1. Copy the example configuration
cp dt_hierarchy_config.example.yaml dt_hierarchy_config.yaml

# 2. Customize with your team UUIDs and organizational structure
# Edit dt_hierarchy_config.yaml

# 3. Preview what will be created (dry run)
python initialize_dt_hierarchy.py --dry-run

# 4. Initialize the complete hierarchy
python initialize_dt_hierarchy.py
```

#### Federal Network Template

The configuration includes federal-appropriate examples:

- **Technology Operations**: IT infrastructure, cybersecurity, software development
- **Mission Operations**: Command systems, communications, intelligence  
- **Support Services**: HR, finance, facilities management

Each district includes appropriate security and compliance tags:
- Security clearance levels (`clearance:secret`, `clearance:top-secret`)
- FISMA compliance markers (`compliance:fisma-high`)
- Data classification (`data:pii`, `data:classified`)
- Criticality levels (`criticality:critical`, `criticality:high`)

#### Configuration Management Commands

```bash
# Show configuration summary
python initialize_dt_hierarchy.py --summary

# Initialize specific district only  
python initialize_dt_hierarchy.py --district "Technology Operations"

# Validate existing hierarchy against config
python initialize_dt_hierarchy.py --validate

# Test configuration loading
python dt_config_loader.py
```

#### Configuration Structure

```yaml
hierarchy:
  "Your District Name":
    description: "District description"
    tags: ["clearance:secret", "category:technology"]
    teams: ["team-uuid-1", "team-uuid-2"]
    
    business_lines:
      "Your Business Line":
        description: "Business line description"  
        tags: ["function:development"]
        teams: ["bl-team-uuid"]
        
        projects:
          - name: "your-project"
            description: "Project description"
            tags: ["type:application", "criticality:high"]
```

See `dt_hierarchy_config.example.yaml` for a complete federal network template.

## 📦 Distribution Channels

### PyPI Package
[![PyPI version](https://badge.fury.io/py/sbom-upload-validator.svg)](https://pypi.org/project/sbom-upload-validator/)

```bash
pip install sbom-upload-validator==1.0.1
```

**Features:**
- 🚀 CLI tools for server management
- 📚 Library API for custom integrations  
- ⚙️ Configuration validation utilities
- 🏗️ Hierarchy initialization commands

### Docker Hub
[![Docker Pulls](https://img.shields.io/docker/pulls/stljim/sbom-upload-validator)](https://hub.docker.com/r/stljim/sbom-upload-validator)

```bash
docker pull stljim/sbom-upload-validator:latest
```

**Available Tags:**
- `latest` - Latest stable release (currently v1.0.1)
- `1.0.1` - Latest stable release
- `1.0.0` - Previous stable release
- `federal` - Federal network optimized
- `develop` - Development builds

**Multi-Architecture Support:**
- `linux/amd64` (Intel/AMD 64-bit)
- `linux/arm64` (ARM 64-bit)

## 🧪 Testing

### Quick API Testing
```bash
# Test API connectivity
python dt_api_utils.py

# Health check
curl http://localhost:8888/health

# View API documentation
open http://localhost:8888
```

### Examples & Test Data
For comprehensive testing scenarios, example SBOMs, and bulk upload utilities, see the companion repository:

**📋 [SBOM Upload Validator Examples](https://github.com/StL-Jim/sbom-upload-validator-examples)**

- **216 enterprise SBOM examples** across 12 industries
- **16 basic test SBOMs** for quick validation
- **Generation scripts** for custom SBOM datasets
- **Upload utilities** for bulk testing scenarios

```bash
# Clone examples repository
git clone https://github.com/StL-Jim/sbom-upload-validator-examples.git
cd sbom-upload-validator-examples

# Upload test data
python upload_test_sboms.py --directory test_sboms
```

## 📊 How It Works

1. **Hierarchy Management**: Service automatically creates District→Business Line→Project structure
2. **Version Detection**: Checks if project version already exists
3. **Smart Cloning**: If project exists but version doesn't, clones latest version preserving vulnerability data
4. **SBOM Upload**: Uploads SBOM to the appropriate project version in Dependency-Track
5. **Metadata Enrichment**: Tags projects with GitLab metadata for easy filtering and reporting

## 🚀 CI/CD Pipeline & Security

### Automated Workflows

The project includes comprehensive GitHub Actions workflows for:

- **🧪 Continuous Integration** (`ci.yml`):
  - Multi-Python version testing (3.9, 3.10, 3.11)
  - Code formatting with Black
  - Linting with flake8
  - Security scanning with bandit, safety, pip-audit
  - CycloneDX SBOM generation for the project itself

- **📦 Package Publishing** (`python-publish.yml`):
  - Automated PyPI publishing with Trusted Publishers
  - TestPyPI for release candidates
  - GitHub Releases with automated changelog
  - Manual publishing scripts for troubleshooting

- **🐳 Docker Builds** (`docker-build.yml`):
  - Multi-platform builds (AMD64/ARM64)
  - Security scanning with Trivy (filesystem + container)
  - Docker Hub publishing with metadata
  - SARIF security report uploads

### Security Features

- **🔒 Vulnerability Scanning**: Trivy scans for CVEs in dependencies and container images
- **🕵️ Static Analysis**: Bandit analyzes Python code for security issues
- **🛡️ Dependency Auditing**: Safety and pip-audit check for known vulnerabilities
- **📋 SBOM Generation**: Comprehensive CycloneDX SBOMs for supply chain transparency
- **🏷️ SARIF Integration**: Security results uploaded to GitHub Security tab

### Quality Assurance

- **📏 Code Formatting**: Automated Black formatting enforcement
- **🔍 Linting**: flake8 code quality checks
- **🧪 Testing**: pytest with coverage reporting
- **📋 Package Validation**: twine package integrity checks

## 🔧 Development

### Project Structure

```
├── app.py                              # Main Flask API application
├── dt_api_utils.py                     # Dependency-Track API client and hierarchy manager
├── dt_config_loader.py                 # YAML configuration loader and validator
├── initialize_dt_hierarchy.py          # Bulk hierarchy initialization script
├── dt_hierarchy_config.yaml            # Main hierarchy configuration file
├── dt_hierarchy_config.example.yaml    # Federal network configuration template
├── templates/
│   └── api_docs.html                   # API documentation page
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Container configuration
├── docker-compose.yml                  # Complete development stack
├── CLAUDE.md                           # Detailed architecture documentation
└── README.md                           # This file
```

### Running in Development Mode

```bash
FLASK_ENV=development python app.py
```

### Manual PyPI Publishing

For manual package publishing (when automated workflows fail or for testing):

#### Prerequisites
- PyPI account with API token
- Package version updated in `pyproject.toml` and `sbom_upload_validator/__init__.py`

#### Windows
```bash
# Run the provided batch script
manual_pypi_publish.bat
```

#### Unix/Linux/macOS
```bash
# Make script executable and run
chmod +x manual_pypi_publish.sh
./manual_pypi_publish.sh
```

#### Manual Step-by-Step
```bash
# 1. Install/upgrade build tools
python -m pip install --upgrade pip build twine

# 2. Clean previous builds
rm -rf dist/ build/ *.egg-info/

# 3. Build the package
python -m build

# 4. Check package integrity
python -m twine check dist/*

# 5. Upload to PyPI
python -m twine upload dist/*
```

**Authentication:**
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

**Files Created:**
- `manual_pypi_publish.bat` - Windows publishing script
- `manual_pypi_publish.sh` - Unix/Linux publishing script
- Both scripts handle the complete build and upload process

## 📚 Documentation

- **API Documentation**: Visit `/` endpoint for interactive documentation
- **Architecture Guide**: See `CLAUDE.md` for detailed implementation details
- **Dependency-Track API**: Includes complete OpenAPI specification in `openapi.yaml`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Complete API documentation available at the root endpoint
- **Architecture**: See `CLAUDE.md` for implementation details