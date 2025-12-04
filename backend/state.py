"""Agent state definition."""
from typing import Optional, Dict, Any, List
from langgraph.prebuilt.chat_agent_executor import AgentState


class MedicalAgentState(AgentState):
    """Extended state for medical analytics agent."""
    visualization_json: Optional[Dict[str, Any]] = None
    final_response: Optional[Dict[str, Any]] = None
    step_count: int = 0
    found_codes: List[str] = []
    last_sql: Optional[str] = None
