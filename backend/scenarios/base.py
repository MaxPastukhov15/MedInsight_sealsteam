"""Base class for all analytical scenarios."""

from abc import ABC, abstractmethod
from typing import Any, Dict  # , Optional  # noqa: F401 (unused)

from monitoring.logging_config import logger


class Scenario(ABC):
    """Base class for all analytical scenarios."""

    def __init__(self, name: str) -> None:
        """Initialize scenario.

        Args:
            name: Scenario name
        """
        self.name = name
        logger.info("scenario_initialized", name=name)

    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scenario logic.

        Args:
            params: Input parameters

        Returns:
            Scenario results
        """
        pass

    def validate(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters.

        Args:
            params: Parameters to validate

        Returns:
            True if valid, False otherwise
        """
        # Default implementation - override in subclasses
        return True

    async def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run scenario with validation.

        Args:
            params: Input parameters

        Returns:
            Scenario results

        Raises:
            ValueError: If parameters are invalid
        """
        if not self.validate(params):
            logger.error(
                "scenario_validation_failed",
                name=self.name,
                params=params,
            )
            raise ValueError(f"Invalid parameters for {self.name}")

        logger.info(
            "scenario_started",
            name=self.name,
            params=params,
        )

        try:
            result = await self.execute(params)
            logger.info(
                "scenario_completed",
                name=self.name,
                success=True,
            )
            return result
        except Exception as e:
            logger.error(
                "scenario_failed",
                name=self.name,
                error=str(e),
            )
            raise
