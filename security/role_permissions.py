"""
Role-based permission system for Manus AI Clone
Implements comprehensive role and permission management
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from security.permission_validator import PermissionValidator, RolePermissions, SecurityContext, PermissionLevel

class UserRole:
    """
    Represents a user role with permissions and inheritance
    """
    def __init__(self, 
                 role_id: str,
                 name: str,
                 description: str = "",
                 parent_roles: Optional[List[str]] = None):
        self.role_id = role_id
        self.name = name
        self.description = description
        self.parent_roles = parent_roles or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert role to dictionary representation"""
        return {
            "role_id": self.role_id,
            "name": self.name,
            "description": self.description,
            "parent_roles": self.parent_roles,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class UserPermission:
    """
    Represents a specific permission that can be granted to roles
    """
    def __init__(self, 
                 permission_id: str,
                 name: str,
                 level: PermissionLevel,
                 resource_type: str,
                 description: str = ""):
        self.permission_id = permission_id
        self.name = name
        self.level = level
        self.resource_type = resource_type
        self.description = description
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert permission to dictionary representation"""
        return {
            "permission_id": self.permission_id,
            "name": self.name,
            "level": self.level.value,
            "resource_type": self.resource_type,
            "description": self.description,
            "created_at": self.created_at
        }


class RoleManager:
    """
    Manages user roles and their permissions
    """
    def __init__(self):
        # Role storage
        self.roles = {}  # type: Dict[str, UserRole]
        self.role_names = {}  # type: Dict[str, str]  # name -> role_id mapping
        
        # Permission storage
        self.permissions = {}  # type: Dict[str, UserPermission]
        
        # Role-to-permission mapping
        self.role_permissions = {}  # type: Dict[str, Dict[str, PermissionLevel]]
        
        # Default roles
        self.default_roles = ["user", "admin"]
        
        # Initialize default roles
        self._initialize_default_roles()

    def _initialize_default_roles(self) -> None:
        """Initialize default system roles"""
        # User role (default)
        user_role = UserRole(
            role_id=str(uuid.uuid4()),
            name="user",
            description="Default user role with basic access"
        )
        self.roles[user_role.role_id] = user_role
        self.role_names[user_role.name] = user_role.role_id
        
        # Admin role
        admin_role = UserRole(
            role_id=str(uuid.uuid4()),
            name="admin",
            description="Administrator role with full access",
            parent_roles=[user_role.role_id]
        )
        self.roles[admin_role.role_id] = admin_role
        self.role_names[admin_role.name] = admin_role.role_id

    def create_role(self, 
                   name: str,
                   description: str = "",
                   parent_roles: Optional[List[str]] = None) -> str:
        """
        Create a new user role
        
        Args:
            name: Name of the role
            description: Description of the role
            parent_roles: List of parent role names
            
        Returns:
            ID of created role
        """
        # Check if role name exists
        if name in self.role_names:
            raise ValueError(f"Role '{name}' already exists")
            
        # Create role
        role_id = str(uuid.uuid4())
        role = UserRole(
            role_id=role_id,
            name=name,
            description=description,
            parent_roles=parent_roles
        )
        
        # Store role
        self.roles[role_id] = role
        self.role_names[name] = role_id
        
        # Initialize role permissions
        self.role_permissions[role_id] = {}
        
        return role_id

    def delete_role(self, role_id: str) -> bool:
        """
        Delete a user role
        
        Args:
            role_id: ID of role to delete
            
        Returns:
            True if successful
        """
        # Check if role exists
        if role_id not in self.roles:
            return False
            
        # Don't allow deleting default roles
        role_name = self.roles[role_id].name
        if role_name in self.default_roles:
            return False
            
        # Remove from roles
        del self.roles[role_id]
        
        # Remove from role names mapping
        role_name = self.roles[role_id].name
        if role_name in self.role_names:
            del self.role_names[role_name]
            
        # Remove role permissions
        if role_id in self.role_permissions:
            del self.role_permissions[role_id]
            
        return True

    def add_permission(self, 
                     role_id: str,
                     resource_type: str,
                     level: PermissionLevel,
                     name: str = "",
                     description: str = "") -> str:
        """
        Add a permission to a role
        
        Args:
            role_id: ID of role to modify
            resource_type: Type of resource
            level: Required permission level
            name: Name of the permission
            description: Description of the permission
            
        Returns:
            ID of created permission
        """
        # Check if role exists
        if role_id not in self.roles:
            raise ValueError(f"Role {role_id} not found")
            
        # Generate permission ID
        permission_id = str(uuid.uuid4())
        
        # Create permission
        permission = UserPermission(
            permission_id=permission_id,
            name=name or f"{resource_type}_{level.name}",
            level=level,
            resource_type=resource_type,
            description=description
        )
        
        # Store permission
        self.permissions[permission_id] = permission
        
        # Update role permissions
        if role_id not in self.role_permissions:
            self.role_permissions[role_id] = {}
            
        # Set permission level
        self.role_permissions[role_id][resource_type] = level
        
        return permission_id

    def remove_permission(self, role_id: str, resource_type: str) -> bool:
        """
        Remove a permission from a role
        
        Args:
            role_id: ID of role to modify
            resource_type: Type of resource
            
        Returns:
            True if successful
        """
        # Check if role exists
        if role_id not in self.roles:
            return False
            
        # Check if role has this permission
        if role_id not in self.role_permissions:
            return False
            
        if resource_type not in self.role_permissions[role_id]:
            return False
            
        # Remove permission
        del self.role_permissions[role_id][resource_type]
        
        # Clean up permissions dict if empty
        if not self.role_permissions[role_id]:
            del self.role_permissions[role_id]
            
        return True

    def get_effective_permissions(self, role_ids: List[str]) -> Dict[str, PermissionLevel]:
        """
        Get effective permissions by combining all role permissions
        
        Args:
            role_ids: List of role IDs to combine
            
        Returns:
            Dictionary of effective permissions
        """
        result = {}
        
        # Process each role
        for role_id in role_ids:
            # Get direct permissions
            if role_id in self.role_permissions:
                for resource, level in self.role_permissions[role_id].items():
                    # Only keep highest level
                    if resource not in result or level.value > result.get(resource, PermissionLevel.NONE).value:
                        result[resource] = level
            
            # Get inherited permissions through parent roles
            if role_id in self.roles:
                parent_permissions = self.get_effective_permissions(
                    [pid for pid in self.roles[role_id].parent_roles if pid in self.roles]
                )
                for resource, level in parent_permissions.items():
                    if resource not in result or level.value > result.get(resource, PermissionLevel.NONE).value:
                        result[resource] = level
            
        return result

    def check_permission(self, 
                       role_ids: List[str],
                       resource_type: str,
                       required_level: PermissionLevel) -> bool:
        """
        Check if any of the roles have sufficient permission
        
        Args:
            role_ids: List of role IDs to check
            resource_type: Type of resource
            required_level: Required permission level
            
        Returns:
            True if permitted, False otherwise
        """
        # Get effective permissions
        permissions = self.get_effective_permissions(role_ids)
        
        # Check against required level
        if resource_type in permissions:
            return permissions[resource_type].value >= required_level.value
            
        # No explicit permission means NONE
        return required_level == PermissionLevel.NONE

    def get_role_permissions(self, role_id: str) -> Dict[str, Any]:
        """
        Get all permissions for a role
        
        Args:
            role_id: ID of role
            
        Returns:
            Dictionary containing permissions
        """
        if role_id not in self.role_permissions:
            return {}
            
        return {
            resource: level.name 
            for resource, level in self.role_permissions[role_id].items()
        }

    def get_role_hierarchy(self, role_id: str) -> Dict[str, Any]:
        """
        Get complete hierarchy for a role
        
        Args:
            role_id: ID of role
            
        Returns:
            Dictionary containing role hierarchy information
        """
        # Check if role exists
        if role_id not in self.roles:
            return {}
            
        role = self.roles[role_id]
        
        # Build hierarchy structure
        hierarchy = {
            "role": role.to_dict(),
            "direct_permissions": self.get_role_permissions(role_id),
            "inherited_permissions": {},
            "parents": [],
            "all_permissions": {}
        }
        
        # Get parent roles
        parents = []
        for parent_id in role.parent_roles:
            if parent_id in self.roles:
                parents.append({
                    "role": self.roles[parent_id].to_dict(),
                    "permissions": self.get_role_permissions(parent_id)
                })
                
        hierarchy["parents"] = parents
        
        # Calculate effective permissions
        effective_permissions = self.get_effective_permissions([role_id])
        hierarchy["all_permissions"] = {
            r: l.name for r, l in effective_permissions.items()
        }
        
        # Calculate inherited permissions
        direct = self.get_role_permissions(role_id)
        inherited = {}
        for p in parents:
            for res, lev in p["permissions"].items():
                if res not in direct:  # Only show inherited permissions
                    inherited[res] = lev
        
        hierarchy["inherited_permissions"] = inherited
        
        return hierarchy

    def get_all_roles(self) -> List[Dict[str, Any]]:
        """Get all defined roles"""
        return [r.to_dict() for r in self.roles.values()]

    def get_all_permissions(self) -> Dict[str, Dict[str, str]]:
        """Get all permissions by role"""
        result = {}
        
        for role_id, permissions in self.role_permissions.items():
            if role_id in self.roles:
                role_name = self.roles[role_id].name
                result[role_name] = {
                    resource: level.name for resource, level in permissions.items()
                }
                
        return result

    def update_role(self, 
                  role_id: str,
                  updates: Dict[str, Any]) -> bool:
        """
        Update role details
        
        Args:
            role_id: ID of role to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        # Check if role exists
        if role_id not in self.roles:
            return False
            
        role = self.roles[role_id]
        
        # Update name
        if "name" in updates:
            new_name = updates["name"]
            if new_name in self.role_names and self.role_names[new_name] != role_id:
                return False  # Name conflict
                
            # Update name mapping
            old_name = role.name
            if old_name in self.role_names:
                del self.role_names[old_name]
            self.role_names[new_name] = role_id
            role.name = new_name
            
        # Update description
        if "description" in updates:
            role.description = updates["description"]
            
        # Update parent roles
        if "parent_roles" in updates:
            role.parent_roles = updates["parent_roles"]
            
        # Mark as updated
        role.updated_at = datetime.now().isoformat()
        
        return True

    def apply_to_validator(self, validator: PermissionValidator) -> None:
        """
        Apply configured roles and permissions to a validator
        
        Args:
            validator: PermissionValidator to configure
        """
        # Convert our role permissions to validator format
        for role_id, permissions in self.role_permissions.items():
            if role_id in self.roles:
                role = self.roles[role_id]
                validator.add_role_permissions(
                    role.name,
                    permissions
                )