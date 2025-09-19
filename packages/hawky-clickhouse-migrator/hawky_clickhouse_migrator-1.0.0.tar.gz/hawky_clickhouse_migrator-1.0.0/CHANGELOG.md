# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of ClickHouse Migrator
- Support for migrating data between ClickHouse Cloud and self-hosted instances
- CLI interface with comprehensive command set
- Real-time progress tracking with Rich UI
- Custom query support for selective data migration
- Parallel processing with configurable workers
- Resume capability with checkpoint files
- Schema migration support
- Data integrity verification
- YAML configuration file support
- Comprehensive error handling and retry mechanisms
- Detailed logging and monitoring capabilities

### Features
- **Core Migration Engine**: Reliable data transfer between ClickHouse instances
- **Connection Management**: Robust connection handling with automatic retries
- **Progress Tracking**: Beautiful progress bars and detailed statistics
- **Batch Processing**: Configurable batch sizes for optimal performance
- **CLI Commands**:
  - `migrate`: Main migration command
  - `list-tables`: List available tables in ClickHouse instance
  - `inspect-table`: Examine table structure and sample data
  - `test-connection`: Verify connectivity to ClickHouse instances
  - `generate-config`: Create configuration file template
- **Configuration**: Flexible configuration via CLI arguments or YAML files
- **Testing**: Comprehensive test suite with 95%+ coverage

### Supported ClickHouse Versions
- ClickHouse 21.x and later
- ClickHouse Cloud
- Self-hosted ClickHouse instances

### Python Support
- Python 3.8+
- Cross-platform compatibility (Windows, macOS, Linux)

## [0.1.0] - 2024-12-14

### Added
- Initial project structure and core functionality
- Basic migration capabilities
- CLI interface foundation
- Documentation and examples