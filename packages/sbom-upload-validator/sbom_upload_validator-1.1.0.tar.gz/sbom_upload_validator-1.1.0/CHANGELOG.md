# Changelog

All notable changes to the SBOM Upload Validator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **🏢 Complete Organizational Structure Implementation**
  - 24 teams created with role-based permissions based on Excel organizational analysis
  - 27 projects organized across 3 districts and 7 business lines (STLS structure)
  - 131 team-to-project assignments via Portfolio Access Control (PAC)
  - Hierarchical team structure: Organization → District → Business Line → Project
- **🔧 Enhanced Team Management Scripts**
  - `assign_teams_to_projects.py` - Automated team-to-project assignment with organizational rules
  - `simple_hierarchy_init.py` - Project hierarchy initialization from YAML configuration
  - `create_dt_teams.py` - Team creation from Excel organizational structure analysis
  - `fix_team_permissions.py` - Permission management utility for team maintenance
  - `analyze_dt_permissions.py` - Excel file parser for organizational team extraction
- **🔑 Direct Dependency-Track API Key Authentication**
  - Hybrid authentication supporting both legacy API keys and native DT API keys
  - 5-minute caching for DT API key validation to optimize performance
  - New API endpoints: `/api/v1/keys/validate` and `/api/v1/keys/list`
  - Seamless integration with existing DT user/team permission system
- **📚 Enhanced Documentation**
  - Complete organizational structure diagram added to README.md
  - Comprehensive team management documentation in CLAUDE.md
  - TEAM_CREATION_SUMMARY.md documenting all 131 team assignments
  - Fixed GitHub Actions badges with working static alternatives

### Changed
- **🔧 Enhanced DT API Integration**
  - Fixed team assignment using correct Portfolio Access Control endpoints (`PUT /api/v1/acl/mapping`)
  - Improved error handling for 409 conflicts and empty API responses
  - Enhanced `_make_request()` method with better response parsing and caching
  - Added comprehensive team management methods to DependencyTrackAPI class
- **📦 Updated Dependencies**
  - Added PyYAML==6.0.1 for YAML configuration file support
  - Enhanced requirements.txt with debugging support (debugpy)

### Fixed
- **🐛 API Endpoint Corrections**
  - Resolved 404 errors in team-to-project assignments by discovering correct ACL endpoints
  - Fixed Unicode encoding issues in Windows command prompt output
  - Improved conflict detection for existing team assignments ("Already assigned" vs errors)
- **🔒 Authentication & Security Improvements**
  - Added bcrypt password reset utility with Java-compatible salt format ($2a$ vs $2b$)
  - Enhanced API key validation with proper caching and error handling
  - Fixed environment variable persistence issues in wrapper scripts

### Security
- **🛡️ Complete Access Control Implementation**
  - Portfolio Access Control fully operational with 131 granular team-to-project assignments
  - Role-based team structure implemented for federal organizational compliance
  - Proper ACL inheritance implemented: District → Business Line → Project levels
  - Team permission structure: Write teams, View teams, Analysis teams, INFOSEC teams

## [1.0.2] - 2025-09-19

### Added
- **📦 DockerHub Integration**
  - Pre-built container images published to DockerHub (`stljim/sbom-upload-validator`)
  - Multi-platform support (AMD64/ARM64) in published images
  - Versioned releases for reliable deployments

### Changed
- **🚀 Simplified Deployment**
  - Updated docker-compose.yml to use pre-built DockerHub image instead of local builds
  - Improved deployment reliability with versioned, published container images
  - Eliminated need for local Docker image compilation

### Removed
- **🧹 Repository Cleanup**
  - Moved 216+ enterprise SBOM examples to separate repository for better organization
  - Reduced main repository size and complexity
  - Cleaner development experience with focused codebase

## [1.0.1] - 2025-09-17

### Fixed
- Fixed Trusted Publisher environment configuration for PyPI publishing
- Fixed cycloneDX import paths for cyclonedx-python-lib v11.1.0 compatibility
- Fixed cycloneDX command syntax issues in SBOM generation workflows

### Changed
- Updated GitHub Actions workflows to include proper environment specifications
- Improved PyPI publishing reliability with environment protection rules

## [1.0.0] - 2025-09-17

### Added
- **Complete CI/CD Pipeline**: GitHub Actions workflows for testing, security scanning, and deployment
- **PyPI Publishing**: Automated package publishing with Trusted Publishers
- **Docker Multi-Platform Builds**: AMD64 and ARM64 container support
- **Security Scanning**: Integrated Trivy, bandit, safety, and pip-audit
- **CycloneDX SBOM Generation**: Comprehensive SBOM generation for the project itself
- **Code Quality**: Black formatting, flake8 linting, and pytest testing
- **Production Features**:
  - Hierarchical project management in Dependency-Track
  - GitLab CI/CD pipeline integration
  - API key authentication with multi-key support
  - Federal network deployment templates
  - YAML-based bulk configuration
  - Version cloning with vulnerability preservation

### Changed
- **BREAKING**: Removed ALL SPDX SBOM support - CycloneDX format only
- Updated documentation with production deployment guidance
- Enhanced error handling and logging throughout the application

### Security
- Implemented comprehensive security scanning in CI/CD pipeline
- Added SARIF security report uploads to GitHub Security tab
- Enhanced container security with multi-stage builds
- Dependency vulnerability scanning with multiple tools

## [1.0.0-rc.1] through [1.0.0-rc.25] - 2025-09-17

### Development Releases
- Iterative development and testing of CI/CD pipeline
- Resolution of GitHub Actions workflow issues
- Fix of package building and publishing problems
- Migration from SPDX to CycloneDX-only SBOM generation
- Security scanning integration and optimization

---

## Release Notes

### Unreleased (v1.1.0) Highlights
**Major organizational structure implementation** with complete team management:
- **🏢 Enterprise Team Management**: 24 teams with 131 project assignments based on organizational hierarchy
- **🔑 Native DT Authentication**: Direct integration with Dependency-Track API keys, eliminating separate key management
- **🛡️ Portfolio Access Control**: Complete granular access control with role-based team permissions
- **📊 Federal Structure Ready**: STLS organizational structure with 3 districts, 7 business lines, 27 projects

### v1.0.2 Highlights
**DockerHub integration** for simplified deployment:
- Pre-built multi-platform container images eliminate local build requirements
- Streamlined docker-compose setup with versioned, reliable deployments

### v1.0.1 Highlights
This patch release focuses on fixing PyPI publishing issues and ensuring reliable automated deployments.

### v1.0.0 Highlights
The first production release of SBOM Upload Validator brings enterprise-ready features:

- **🚀 Production Ready**: Complete CI/CD automation with security scanning
- **📦 Multi-Platform**: PyPI packages and Docker containers for AMD64/ARM64
- **🔐 Security First**: Comprehensive vulnerability scanning and static analysis
- **📋 CycloneDX Only**: Pure CycloneDX SBOM implementation for OWASP Dependency-Track
- **🏛️ Federal Ready**: Government and enterprise deployment templates
- **🔗 GitLab Integration**: Native CI/CD pipeline support with rich metadata

### Upgrade Notes

#### From rc.25 to 1.0.0
- No breaking changes - direct upgrade supported
- All configuration remains compatible

#### SPDX Removal (rc.25)
- **BREAKING CHANGE**: SPDX SBOM support completely removed
- Only CycloneDX SBOMs are generated and processed
- Update any scripts or workflows that depended on SPDX output

### Installation

#### PyPI (Recommended)
```bash
# Latest stable release
pip install sbom-upload-validator==1.0.2

# Upcoming release with organizational features (when available)
pip install sbom-upload-validator==1.1.0
```

#### Docker
```bash
# Latest stable release
docker pull stljim/sbom-upload-validator:1.0.2

# Use latest tag for most recent
docker pull stljim/sbom-upload-validator:latest
```

### Support

- **Documentation**: See README.md and CLAUDE.md for detailed guidance
- **Issues**: Report bugs via GitHub Issues
- **Security**: Contact maintainers for security vulnerabilities