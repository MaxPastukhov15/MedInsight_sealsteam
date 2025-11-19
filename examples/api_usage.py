"""Examples of using the Medical Analytics API."""

import httpx
import asyncio


BASE_URL = "http://localhost:8000"


async def example_chat() -> None:
    """Example: Chat with AI agent."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/chat",
            json={
                "message": "Какой грипп в СПб сейчас?",
                "user_id": "test_user",
            },
        )
        print("Chat Response:")
        print(response.json())


async def example_analyze() -> None:
    """Example: Analyze disease."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/analyze",
            json={
                "disease_name": "грипп",
                "region": "Санкт-Петербург",
                "days": 7,
            },
        )
        print("Analysis Response:")
        print(response.json())


async def example_forecast() -> None:
    """Example: Forecast disease."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/forecast",
            json={
                "disease_name": "грипп",
                "region": "Санкт-Петербург",
                "forecast_days": 14,
            },
        )
        print("Forecast Response:")
        print(response.json())


async def example_health_check() -> None:
    """Example: Health check."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/health")
        print("Health Check:")
        print(response.json())


async def main() -> None:
    """Run all examples."""
    print("=" * 60)
    print("Medical Analytics API Examples")
    print("=" * 60)

    await example_health_check()
    print()

    await example_chat()
    print()

    await example_analyze()
    print()

    await example_forecast()
    print()


if __name__ == "__main__":
    asyncio.run(main())
