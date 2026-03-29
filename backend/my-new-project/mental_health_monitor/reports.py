"""Report generation for orchestrator conclusions."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate markdown reports from orchestrator findings."""
    
    REPORT_DIR = Path("weekly_reports")
    
    @classmethod
    def ensure_report_dir(cls):
        """Create report directory if it doesn't exist."""
        cls.REPORT_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def generate_report(
        cls,
        week_number: int,
        overall_state: str,
        behavioral_output: Dict[str, Any],
        physiological_output: Dict[str, Any],
        context_output: Dict[str, Any],
        language_output: Dict[str, Any],
        orchestrator_output: Dict[str, Any]
    ) -> Path:
        """Generate a comprehensive weekly report.
        
        Args:
            week_number: Week number (1, 2, 3)
            overall_state: Overall state from orchestrator
            behavioral_output: Behavioral agent output
            physiological_output: Physiological agent output
            context_output: Context agent output
            language_output: Language agent output
            orchestrator_output: Orchestrator agent output with reasoning
        
        Returns:
            Path to the generated report file
        """
        cls.ensure_report_dir()
        
        report_path = cls.REPORT_DIR / f"week_{week_number}_report.md"
        
        report_content = cls._build_report_markdown(
            week_number,
            overall_state,
            behavioral_output,
            physiological_output,
            context_output,
            language_output,
            orchestrator_output
        )
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Weekly report saved: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Error generating report for week {week_number}: {e}")
            raise
    
    @classmethod
    def _build_report_markdown(
        cls,
        week_number: int,
        overall_state: str,
        behavioral_output: Dict[str, Any],
        physiological_output: Dict[str, Any],
        context_output: Dict[str, Any],
        language_output: Dict[str, Any],
        orchestrator_output: Dict[str, Any]
    ) -> str:
        """Build the markdown report content.
        
        Args:
            All analysis outputs from agents
        
        Returns:
            Formatted markdown string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Use orchestrator_output as source of truth for overall state
        final_state = orchestrator_output.get('overall_state', overall_state).lower()
        final_support_level = orchestrator_output.get('support_level', 'minimal').upper()
        
        report = f"""# Mental Health Weekly Assessment Report
## Week {week_number}

**Generated:** {timestamp}

---

## Overall Assessment

**Status:** `{final_state.upper()}`

**Support Level:** `{final_support_level}`

### Summary
{orchestrator_output.get('reasoning', 'No analysis available')}

---

## Orchestrator Synthesis

### Primary Concerns
{cls._format_concerns(orchestrator_output.get('primary_concerns', []))}

### Recommended Support Level
**Level:** `{orchestrator_output.get('support_level', 'minimal').upper()}`

### Integrated Analysis & Reasoning
{orchestrator_output.get('reasoning', 'No additional reasoning provided')}

---

## Action Items

{cls._generate_action_items(final_state, orchestrator_output.get('primary_concerns', []))}

---

## Next Steps

1. Review this report and reflect on the findings
2. Consider discussing any concerns with a healthcare professional
3. Track progress towards recommendations in next week's assessment
4. Continue engaging with the support agent for additional guidance

---

**Report Generated:** {timestamp}
**System:** Mental Health Behavioral Monitoring System v0.1.0
"""
        return report
    
    @classmethod
    def _format_metric_summary(cls, metrics: Dict[str, Any]) -> str:
        """Format metric summary as code block."""
        if not metrics:
            return "No metrics available"
        
        lines = []
        for key, value in metrics.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines) if lines else "No metrics available"
    
    @classmethod
    def _format_concerns(cls, concerns: list) -> str:
        """Format primary concerns as markdown list."""
        if not concerns:
            return "No significant concerns identified at this time."
        
        items = []
        for i, concern in enumerate(concerns, 1):
            items.append(f"{i}. {concern}")
        return "\n".join(items)
    
    @classmethod
    def _generate_action_items(cls, overall_state: str, concerns: list) -> str:
        """Generate action items based on state and concerns."""
        items = []
        
        # Base items
        items.append("- Monitor changes in daily routines and energy levels")
        items.append("- Maintain regular sleep schedule and exercise habits")
        
        # State-based items
        if overall_state.lower() in ["watchful", "elevated"]:
            items.append("- Consider reaching out to a healthcare provider if concerns persist")
            items.append("- Practice stress management and mindfulness techniques")
        
        if overall_state.lower() == "elevated":
            items.append("- **Urgent**: Schedule a consultation with a mental health professional")
            items.append("- Increase frequency of check-ins with support system")
        
        # Concern-based items
        if concerns:
            items.append("- Address identified concerns with targeted interventions:")
            for concern in concerns[:2]:  # Top 2 concerns
                items.append(f"  - {concern}")
        
        return "\n".join(items)


def save_weekly_report(
    week_number: int,
    overall_state: str,
    behavioral_output: Dict[str, Any],
    physiological_output: Dict[str, Any],
    context_output: Dict[str, Any],
    language_output: Dict[str, Any],
    orchestrator_output: Dict[str, Any]
) -> Path:
    """Convenience function to save a weekly report.
    
    Args:
        All weekly analysis outputs
    
    Returns:
        Path to generated report
    """
    return ReportGenerator.generate_report(
        week_number,
        overall_state,
        behavioral_output,
        physiological_output,
        context_output,
        language_output,
        orchestrator_output
    )
