"""AI-ORG: AWS Organization management CLI with Control Tower integration.

This package provides a comprehensive command-line interface for managing AWS Organizations
with AWS Control Tower. It automates account creation, SSO permission assignment, and
StackSet deployment monitoring for Control Tower organizations.

Key Features:
    - Automated account creation with proper OU placement
    - SSO permission management and assignment
    - StackSet deployment monitoring and status checking
    - Configuration management with caching
    - Enterprise-grade DevOps automation

Example:
    Basic usage example::

        >>> from ai_org.cli import cli
        >>> # Use CLI commands: ai-org account create, ai-org sso assign, etc.

Modules:
    cli: Main CLI entry point and command routing
    commands: Command implementations for account, SSO, StackSet, and config management
    core: Core business logic and AWS service managers
    utils: Utility functions for caching, output formatting, and validation

Attributes:
    __version__: Package version string
"""

__version__ = "0.1.0"
