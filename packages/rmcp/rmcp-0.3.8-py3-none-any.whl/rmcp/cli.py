"""
Command-line interface for RMCP MCP Server.

Provides entry points for running the server with different transports
and configurations, following the principle of "multiple deployment targets."
"""

import asyncio
import logging
import sys
from pathlib import Path
# Modern Python 3.10+ syntax for type hints

import click

from . import __version__
from .core.server import create_server
from .registries.prompts import (
    model_diagnostic_prompt,
    register_prompt_functions,
    statistical_workflow_prompt,
)
from .registries.resources import ResourcesRegistry
from .registries.tools import register_tool_functions
from .transport.stdio import StdioTransport

# Configure logging to stderr only
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=__version__)
def cli():
    """RMCP MCP Server - Comprehensive statistical analysis with 40 tools across 9 categories."""
    pass


@cli.command()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level",
)
def start(log_level: str):
    """Start RMCP MCP server (default stdio transport)."""

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, log_level))

    logger.info("Starting RMCP MCP Server")

    try:
        # Create and configure server
        server = create_server()
        config = {"allowed_paths": [str(Path.cwd())], "read_only": True}
        server.configure(**config)

        # Register built-in statistical tools
        _register_builtin_tools(server)

        # Register built-in prompts
        register_prompt_functions(
            server.prompts, statistical_workflow_prompt, model_diagnostic_prompt
        )

        # Set up stdio transport
        transport = StdioTransport()
        transport.set_message_handler(server.handle_request)

        # Run the server
        asyncio.run(transport.run())

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--allowed-paths",
    multiple=True,
    help="Allowed file system paths (can be specified multiple times)",
)
@click.option(
    "--cache-root", type=click.Path(), help="Root directory for content caching"
)
@click.option(
    "--read-only/--read-write",
    default=True,
    help="File system access mode (default: read-only)",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level",
)
@click.option(
    "--config-file", type=click.Path(exists=True), help="Configuration file path"
)
def serve(
    allowed_paths: list[str],
    cache_root: str | None,
    read_only: bool,
    log_level: str,
    config_file: str | None,
):
    """Run MCP server with advanced configuration options."""

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, log_level))

    logger.info("Starting RMCP MCP Server")

    try:
        # Load configuration
        config = _load_config(config_file) if config_file else {}

        # Override with CLI options
        if allowed_paths:
            config["allowed_paths"] = list(allowed_paths)
        if cache_root:
            config["cache_root"] = cache_root
        config["read_only"] = read_only

        # Set defaults if not specified
        if "allowed_paths" not in config:
            config["allowed_paths"] = [str(Path.cwd())]

        # Create and configure server
        server = create_server()
        server.configure(**config)

        # Register built-in statistical tools
        _register_builtin_tools(server)

        # Register built-in prompts
        register_prompt_functions(
            server.prompts, statistical_workflow_prompt, model_diagnostic_prompt
        )

        # Set up stdio transport
        transport = StdioTransport()
        transport.set_message_handler(server.handle_request)

        # Run the server
        asyncio.run(transport.run())

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


@cli.command()
@click.option("--host", default="localhost", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--allowed-paths", multiple=True, help="Allowed file system paths")
@click.option("--cache-root", help="Cache root directory")
def serve_http(host: str, port: int, allowed_paths: tuple[str, ...], cache_root: str | None):
    """Run MCP server over HTTP transport (requires fastapi extras)."""
    try:
        from .transport.http import HTTPTransport
    except ImportError:
        click.echo(
            "HTTP transport requires 'fastapi' extras. Install with: pip install rmcp[http]"
        )
        sys.exit(1)

    logger.info(f"Starting HTTP transport on {host}:{port}")
    
    # Create and configure server
    server = create_server()
    _register_builtin_tools(server)
    
    # Create HTTP transport
    transport = HTTPTransport(host=host, port=port)
    transport.set_message_handler(server.handle_request)
    
    click.echo(f"🚀 RMCP HTTP server starting on http://{host}:{port}")
    click.echo(f"📊 Available tools: {len(server.tools._tools)}")
    click.echo(f"🔗 Endpoints:")
    click.echo(f"   • POST http://{host}:{port}/ (JSON-RPC requests)")
    click.echo(f"   • GET  http://{host}:{port}/sse (Server-Sent Events)")
    click.echo(f"   • GET  http://{host}:{port}/health (Health check)")
    
    try:
        asyncio.run(transport.run())
    except KeyboardInterrupt:
        click.echo("\n👋 Shutting down HTTP server")
    except Exception as e:
        logger.error(f"HTTP server error: {e}")
        sys.exit(1)


@cli.command()
@click.option("--allowed-paths", multiple=True, help="Allowed file system paths")
@click.option("--output", type=click.Path(), help="Output file for capabilities")
def list_capabilities(allowed_paths: list[str], output: str | None):
    """List server capabilities (tools, resources, prompts)."""

    # Create server to inspect capabilities
    server = create_server()
    if allowed_paths:
        server.configure(allowed_paths=list(allowed_paths))

    _register_builtin_tools(server)
    register_prompt_functions(
        server.prompts, statistical_workflow_prompt, model_diagnostic_prompt
    )

    async def _list():
        from .core.context import Context, LifespanState

        context = Context.create("list", "list", server.lifespan_state)

        # Get capabilities
        tools = await server.tools.list_tools(context)
        resources = await server.resources.list_resources(context)
        prompts = await server.prompts.list_prompts(context)

        capabilities = {
            "server": {
                "name": server.name,
                "version": server.version,
                "description": server.description,
            },
            "tools": tools,
            "resources": resources,
            "prompts": prompts,
        }

        import json

        json_output = json.dumps(capabilities, indent=2)

        if output:
            with open(output, "w") as f:
                f.write(json_output)
            click.echo(f"Capabilities written to {output}")
        else:
            click.echo(json_output)

    asyncio.run(_list())


@cli.command()
def validate_config():
    """Validate server configuration."""
    click.echo("Configuration validation not yet implemented")
    # TODO: Add config validation


@cli.command("check-r-packages")
def check_r_packages():
    """Check R package installation status."""
    import json
    import subprocess

    # Define all required packages with their categories
    packages = {
        "Core Statistical": ["jsonlite", "plm", "lmtest", "sandwich", "AER", "dplyr"],
        "Time Series": ["forecast", "vars", "urca", "tseries"],
        "Statistical Testing": ["nortest", "car"],
        "Machine Learning": ["rpart", "randomForest"],
        "Data Visualization": ["ggplot2", "gridExtra", "tidyr", "rlang"],
    }

    click.echo("🔍 Checking R Package Installation Status")
    click.echo("=" * 50)

    # Check if R is available
    try:
        result = subprocess.run(
            ["R", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            click.echo("❌ R not found. Please install R first.")
            return
        version_line = result.stdout.split("\n")[0]
        click.echo(f"✅ R is available: {version_line}")
    except Exception as e:
        click.echo(f"❌ R check failed: {e}")
        return

    click.echo()

    # Check each package category
    all_packages = []
    missing_packages = []

    for category, pkg_list in packages.items():
        click.echo(f"📦 {category} Packages:")
        for pkg in pkg_list:
            all_packages.append(pkg)
            try:
                # Check if package is installed
                r_cmd = f'if (require("{pkg}", quietly=TRUE)) cat("INSTALLED") else cat("MISSING")'
                result = subprocess.run(
                    ["R", "--slave", "-e", r_cmd],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if "INSTALLED" in result.stdout:
                    click.echo(f"   ✅ {pkg}")
                else:
                    click.echo(f"   ❌ {pkg}")
                    missing_packages.append(pkg)
            except Exception:
                click.echo(f"   ❓ {pkg} (check failed)")
                missing_packages.append(pkg)
        click.echo()

    # Summary
    installed_count = len(all_packages) - len(missing_packages)
    click.echo(f"📊 Summary: {installed_count}/{len(all_packages)} packages installed")

    if missing_packages:
        click.echo()
        click.echo("❌ Missing Packages:")
        for pkg in missing_packages:
            click.echo(f"   - {pkg}")

        click.echo()
        click.echo("💡 To install missing packages, run in R:")
        missing_str = '", "'.join(missing_packages)
        click.echo(f'   install.packages(c("{missing_str}"))')

        click.echo()
        click.echo("🚀 Or install all RMCP packages at once:")
        all_str = '", "'.join(all_packages)
        click.echo(
            f'   install.packages(c("{all_str}"), repos="https://cran.rstudio.com/")'
        )
    else:
        click.echo()
        click.echo("🎉 All required R packages are installed!")
        click.echo("✅ RMCP is ready to use!")


def _load_config(config_file: str) -> dict:
    """Load configuration from file."""
    import json

    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config file {config_file}: {e}")
        return {}


def _register_builtin_tools(server):
    """Register built-in statistical tools."""
    from .tools.descriptive import frequency_table, outlier_detection, summary_stats
    from .tools.econometrics import instrumental_variables, panel_regression, var_model
    from .tools.fileops import (
        data_info,
        filter_data,
        read_csv,
        read_excel,
        read_json,
        write_csv,
    )
    from .tools.formula_builder import build_formula, validate_formula
    from .tools.helpers import load_example, suggest_fix, validate_data
    from .tools.machine_learning import decision_tree, kmeans_clustering, random_forest
    from .tools.regression import (
        correlation_analysis,
        linear_model,
        logistic_regression,
    )
    from .tools.statistical_tests import anova, chi_square_test, normality_test, t_test
    from .tools.timeseries import arima_model, decompose_timeseries, stationarity_test
    from .tools.transforms import difference, lag_lead, standardize, winsorize
    from .tools.visualization import (
        boxplot,
        correlation_heatmap,
        histogram,
        regression_plot,
        scatter_plot,
        time_series_plot,
    )

    # Register all statistical tools
    register_tool_functions(
        server.tools,
        # Original regression tools
        linear_model,
        correlation_analysis,
        logistic_regression,
        # Time series analysis
        arima_model,
        decompose_timeseries,
        stationarity_test,
        # Data transformations
        lag_lead,
        winsorize,
        difference,
        standardize,
        # Statistical tests
        t_test,
        anova,
        chi_square_test,
        normality_test,
        # Descriptive statistics
        summary_stats,
        outlier_detection,
        frequency_table,
        # File operations
        read_csv,
        write_csv,
        data_info,
        filter_data,
        read_excel,
        read_json,
        # Econometrics
        panel_regression,
        instrumental_variables,
        var_model,
        # Machine learning
        kmeans_clustering,
        decision_tree,
        random_forest,
        # Visualization
        scatter_plot,
        histogram,
        boxplot,
        time_series_plot,
        correlation_heatmap,
        regression_plot,
        # Natural language tools
        build_formula,
        validate_formula,
        # Helper tools
        suggest_fix,
        validate_data,
        load_example,
    )

    logger.info("Registered comprehensive statistical analysis tools (40 total)")


if __name__ == "__main__":
    cli()
