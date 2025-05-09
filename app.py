#!/usr/bin/env python3
"""
Main application entry point for myproject template.
This file demonstrates how to use the myproject package with proper error
handling and logging.
"""
import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, Any, Optional

# Configure logging first so we can log import errors
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("myproject")

# Try to add the src directory to the Python path if needed
try:
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    if os.path.exists(src_path) and src_path not in sys.path:
        logger.debug("Adding %s to Python path", src_path)
        sys.path.insert(0, src_path)
        logger.debug("Python path is now: %s", sys.path)
except (OSError, json.JSONDecodeError) as e:
    logger.error("Error adjusting Python path: %s", e)

# Try to import the package
try:
    import requests
except ImportError as e:
    logger.critical("Failed to import requests: %s", e)
    logger.debug("Make sure requests is installed: pip install requests")
    sys.exit(1)

# Try to import from the myproject package
try:
    from myproject import hello
    logger.debug("Successfully imported hello from myproject")
except ImportError as e:
    logger.critical(f"Failed to import from myproject: {e}")
    logger.debug("This could be because:")
    logger.debug("1. The package is not installed (run: pip install -e .)")
    logger.debug("2. The src directory is not in the Python path")
    logger.debug("3. The package structure has changed")
    logger.debug(f"Current Python path: {sys.path}")
    
    # Try a fallback for development
    try:
        logger.debug("Attempting fallback import...")
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from src.myproject import hello
        logger.debug("Fallback import successful")
    except ImportError as fallback_error:
        logger.critical("Fallback import also failed: %s", fallback_error)
        logger.debug("You may need to install the package: pip install -e .")
        sys.exit(1)

# Now that logging is set up and imports are handled, we can continue

# Constants
DEFAULT_API_URL = "https://httpbin.org/get"
CONFIG_FILE = "config.json"


def load_config(config_path: str = CONFIG_FILE) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration values
    """
    try:
        logger.debug("Attempting to load config from %s", config_path)
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                logger.info(f"Successfully loaded config from {config_path}")
                return json.load(f)
        else:
            logger.warning(
                f"Config file {config_path} not found, using defaults"
            )
            return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing config file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading config: {e}")
        return {}


def make_api_request(
    url: str, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Make an API request with error handling and logging.
    
    Args:
        url: The API endpoint URL
        params: Optional query parameters
        
    Returns:
        API response as a dictionary
    """
    start_time = time.time()
    logger.info(f"Making API request to {url}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        elapsed = time.time() - start_time
        logger.debug(f"Request completed in {elapsed:.2f} seconds")
        
        # Log different response codes appropriately
        if response.status_code == 200:
            logger.info(f"API request successful: {response.status_code}")
        elif response.status_code >= 400 and response.status_code < 500:
            logger.warning(f"API client error: {response.status_code}")
        elif response.status_code >= 500:
            logger.error(f"API server error: {response.status_code}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {e}")
        logger.debug("Network connectivity issue or invalid URL")
        raise
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timed out: {e}")
        logger.debug("API endpoint is taking too long to respond")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing API response: {e}")
        logger.debug("API returned invalid JSON")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during API request: {e}")
        raise


def main():
    """Main application entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description="myproject CLI application")
    parser.add_argument(
        "--url", default=DEFAULT_API_URL, help="API URL to query"
    )
    parser.add_argument(
        "--config", default=CONFIG_FILE, help="Path to config file"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    try:
        # Log package import status
        logger.debug("Checking myproject package import")
        message = hello()
        logger.info(f"Package import successful: {message}")
        
        # Load configuration
        config = load_config(args.config)
        
        # Make API request
        url = config.get("api_url", args.url)
        logger.debug(f"Using API URL: {url}")
        
        response = make_api_request(url)
        print(json.dumps(response, indent=2))
        
        logger.info("Application completed successfully")
        return 0
    
    except ImportError as e:
        logger.critical(f"Package import error: {e}")
        logger.debug("Check that the package is installed correctly")
        return 1
    except Exception as e:
        logger.critical(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())