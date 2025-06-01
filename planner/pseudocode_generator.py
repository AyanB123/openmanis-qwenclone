"""
Pseudocode generation system for Manus AI Clone
Implements plan-to-code conversion with multiple formats
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
import uuid
from datetime import datetime

from planner.task_planner import ExecutionPlan, ExecutionStep, TaskPriority, PlanStatus

class PseudocodeFormat(Enum):
    """Supported pseudocode formats"""
    NUMBERED = "numbered"
    INDENTED = "indented"
    PLAIN = "plain"
    PYTHON_LIKE = "python-like"
    NATURAL_LANGUAGE = "natural_language"


class PseudocodeStyle(Enum):
    """Pseudocode style preferences"""
    CONCISE = "concise"
    DETAILED = "detailed"
    VERBOSE = "verbose"


class PseudocodeGenerator:
    """
    Generates pseudocode representations of execution plans
    """
    def __init__(self):
        # Formatting rules by language
        self.format_rules = {
            PseudocodeFormat.NUMBERED: self._format_numbered,
            PseudocodeFormat.INDENTED: self._format_indented,
            PseudocodeFormat.PLAIN: self._format_plain,
            PseudocodeFormat.PYTHON_LIKE: self._format_python_like,
            PseudocodeFormat.NATURAL_LANGUAGE: self._format_natural_language
        }
        
        # Default style settings
        self.default_style = PseudocodeStyle.CONCISE
        self.default_format = PseudocodeFormat.NUMBERED

    def generate_pseudocode(self, 
                          plan: ExecutionPlan, 
                          code_format: Optional[PseudocodeFormat] = None,
                          style: Optional[PseudocodeStyle] = None) -> Dict[str, Any]:
        """
        Generate pseudocode representation of a plan
        
        Args:
            plan: Execution plan to convert to pseudocode
            code_format: Format to use (defaults to numbered)
            style: Detail level (defaults to concise)
            
        Returns:
            Dictionary containing pseudocode and metadata
        """
        # Use default format if not specified
        if code_format is None:
            code_format = self.default_format
            
        # Use default style if not specified
        if style is None:
            style = self.default_style
        
        # Generate the pseudocode lines
        pseudocode_lines = self.format_rules[code_format](plan, style)
        
        # Return result with metadata
        return {
            "pseudocode_id": str(uuid.uuid4()),
            "generated_at": datetime.now().isoformat(),
            "format": code_format.value,
            "style": style.value,
            "plan_id": plan.plan_id,
            "task_description": plan.task_description,
            "pseudocode": pseudocode_lines,
            "step_count": len(plan.steps),
            "metadata": {
                "source": "execution_plan",
                "complexity": plan.metadata.estimated_complexity if plan.metadata else 0.5
            }
        }

    def _format_numbered(self, 
                        plan: ExecutionPlan, 
                        style: PseudocodeStyle) -> List[str]:
        """
        Format steps as numbered list
        
        Args:
            plan: Execution plan to format
            style: Detail level
            
        Returns:
            List of pseudocode lines
        """
        lines = []
        for i, step in enumerate(plan.steps, 1):
            line = f"{i}. {step.description}"
            
            # Add tool info if present
            if step.tool_name:
                line += f" [tool: {step.tool_name}]"
                
            # Add parameters if detailed style
            if style == PseudocodeStyle.DETAILED:
                if step.parameters:
                    line += f" (params: {step.parameters})"
                
            # Add priority indicator if verbose
            if style == PseudocodeStyle.VERBOSE:
                line += f" [priority: {TaskPriority(step.priority).name}]"
                
            lines.append(line)
            
        return lines

    def _format_indented(self, 
                        plan: ExecutionPlan, 
                        style: PseudocodeStyle) -> List[str]:
        """
        Format steps as indented blocks
        
        Args:
            plan: Execution plan to format
            style: Detail level
            
        Returns:
            List of pseudocode lines
        """
        lines = ["FUNCTION execute_plan():" if style == PseudocodeStyle.PYTHON_LIKE else "BEGIN PLAN:" ]
        
        for step in plan.steps:
            # Base indent
            line = "    " + step.description
            
            # Add tool info if present
            if step.tool_name:
                line += f" [tool: {step.tool_name}]"
                
            # Add parameters if detailed style
            if style == PseudocodeStyle.DETAILED:
                if step.parameters:
                    line += f" (params: {step.parameters})"
                
            # Add status indicators
            if step.status == PlanStatus.COMPLETED:
                line += " [✓]"
            elif step.status == PlanStatus.FAILED:
                line += " [✗]"
                
            lines.append(line)
            
        lines.append("END PLAN")
        return lines

    def _format_plain(self, 
                     plan: ExecutionPlan, 
                     style: PseudocodeStyle) -> List[str]:
        """
        Format steps as plain text
        
        Args:
            plan: Execution plan to format
            style: Detail level
            
        Returns:
            List of pseudocode lines
        """
        lines = []
        for step in plan.steps:
            line = step.description
            
            # Add tool info if present
            if step.tool_name:
                line += f" [tool: {step.tool_name}]"
                
            # Add status markers
            if step.status == PlanStatus.COMPLETED:
                line += " [completed]"
            elif step.status == PlanStatus.FAILED:
                line += " [failed]"
                
            lines.append(line)
            
        return lines

    def _format_python_like(self, 
                         plan: ExecutionPlan, 
                         style: PseudocodeStyle) -> List[str]:
        """
        Format steps as Python-like pseudocode
        
        Args:
            plan: Execution plan to format
            style: Detail level
            
        Returns:
            List of pseudocode lines
        """
        lines = [
            "def execute_plan():",
            "    " + plan.task_description,
            "    try:",
            "        " + "\n        ".join(
                self._generate_python_steps(plan, style)
            ),
            "    except Exception as e:",
            "        raise"
        ]
        return lines

    def _generate_python_steps(self, 
                             plan: ExecutionPlan, 
                             style: PseudocodeStyle) -> List[str]:
        """
        Generate individual Python-style steps
        
        Args:
            plan: Execution plan to format
            style: Detail level
            
        Returns:
            List of pseudocode lines
        """
        lines = []
        for step in plan.steps:
            line = f"# {step.description}"
            
            # Add tool call if present
            if step.tool_name:
                tool_call = f"result = {step.tool_name}_tool({step.parameters})"
                lines.append(f"    {tool_call}")
                
            # Add status check if verbose
            if style == PseudocodeStyle.VERBOSE:
                status = f"# Status: {PlanStatus(step.status).name}"
                lines.append(f"    {status}")
                
            lines.append(f"    {line}")
            
        return lines

    def _format_natural_language(self, 
                               plan: ExecutionPlan, 
                               style: PseudocodeStyle) -> List[str]:
        """
        Format steps as natural language description
        
        Args:
            plan: Execution plan to format
            style: Detail level
            
        Returns:
            List of pseudocode lines
        """
        lines = [f"Execution plan for: {plan.task_description}" , ""]
        
        for i, step in enumerate(plan.steps, 1):
            line = f"Step {i}: {step.description}"
            
            # Add tool info if present
            if step.tool_name:
                line += f" using {step.tool_name}"
                
            # Add parameters if detailed
            if style == PseudocodeStyle.DETAILED and step.parameters:
                line += f" with parameters: {step.parameters}"
                
            # Add status info
            if step.status != PlanStatus.PENDING:
                line += f" ({PlanStatus(step.status).name.lower()})"
                
            lines.append(line)
            
        # Add summary if verbose
        if style == PseudocodeStyle.VERBOSE:
            lines.extend([
                "",
                f"Total steps: {len(plan.steps)}",
                f"Estimated complexity: {plan.metadata.estimated_complexity if plan.metadata else 'unknown'}"
            ])
            
        return lines

    def set_format_rule(self, 
                       format_type: PseudocodeFormat, 
                       rule: Dict[str, Any]) -> None:
        """
        Set formatting rules for specific languages
        
        Args:
            format_type: Programming language name
            rule: Dictionary of formatting rules
        """
        self.format_rules[format_type] = rule