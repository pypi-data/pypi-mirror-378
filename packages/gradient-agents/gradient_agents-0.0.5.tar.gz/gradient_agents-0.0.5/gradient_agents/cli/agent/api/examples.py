"""Example usage of the Galileo traces API services.

This file demonstrates how to use the API services in different scenarios.
It's not meant to be imported, just for reference and testing.
"""

import asyncio
import os
from typing import Optional

from . import (
    ApiServiceFactory,
    TraceRequest,
    TraceStatus,
    TracesService,
)


async def example_basic_usage():
    """Example of basic traces service usage."""
    # Option 1: Create service with explicit token
    api_token = "your_digitalocean_api_token_here"
    traces_service = ApiServiceFactory.create_digitalocean_traces_service(api_token)

    try:
        # Create a new trace
        trace_request = TraceRequest(
            name="My Test Trace",
            description="Testing the traces API",
            metadata={"environment": "development", "version": "1.0.0"},
            tags=["test", "api", "development"],
        )

        print("Creating trace...")
        new_trace = await traces_service.create_trace(trace_request)
        print(f"Created trace: {new_trace.id} - {new_trace.name}")

        # Get traces token
        print("Getting traces token...")
        token_response = await traces_service.get_traces_token(new_trace.id)
        print(f"Traces token: {token_response.token[:20]}...")

        # List all traces
        print("Listing traces...")
        traces = await traces_service.list_traces(limit=10)
        print(f"Found {len(traces)} traces")

        # Update the trace
        print("Updating trace...")
        updated_trace = await traces_service.update_trace(
            new_trace.id, description="Updated description via API"
        )
        print(f"Updated trace: {updated_trace.description}")

        # Get specific trace
        print("Getting trace by ID...")
        retrieved_trace = await traces_service.get_trace(new_trace.id)
        if retrieved_trace:
            print(
                f"Retrieved trace: {retrieved_trace.name} (status: {retrieved_trace.status.value})"
            )

        # Delete the trace (optional)
        # print("Deleting trace...")
        # deleted = await traces_service.delete_trace(new_trace.id)
        # print(f"Trace deleted: {deleted}")

    finally:
        # Always clean up HTTP resources
        await traces_service.http_client.close()


async def example_with_environment_variables():
    """Example using environment variables for configuration."""
    # Option 2: Create service from environment variables
    # Set these environment variables:
    # DO_API_TOKEN=your_token_here
    # DO_API_BASE_URL=https://api.digitalocean.com/v2/ (optional)

    try:
        traces_service = ApiServiceFactory.create_digitalocean_traces_service_from_env(
            token_env_var="DO_API_TOKEN", base_url_env_var="DO_API_BASE_URL"
        )

        # List traces with filtering
        development_traces = await traces_service.list_traces(
            limit=5, status=TraceStatus.COMPLETED, tags=["development"]
        )

        print(f"Found {len(development_traces)} development traces")

        for trace in development_traces:
            print(f"- {trace.name} ({trace.id}) - {trace.status.value}")

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Make sure to set the DO_API_TOKEN environment variable")

    finally:
        # Clean up resources
        if "traces_service" in locals():
            await traces_service.http_client.close()


async def example_error_handling():
    """Example demonstrating error handling."""
    api_token = "invalid_token"
    traces_service = ApiServiceFactory.create_digitalocean_traces_service(api_token)

    try:
        # This should fail with authentication error
        traces = await traces_service.list_traces()
        print(f"Unexpectedly got {len(traces)} traces")

    except Exception as e:
        print(f"Expected error occurred: {e}")

    finally:
        await traces_service.http_client.close()


async def main():
    """Run all examples."""
    print("=== Galileo Traces API Examples ===\n")

    print("1. Basic Usage Example:")
    # Uncomment to test with real token:
    # await example_basic_usage()
    print("Skipped (provide real API token to test)\n")

    print("2. Environment Variables Example:")
    # await example_with_environment_variables()
    print("Skipped (set DO_API_TOKEN environment variable to test)\n")

    print("3. Error Handling Example:")
    await example_error_handling()
    print()


if __name__ == "__main__":
    asyncio.run(main())
