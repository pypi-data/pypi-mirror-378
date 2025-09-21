# src/zerocap/client.py
"""
The official ZerocapClient for interacting with the Zerocap ecosystem.

This client provides a high-level, user-friendly interface for discovering
and running ACP Agents, abstracting away the underlying complexities of
service discovery, asynchronous polling, and result parsing.
"""
import asyncio
import time
from typing import Any, Dict, Optional
import httpx
import uuid
from .daemon import hub_client
from .core.acp.models import AgentRun, Message, Part

class AgentSession:
    """
    A handle to a stateful, long-running session with a specific agent.

    This object is created by `ZerocapClient.start_session()` and should be
    used to send multiple, context-aware requests to the same agent.
    """
    def __init__(self, client: 'ZerocapClient', agent_id: str):
        self._client = client
        self.agent_id = agent_id
        self.session_id: uuid.UUID = uuid.uuid4()
        print(f"CLIENT: Session started for agent '{self.agent_id}' with Session ID: {self.session_id}")

    async def run(
        self,
        capability_name: str,
        prompt: str,
        poll_interval: float = 0.5
    ) -> AgentRun:
        """
        Runs a capability within the context of this session.

        The session ID is automatically included in the request, allowing the
        agent to load its state for this specific conversation.

        Args:
            capability_name: The name of the capability to invoke.
            prompt: The text prompt to send as input.
            poll_interval: The time in seconds between polling requests.

        Returns:
            The final, completed AgentRun Pydantic model.
        """
        # This calls the main client's private run executor, but passes its own session_id
        return await self._client._execute_run(
            agent_id=self.agent_id,
            capability_name=capability_name,
            prompt=prompt,
            poll_interval=poll_interval,
            session_id=self.session_id  # The magic is here!
        )

class ZerocapClient:
    """
    A client for discovering and running agents in the Zerocap ecosystem.
    """
    def __init__(self, timeout: float = 30.0):
        """
        Initializes the ZerocapClient.

        Args:
            timeout: The default timeout in seconds for network requests.
        """
        self._timeout = timeout

    def start_session(self, agent_id: str) -> AgentSession:
        """
        Creates and returns a new session handle for a stateful agent.

        Args:
            agent_id: The unique ID of the agent to start a session with.

        Returns:
            An AgentSession object that can be used to run commands.
        """
        return AgentSession(self, agent_id)

    async def run(
        self,
        agent_id: str,
        capability_name: str,
        prompt: str,
        poll_interval: float = 0.5
    ) -> AgentRun:
        """
        Runs a single, stateless task on an agent.

        This is a convenience method for one-shot requests where no memory
        or context needs to be preserved.
        """
        # Calls the main executor with no session_id
        return await self._execute_run(
            agent_id=agent_id,
            capability_name=capability_name,
            prompt=prompt,
            poll_interval=poll_interval,
            session_id=None
        )

    # --- The private, unified run executor ---
    async def _execute_run(
        self,
        agent_id: str,
        capability_name: str,
        prompt: str,
        poll_interval: float,
        session_id: Optional[uuid.UUID]
    ) -> AgentRun:
        """The core logic for executing any agent run, stateful or stateless."""
        print(f"CLIENT: Running capability '{capability_name}' on agent '{agent_id}' (Session: {session_id or 'Stateless'})")
        
        agent_info = hub_client.discover_acp_agent(agent_id)
        agent_address = agent_info.get("address")
        if not agent_address:
            raise ConnectionError(f"Discovered agent '{agent_id}' but it has no address.")

        base_url = f"{agent_address}/agent"

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            # --- UPDATED: The request body now includes the session_id ---
            run_input = {
                "capability_name": capability_name,
                "input_message": {"role": "user/client", "parts": [{"content_type": "text/plain", "content": prompt}]},
                "session_id": str(session_id) if session_id else None
            }
            
            create_response = await client.post(f"{base_url}/runs", json=run_input)
            create_response.raise_for_status()
            
            run_data = create_response.json()
            run_id = run_data.get("id")
            print(f"CLIENT: Run '{run_id}' created with status '{run_data.get('status')}'.")
            run_url = f"{base_url}/runs/{run_id}"

            start_time = time.time()
            while time.time() - start_time < self._timeout:
                await asyncio.sleep(poll_interval)
                get_response = await client.get(run_url)
                get_response.raise_for_status()
                run_data = get_response.json()
                status = run_data.get("status")
                
                if status in ["completed", "failed", "cancelled"]:
                    break
            else:
                raise TimeoutError(f"Run did not complete within {self._timeout} seconds.")

        final_run = AgentRun.model_validate(run_data)
        if final_run.status != "completed":
            error_msg = final_run.output[0].parts[0].content if final_run.output else "No error message provided."
            raise RuntimeError(f"Agent run finished with status '{final_run.status}': {error_msg}")
            
        print(f"CLIENT: Run '{run_id}' completed successfully.")
        return final_run