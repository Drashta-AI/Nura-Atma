"""LangGraph nodes for mental health monitoring system."""

import json
import logging
from typing import Dict, Any
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from .state import GraphState
from ..llm import LLMFactory, BehavioralAgentPrompt, PhysiologicalAgentPrompt, ContextAgentPrompt
from ..llm import LanguageAgentPrompt, OrchestratorAgentPrompt, ConversationalAgentPrompt
from ..database import get_session, AgentOutput, LanguageAgentOutput, OverallState
from ..logging_utils import get_llm_response_logger
from ..reports import save_weekly_report

logger = logging.getLogger(__name__)
llm_logger = get_llm_response_logger()


def behavioral_agent_node(state: GraphState) -> Dict[str, Any]:
    """Behavioral Signal Agent node.
    
    Args:
        state: Current graph state
    
    Returns:
        Dictionary with behavioral_agent_output
    """
    try:
        llm = LLMFactory.get_llm()
        
        # Get system prompt
        system_prompt = BehavioralAgentPrompt.get_system_prompt(
            state.character_sketch or {},
            state.baseline_metrics or {}
        )
        
        # Get user prompt
        user_prompt = BehavioralAgentPrompt.get_user_prompt(
            state.behavioral_metric_states or {},
            state.week_number
        )
        
        # Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        response_text = response.content.strip()
        llm_logger.info(f"[behavioral_agent] LLM response (week {state.week_number}):\n{response_text}")
        
        # Parse JSON response
        try:
            output_json = json.loads(response_text)
            llm_logger.debug(f"[behavioral_agent] Successfully parsed JSON response")
        except json.JSONDecodeError:
            # Try to extract JSON from response
            llm_logger.warning(f"[behavioral_agent] Failed to parse JSON directly, attempting extraction")
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                output_json = json.loads(json_match.group())
                llm_logger.info(f"[behavioral_agent] Extracted JSON from response")
            else:
                llm_logger.error(f"[behavioral_agent] Could not extract JSON from response")
                output_json = {
                    "overall_state": "normal",
                    "metric_summary": {},
                    "implications": "Unable to parse response",
                    "reasoning": response_text
                }
        
        # Ensure all required fields
        output_json.setdefault("overall_state", "normal")
        output_json.setdefault("metric_summary", {})
        output_json.setdefault("implications", "")
        output_json.setdefault("recommendations", "")
        output_json.setdefault("reasoning", "")
        
        # Save to database
        session = get_session()
        try:
            agent_out = AgentOutput(
                week_number=state.week_number,
                agent_name="behavioral",
                agent_state=output_json.get("overall_state", "normal"),
                metric_states=state.behavioral_metric_states,
                reasoning_json=output_json
            )
            session.add(agent_out)
            session.commit()
        except Exception as e:
            logger.error(f"Error saving behavioral agent output: {e}")
            session.rollback()
        finally:
            session.close()
        
        return {
            "behavioral_agent_output": output_json,
            "processed_agents": ["behavioral"]
        }
    
    except Exception as e:
        logger.error(f"Error in behavioral agent: {e}", exc_info=True)
        return {
            "behavioral_agent_output": {"overall_state": "normal", "reasoning": str(e)},
            "errors": [f"Behavioral agent error: {e}"]
        }


def physiological_agent_node(state: GraphState) -> Dict[str, Any]:
    """Physiological/Energy Agent node.
    
    Args:
        state: Current graph state
    
    Returns:
        Dictionary with physiological_agent_output
    """
    try:
        llm = LLMFactory.get_llm()
        
        # Get system prompt
        system_prompt = PhysiologicalAgentPrompt.get_system_prompt(
            state.character_sketch or {},
            state.baseline_metrics or {}
        )
        
        # Get user prompt
        user_prompt = PhysiologicalAgentPrompt.get_user_prompt(
            state.physiological_metric_states or {},
            state.week_number
        )
        
        # Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        response_text = response.content.strip()
        llm_logger.info(f"[physiological_agent] LLM response (week {state.week_number}):\n{response_text}")
        
        # Parse JSON response
        try:
            output_json = json.loads(response_text)
            llm_logger.debug(f"[physiological_agent] Successfully parsed JSON response")
        except json.JSONDecodeError:
            llm_logger.warning(f"[physiological_agent] Failed to parse JSON directly, attempting extraction")
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                output_json = json.loads(json_match.group())
                llm_logger.info(f"[physiological_agent] Extracted JSON from response")
            else:
                llm_logger.error(f"[physiological_agent] Could not extract JSON from response")
                output_json = {
                    "overall_state": "normal",
                    "energy_assessment": "Unable to parse response",
                    "reasoning": response_text
                }
        
        # Ensure all required fields
        output_json.setdefault("overall_state", "normal")
        output_json.setdefault("energy_assessment", "")
        output_json.setdefault("sleep_quality", "")
        output_json.setdefault("implications", "")
        output_json.setdefault("recommendations", "")
        output_json.setdefault("reasoning", "")
        
        # Save to database
        session = get_session()
        try:
            agent_out = AgentOutput(
                week_number=state.week_number,
                agent_name="physiological",
                agent_state=output_json.get("overall_state", "normal"),
                metric_states=state.physiological_metric_states,
                reasoning_json=output_json
            )
            session.add(agent_out)
            session.commit()
        except Exception as e:
            logger.error(f"Error saving physiological agent output: {e}")
            session.rollback()
        finally:
            session.close()
        
        return {
            "physiological_agent_output": output_json,
            "processed_agents": ["physiological"]
        }
    
    except Exception as e:
        logger.error(f"Error in physiological agent: {e}", exc_info=True)
        return {
            "physiological_agent_output": {"overall_state": "normal", "reasoning": str(e)},
            "errors": [f"Physiological agent error: {e}"]
        }


def context_agent_node(state: GraphState) -> Dict[str, Any]:
    """Context & Environment Agent node.
    
    Args:
        state: Current graph state
    
    Returns:
        Dictionary with context_agent_output
    """
    try:
        llm = LLMFactory.get_llm()
        
        # Get system prompt
        system_prompt = ContextAgentPrompt.get_system_prompt(
            state.character_sketch or {},
            state.baseline_metrics or {}
        )
        
        # Get user prompt
        user_prompt = ContextAgentPrompt.get_user_prompt(
            state.context_metric_states or {},
            state.week_number
        )
        
        # Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        response_text = response.content.strip()
        llm_logger.info(f"[context_agent] LLM response (week {state.week_number}):\n{response_text}")
        
        # Parse JSON response
        try:
            output_json = json.loads(response_text)
            llm_logger.debug(f"[context_agent] Successfully parsed JSON response")
        except json.JSONDecodeError:
            llm_logger.warning(f"[context_agent] Failed to parse JSON directly, attempting extraction")
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                output_json = json.loads(json_match.group())
                llm_logger.info(f"[context_agent] Extracted JSON from response")
            else:
                llm_logger.error(f"[context_agent] Could not extract JSON from response")
                output_json = {
                    "overall_state": "normal",
                    "mobility_assessment": "Unable to parse response",
                    "reasoning": response_text
                }
        
        # Ensure all required fields
        output_json.setdefault("overall_state", "normal")
        output_json.setdefault("mobility_assessment", "")
        output_json.setdefault("location_assessment", "")
        output_json.setdefault("environmental_implications", "")
        output_json.setdefault("recommendations", "")
        output_json.setdefault("reasoning", "")
        
        # Save to database
        session = get_session()
        try:
            agent_out = AgentOutput(
                week_number=state.week_number,
                agent_name="context",
                agent_state=output_json.get("overall_state", "normal"),
                metric_states=state.context_metric_states,
                reasoning_json=output_json
            )
            session.add(agent_out)
            session.commit()
        except Exception as e:
            logger.error(f"Error saving context agent output: {e}")
            session.rollback()
        finally:
            session.close()
        
        return {
            "context_agent_output": output_json,
            "processed_agents": ["context"]
        }
    
    except Exception as e:
        logger.error(f"Error in context agent: {e}", exc_info=True)
        return {
            "context_agent_output": {"overall_state": "normal", "reasoning": str(e)},
            "errors": [f"Context agent error: {e}"]
        }


def language_agent_node(state: GraphState) -> Dict[str, Any]:
    """Language & Expression Agent node.
    
    Args:
        state: Current graph state
    
    Returns:
        Dictionary with language_agent_output
    """
    try:
        llm = LLMFactory.get_llm()
        
        # Get system prompt
        system_prompt = LanguageAgentPrompt.get_system_prompt(
            state.character_sketch or {}
        )
        
        # Get user prompt
        user_prompt = LanguageAgentPrompt.get_user_prompt(
            state.weekly_messages or "No messages available",
            state.week_number
        )
        
        # Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        response_text = response.content.strip()
        llm_logger.info(f"[language_agent] LLM response (week {state.week_number}):\n{response_text}")
        
        # Parse JSON response
        try:
            output_json = json.loads(response_text)
            llm_logger.debug(f"[language_agent] Successfully parsed JSON response")
        except json.JSONDecodeError:
            llm_logger.warning(f"[language_agent] Failed to parse JSON directly, attempting extraction")
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                output_json = json.loads(json_match.group())
                llm_logger.info(f"[language_agent] Extracted JSON from response")
            else:
                llm_logger.error(f"[language_agent] Could not extract JSON from response")
                output_json = {
                    "state": "normal",
                    "sentiment_score": 0.0,
                    "reasoning": response_text
                }
        
        # Ensure all required fields
        output_json.setdefault("state", "normal")
        output_json.setdefault("sentiment_score", 0.0)
        output_json.setdefault("emotional_shift_summary", "")
        output_json.setdefault("tone_observations", "")
        output_json.setdefault("reasoning", "")
        
        # Save to database
        session = get_session()
        try:
            lang_out = LanguageAgentOutput(
                week_number=state.week_number,
                linguistic_state=output_json.get("state", "normal"),
                sentiment_score=float(output_json.get("sentiment_score", 0.0)),
                emotional_shift_summary=output_json.get("emotional_shift_summary", ""),
                reasoning=output_json
            )
            session.add(lang_out)
            session.commit()
        except Exception as e:
            logger.error(f"Error saving language agent output: {e}")
            session.rollback()
        finally:
            session.close()
        
        return {
            "language_agent_output": output_json,
            "processed_agents": ["language"]
        }
    
    except Exception as e:
        logger.error(f"Error in language agent: {e}", exc_info=True)
        return {
            "language_agent_output": {"state": "normal", "reasoning": str(e)},
            "errors": [f"Language agent error: {e}"]
        }


def orchestrator_agent_node(state: GraphState) -> Dict[str, Any]:
    """Central Orchestrator Agent node.
    
    Args:
        state: Current graph state
    
    Returns:
        Dictionary with orchestrator_output and overall_state
    """
    try:
        llm = LLMFactory.get_llm()
        
        # Get system prompt
        system_prompt = OrchestratorAgentPrompt.get_system_prompt(
            state.character_sketch or {}
        )
        
        # Get FULL agent outputs (not just states)
        behavioral_output = state.behavioral_agent_output or {}
        physiological_output = state.physiological_agent_output or {}
        context_output = state.context_agent_output or {}
        language_output = state.language_agent_output or {}
        
        # Get user prompt with full agent outputs
        user_prompt = OrchestratorAgentPrompt.get_user_prompt(
            behavioral_output, physiological_output, context_output, language_output,
            state.week_number
        )
        
        # Log what the orchestrator is receiving
        llm_logger.debug(f"[orchestrator_agent] Receiving from behavioral agent: {behavioral_output}")
        llm_logger.debug(f"[orchestrator_agent] Receiving from physiological agent: {physiological_output}")
        llm_logger.debug(f"[orchestrator_agent] Receiving from context agent: {context_output}")
        llm_logger.debug(f"[orchestrator_agent] Receiving from language agent: {language_output}")
        
        # Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        response_text = response.content.strip()
        llm_logger.info(f"[orchestrator_agent] LLM response (week {state.week_number}):\n{response_text}")
        
        # Parse JSON response
        try:
            output_json = json.loads(response_text)
            llm_logger.debug(f"[orchestrator_agent] Successfully parsed JSON response")
        except json.JSONDecodeError:
            llm_logger.warning(f"[orchestrator_agent] Failed to parse JSON directly, attempting extraction")
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                output_json = json.loads(json_match.group())
                llm_logger.info(f"[orchestrator_agent] Extracted JSON from response")
            else:
                llm_logger.error(f"[orchestrator_agent] Could not extract JSON from response")
                output_json = {
                    "overall_state": "normal",
                    "reasoning": response_text
                }
        
        # Extract agent states from outputs
        behavioral_state = behavioral_output.get('overall_state', 'normal').lower()
        physiological_state = physiological_output.get('overall_state', 'normal').lower()
        context_state = context_output.get('overall_state', 'normal').lower()
        language_state = language_output.get('state', 'normal').lower()
        
        agent_states = [behavioral_state, physiological_state, context_state, language_state]
        
        # Compute overall_state based on agent states if not provided by LLM
        llm_overall_state = output_json.get("overall_state", "").lower()
        
        # Validate and derive overall_state based on agent states (per system prompt rule)
        elevated_count = agent_states.count('elevated')
        watchful_count = agent_states.count('watchful')
        
        if elevated_count >= 2:
            computed_state = "elevated"
        elif watchful_count >= 1 or elevated_count >= 1:
            computed_state = "watchful"
        else:
            computed_state = "normal"
        
        # If LLM didn't provide a state or provided incorrect state, use computed state
        if not llm_overall_state or llm_overall_state == "normal" and computed_state != "normal":
            overall_state = computed_state
            llm_logger.info(f"[orchestrator_agent] Computed overall_state: {overall_state} (agent states: {agent_states})")
        else:
            overall_state = llm_overall_state if llm_overall_state else "normal"
        
        # Update output JSON with validated state
        output_json["overall_state"] = overall_state
        output_json.setdefault("integrated_analysis", "")
        output_json.setdefault("primary_concerns", [])
        output_json.setdefault("support_level", "minimal")
        output_json.setdefault("reasoning", "")
        
        # Save to database
        session = get_session()
        try:
            overall_out = OverallState(
                week_number=state.week_number,
                final_state=overall_state,
                behavioural_state=behavioral_state,
                physiological_state=physiological_state,
                context_state=context_state,
                language_state=language_state,
                orchestrator_reasoning=output_json
            )
            session.add(overall_out)
            session.commit()
        except Exception as e:
            logger.error(f"Error saving orchestrator output: {e}")
            session.rollback()
        finally:
            session.close()
        
        # Generate and save weekly report
        try:
            report_path = save_weekly_report(
                week_number=state.week_number,
                overall_state=overall_state,
                behavioral_output=state.behavioral_agent_output or {},
                physiological_output=state.physiological_agent_output or {},
                context_output=state.context_agent_output or {},
                language_output=state.language_agent_output or {},
                orchestrator_output=output_json
            )
            logger.info(f"Week {state.week_number} report saved: {report_path}")
            llm_logger.info(f"[orchestrator_agent] Week {state.week_number} report generated: {report_path}")
        except Exception as e:
            logger.error(f"Error generating report for week {state.week_number}: {e}")
        
        return {
            "orchestrator_output": output_json,
            "overall_state": overall_state,
            "processed_agents": ["orchestrator"]
        }
    
    except Exception as e:
        logger.error(f"Error in orchestrator agent: {e}", exc_info=True)
        return {
            "orchestrator_output": {"overall_state": "normal", "reasoning": str(e)},
            "overall_state": "normal",
            "errors": [f"Orchestrator error: {e}"]
        }


def conversational_agent_node(state: GraphState) -> Dict[str, Any]:
    """Conversational Support Agent node (always active).
    
    Args:
        state: Current graph state
    
    Returns:
        Dictionary with conversational_message
    """
    try:
        llm = LLMFactory.get_llm()
        
        # Get system prompt
        system_prompt = ConversationalAgentPrompt.get_system_prompt(
            state.character_sketch or {}
        )
        
        # Get language emotional summary
        language_summary = ""
        if state.language_agent_output:
            language_summary = state.language_agent_output.get("emotional_shift_summary", "")
        
        # Get user prompt
        user_prompt = ConversationalAgentPrompt.get_user_prompt(
            state.overall_state or "normal",
            language_summary,
            state.week_number
        )
        
        # Call LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        conversational_message = response.content.strip()
        llm_logger.info(f"[conversational_agent] LLM response (week {state.week_number}):\n{conversational_message}")
        
        # Save to database if overall state is marked
        if state.overall_state:
            session = get_session()
            try:
                overall = session.query(OverallState).filter(
                    OverallState.week_number == state.week_number
                ).first()
                if overall:
                    overall.support_message = conversational_message
                    session.commit()
            except Exception as e:
                logger.error(f"Error updating conversational message: {e}")
                session.rollback()
            finally:
                session.close()
        
        return {
            "conversational_message": conversational_message,
            "processed_agents": ["conversational"]
        }
    
    except Exception as e:
        logger.error(f"Error in conversational agent: {e}", exc_info=True)
        return {
            "conversational_message": "I'm here. How are you feeling? I'd like to hear more.",
            "errors": [f"Conversational agent error: {e}"]
        }
