"""
Access rule management for Manus AI Clone
Implements comprehensive access control rule handling
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Callable

from security.permission_validator import PermissionValidator, SecurityContext, PermissionLevel
from security.access_rule import AccessRule

class RulePriority(Enum):
    """Rule priority levels for conflict resolution"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class RuleConditionType(Enum):
    """Types of rule conditions"""
    TIME_BASED = "time_based"
    IP_BASED = "ip_based"
    ROLE_BASED = "role_based"
    CONTEXTUAL = "contextual"
    CUSTOM = "custom"


class RuleAction(Enum):
    """Actions to take when rule matches"""
    ALLOW = "allow"
    DENY = "deny"
    AUDIT = "audit"
    CHALLENGE = "challenge"


class AccessRule:
    """
    Represents an access control rule
    """
    def __init__(self, 
                 rule_id: str,
                 description: str,
                 resource_type: str,
                 required_permission: PermissionLevel,
                 conditions: Dict[str, Any] = None):
        self.rule_id = rule_id
        self.description = description
        self.resource_type = resource_type
        self.required_permission = required_permission
        self.conditions = conditions or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary representation"""
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "resource_type": self.resource_type,
            "required_permission": self.required_permission.value,
            "conditions": self.conditions,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class AccessRuleManager:
    """
    Manages access control rules with priority and condition handling
    """
    def __init__(self):
        # Rule storage
        self.rules = {}  # type: Dict[str, AccessRule]
        
        # Rule categorization
        self.rules_by_type = {}  # type: Dict[RuleConditionType, List[AccessRule]]
        self.rules_by_resource = {}  # type: Dict[str, List[AccessRule]]
        
        # Default rule settings
        self.default_action = RuleAction.DENY
        self.default_priority = RulePriority.MEDIUM

    def create_rule(self, 
                   resource_type: str,
                   required_permission: PermissionLevel,
                   description: str = "",
                   action: RuleAction = RuleAction.DENY,
                   conditions: Optional[Dict[str, Any]] = None,
                   priority: RulePriority = RulePriority.MEDIUM) -> str:
        """
        Create a new access control rule
        
        Args:
            resource_type: Type of resource to apply rule to
            required_permission: Required permission level
            description: Description of the rule
            action: Action to take when rule matches
            conditions: Additional conditions
            priority: Rule priority for conflict resolution
            
        Returns:
            ID of created rule
        """
        # Generate rule ID
        rule_id = str(uuid.uuid4())
        
        # Create rule
        rule = AccessRule(
            rule_id=rule_id,
            description=f"{description} (auto-created)",
            resource_type=resource_type,
            required_permission=required_permission,
            conditions=conditions or {}
        )
        
        # Store rule
        self.add_rule(rule)
        
        return rule_id

    def add_rule(self, rule: AccessRule) -> None:
        """
        Add an existing access rule
        
        Args:
            rule: Rule to add
        """
        # Store in main rule set
        self.rules[rule.rule_id] = rule
        
        # Categorize by type
        rule_type = self._determine_rule_type(rule)
        if rule_type not in self.rules_by_type:
            self.rules_by_type[rule_type] = []
        self.rules_by_type[rule_type].append(rule)
        
        # Categorize by resource
        if rule.resource_type not in self.rules_by_resource:
            self.rules_by_resource[rule.resource_type] = []
        self.rules_by_resource[rule.resource_type].append(rule)

    def _determine_rule_type(self, rule: AccessRule) -> RuleConditionType:
        """
        Determine the type of a rule based on its conditions
        
        Args:
            rule: Rule to evaluate
            
        Returns:
            Determined rule type
        """
        # Check for time-based conditions
        if "time_restriction" in rule.conditions:
            return RuleConditionType.TIME_BASED
            
        # Check for IP address conditions
        if "ip_whitelist" in rule.conditions or "ip_blacklist" in rule.conditions:
            return RuleConditionType.IP_BASED
            
        # Check for role conditions
        if "required_roles" in rule.conditions:
            return RuleConditionType.ROLE_BASED
            
        # Check for contextual conditions
        if "context_conditions" in rule.conditions:
            return RuleConditionType.CONTEXTUAL
            
        # Default to custom
        return RuleConditionType.CUSTOM

    def get_rules(self, 
                 resource_type: Optional[str] = None,
                 rule_type: Optional[RuleConditionType] = None) -> List[AccessRule]:
        """
        Get matching access rules
        
        Args:
            resource_type: Filter by resource type
            rule_type: Filter by rule type
            
        Returns:
            List of matching rules
        """
        # Start with all rules
        result = list(self.rules.values())
        
        # Filter by resource type
        if resource_type:
            result = [r for r in result if r.resource_type == resource_type]
            
        # Filter by rule type
        if rule_type:
            filtered = []
            for r in result:
                # Need to check actual conditions if no type mapping
                if rule_type == RuleConditionType.CUSTOM:
                    if self._determine_rule_type(r) == rule_type:
                        filtered.append(r)
                else:
                    # Use pre-categorized rules
                    filtered.extend([r for t, rules in self.rules_by_type.items() 
                                    if t == rule_type for rule in rules])
            result = filtered
            
        return result

    def update_rule(self, 
                   rule_id: str,
                   updates: Dict[str, Any]) -> bool:
        """
        Update an existing access rule
        
        Args:
            rule_id: ID of rule to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        # Check if rule exists
        if rule_id not in self.rules:
            return False
            
        # Update rule properties
        rule = self.rules[rule_id]
        
        # Apply updates
        if "description" in updates:
            rule.description = updates["description"]
        if "resource_type" in updates:
            # Remove from old resource category
            old_resource = rule.resource_type
            if old_resource in self.rules_by_resource:
                self.rules_by_resource[old_resource] = [
                    r for r in self.rules_by_resource[old_resource] 
                    if r.rule_id != rule_id
                ]
                if not self.rules_by_resource[old_resource]:
                    del self.rules_by_resource[old_resource]
            
            # Add to new resource category
            new_resource = updates["resource_type"]
            if new_resource not in self.rules_by_resource:
                self.rules_by_resource[new_resource] = []
            self.rules_by_resource[new_resource].append(rule)
            rule.resource_type = new_resource
            
        if "required_permission" in updates:
            try:
                rule.required_permission = PermissionLevel(updates["required_permission"])
            except ValueError:
                return False
            
        if "conditions" in updates:
            rule.conditions = updates["conditions"]
            
        # Update type categorization
        old_type = self._determine_rule_type(rule)
        new_type = self._determine_rule_type(rule)
        if old_type != new_type:
            # Remove from old type category
            if old_type in self.rules_by_type:
                self.rules_by_type[old_type] = [
                    r for r in self.rules_by_type[old_type] 
                    if r.rule_id != rule_id
                ]
                if not self.rules_by_type[old_type]:
                    del self.rules_by_type[old_type]
            
            # Add to new type category
            if new_type not in self.rules_by_type:
                self.rules_by_type[new_type] = []
            self.rules_by_type[new_type].append(rule)
            
        return True

    def delete_rule(self, rule_id: str) -> bool:
        """
        Delete an access control rule
        
        Args:
            rule_id: ID of rule to delete
            
        Returns:
            True if successful
        """
        # Check if rule exists
        if rule_id not in self.rules:
            return False
            
        # Get rule for categorization info
        rule = self.rules[rule_id]
        old_type = self._determine_rule_type(rule)
        
        # Remove from main rule set
        del self.rules[rule_id]
        
        # Remove from type categorization
        if old_type in self.rules_by_type:
            self.rules_by_type[old_type] = [
                r for r in self.rules_by_type[old_type] 
                if r.rule_id != rule_id
            ]
            if not self.rules_by_type[old_type]:
                del self.rules_by_type[old_type]
                
        # Remove from resource categorization
        if rule.resource_type in self.rules_by_resource:
            self.rules_by_resource[rule.resource_type] = [
                r for r in self.rules_by_resource[rule.resource_type] 
                if r.rule_id != rule_id
            ]
            if not self.rules_by_resource[rule.resource_type]:
                del self.rules_by_resource[rule.resource_type]
                
        return True

    def validate_access(self, 
                       context: SecurityContext,
                       resource_type: str,
                       required_permission: PermissionLevel) -> bool:
        """
        Validate access using all applicable rules
        
        Args:
            context: Security context
            resource_type: Type of resource being accessed
            required_permission: Required permission level
            
        Returns:
            True if access is allowed
        """
        # Get all rules for this resource type
        applicable_rules = self.get_rules(resource_type)
        
        # Sort rules by priority
        sorted_rules = sorted(
            applicable_rules,
            key=lambda r: self._get_rule_priority(r).value
        )
        
        # Apply each rule
        for rule in sorted_rules:
            # Skip if rule doesn't match conditions
            if not self._check_conditions(rule, context):
                continue
                
            # Return based on permission level
            if rule.required_permission.value <= required_permission.value:
                return True
            
        # If no rule allows access, deny it
        return False

    def _get_rule_priority(self, rule: AccessRule) -> RulePriority:
        """
        Determine priority for a rule (can be extended with more logic)
        
        Args:
            rule: Rule to evaluate
            
        Returns:
            Priority level
        """
        # Simple default priority based on rule type
        rule_type = self._determine_rule_type(rule)
        if rule_type == RuleConditionType.TIME_BASED:
            return RulePriority.HIGH
        elif rule_type == RuleConditionType.IP_BASED:
            return RulePriority.HIGH
        elif rule_type == RuleConditionType.ROLE_BASED:
            return RulePriority.MEDIUM
        else:
            return RulePriority.LOW

    def _check_conditions(self, 
                        rule: AccessRule,
                        context: SecurityContext) -> bool:
        """
        Check additional conditions for a rule
        
        Args:
            rule: Access rule
            context: Security context
            
        Returns:
            True if conditions are satisfied
        """
        # No conditions means unconditional access
        if not rule.conditions:
            return True
            
        # Time-based restrictions
        if "time_restriction" in rule.conditions:
            current_hour = datetime.now().hour
            allowed_hours = rule.conditions["time_restriction"].split("-")
            if len(allowed_hours) == 2:
                start_hour, end_hour = map(int, allowed_hours)
                if not (start_hour <= current_hour < end_hour):
                    return False
            
        # IP address condition
        if "ip_whitelist" in rule.conditions:
            if context.ip_address not in rule.conditions["ip_whitelist"]:
                return False
                
        # Role requirements
        if "required_roles" in rule.conditions:
            matched = False
            for role in context.roles:
                if role in rule.conditions["required_roles"]:
                    matched = True
                    break
            if not matched:
                return False
                
        # Contextual conditions
        if "context_conditions" in rule.conditions:
            context_dict = context.to_dict()
            for key, value in rule.conditions["context_conditions"].items():
                if key not in context_dict or context_dict[key] != value:
                    return False
            
        return True

    def _check_time_restrictions(self, rule: AccessRule) -> bool:
        """
        Check time-based restrictions for a rule
        
        Args:
            rule: Access rule
            
        Returns:
            True if within allowed time
        """
        if "time_restriction" not in rule.conditions:
            return True
            
        current_hour = datetime.now().hour
        allowed_hours = rule.conditions["time_restriction"].split("-")
        if len(allowed_hours) == 2:
            start_hour, end_hour = map(int, allowed_hours)
            return start_hour <= current_hour < end_hour
            
        return True

    def _check_ip_restrictions(self, rule: AccessRule, context: SecurityContext) -> bool:
        """
        Check IP address restrictions for a rule
        
        Args:
            rule: Access rule
            context: Security context
            
        Returns:
            True if IP address is allowed
        """
        if "ip_whitelist" in rule.conditions:
            return context.ip_address in rule.conditions["ip_whitelist"]
            
        if "ip_blacklist" in rule.conditions:
            return context.ip_address not in rule.conditions["ip_blacklist"]
            
        return True

    def _check_role_requirements(self, rule: AccessRule, context: SecurityContext) -> bool:
        """
        Check role requirements for a rule
        
        Args:
            rule: Access rule
            context: Security context
            
        Returns:
            True if roles are satisfied
        """
        if "required_roles" in rule.conditions:
            matched = False
            for role in context.roles:
                if role in rule.conditions["required_roles"]:
                    matched = True
                    break
            return matched
            
        return True

    def _check_context_conditions(self, rule: AccessRule, context: SecurityContext) -> bool:
        """
        Check contextual conditions for a rule
        
        Args:
            rule: Access rule
            context: Security context
            
        Returns:
            True if conditions are satisfied
        """
        if "context_conditions" in rule.conditions:
            context_dict = context.to_dict()
            for key, value in rule.conditions["context_conditions"].items():
                if key not in context_dict or context_dict[key] != value:
                    return False
            
        return True

    def _check_custom_conditions(self, rule: AccessRule, context: SecurityContext) -> bool:
        """
        Check custom conditions for a rule
        
        Args:
            rule: Access rule
            context: Security context
            
        Returns:
            True if conditions are satisfied
        """
        # This would implement custom condition checking
        return True

    def get_rule_status(self) -> Dict[str, Any]:
        """Get status information about configured rules"""
        # Calculate statistics
        total_rules = len(self.rules)
        
        # Count by type
        type_counts = {t.value: len(rules) for t, rules in self.rules_by_type.items()}
        
        # Count by resource
        resource_counts = {r: len(rules) for r, rules in self.rules_by_resource.items()}
        
        return {
            "total_rules": total_rules,
            "rules_by_type": type_counts,
            "rules_by_resource": resource_counts,
            "default_action": self.default_action.value,
            "default_priority": self.default_priority.value
        }