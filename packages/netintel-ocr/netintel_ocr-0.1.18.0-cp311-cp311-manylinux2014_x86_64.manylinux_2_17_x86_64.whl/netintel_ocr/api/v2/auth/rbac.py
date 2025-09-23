"""
Role-Based Access Control (RBAC) System
"""

from typing import Dict, List, Set, Optional, Any
from enum import Enum
from datetime import datetime
import logging
from pydantic import BaseModel, Field
from fastapi import HTTPException, status
import json
from pathlib import Path


logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    """Resource types in the system"""
    DOCUMENT = "document"
    COLLECTION = "collection"
    SEARCH = "search"
    ANALYTICS = "analytics"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    ADMIN = "admin"
    MILVUS = "milvus"
    MCP = "mcp"


class Action(str, Enum):
    """Actions that can be performed on resources"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    EXPORT = "export"
    SHARE = "share"


class Permission(BaseModel):
    """Permission definition"""
    id: str
    name: str
    resource_type: ResourceType
    actions: List[Action]
    conditions: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class Role(BaseModel):
    """Role definition"""
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str]  # Permission IDs
    parent_roles: List[str] = Field(default_factory=list)  # Role inheritance
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(BaseModel):
    """User with roles"""
    id: str
    username: str
    email: Optional[str] = None
    roles: List[str]  # Role IDs
    direct_permissions: List[str] = Field(default_factory=list)  # Override permissions
    attributes: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_access: Optional[datetime] = None


class RBACService:
    """Role-Based Access Control Service"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize RBAC service
        
        Args:
            config_path: Path to RBAC configuration file
        """
        
        # Storage for roles and permissions
        self.permissions: Dict[str, Permission] = {}
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        
        # Cache for computed permissions
        self._permission_cache: Dict[str, Set[str]] = {}
        
        # Load configuration
        if config_path and config_path.exists():
            self._load_config(config_path)
        else:
            self._initialize_default_rbac()

    def _initialize_default_rbac(self):
        """
        Initialize default RBAC configuration
        """
        
        # Default Permissions
        default_permissions = [
            # Document permissions
            Permission(
                id="doc_read",
                name="Read Documents",
                resource_type=ResourceType.DOCUMENT,
                actions=[Action.READ],
                description="Read document content and metadata",
            ),
            Permission(
                id="doc_write",
                name="Write Documents",
                resource_type=ResourceType.DOCUMENT,
                actions=[Action.CREATE, Action.UPDATE],
                description="Create and update documents",
            ),
            Permission(
                id="doc_delete",
                name="Delete Documents",
                resource_type=ResourceType.DOCUMENT,
                actions=[Action.DELETE],
                description="Delete documents",
            ),
            Permission(
                id="doc_export",
                name="Export Documents",
                resource_type=ResourceType.DOCUMENT,
                actions=[Action.EXPORT],
                description="Export documents in various formats",
            ),
            
            # Search permissions
            Permission(
                id="search_basic",
                name="Basic Search",
                resource_type=ResourceType.SEARCH,
                actions=[Action.EXECUTE],
                conditions={"search_types": ["basic", "similarity"]},
                description="Execute basic searches",
            ),
            Permission(
                id="search_advanced",
                name="Advanced Search",
                resource_type=ResourceType.SEARCH,
                actions=[Action.EXECUTE],
                conditions={"search_types": ["advanced", "hybrid", "multi_vector"]},
                description="Execute advanced searches",
            ),
            
            # Analytics permissions
            Permission(
                id="analytics_view",
                name="View Analytics",
                resource_type=ResourceType.ANALYTICS,
                actions=[Action.READ],
                description="View analytics dashboards",
            ),
            Permission(
                id="analytics_export",
                name="Export Analytics",
                resource_type=ResourceType.ANALYTICS,
                actions=[Action.EXPORT],
                description="Export analytics data",
            ),
            
            # Knowledge Graph permissions
            Permission(
                id="kg_query",
                name="Query Knowledge Graph",
                resource_type=ResourceType.KNOWLEDGE_GRAPH,
                actions=[Action.READ, Action.EXECUTE],
                description="Query knowledge graph",
            ),
            Permission(
                id="kg_modify",
                name="Modify Knowledge Graph",
                resource_type=ResourceType.KNOWLEDGE_GRAPH,
                actions=[Action.CREATE, Action.UPDATE, Action.DELETE],
                description="Modify knowledge graph",
            ),
            
            # Milvus permissions
            Permission(
                id="milvus_read",
                name="Read Milvus",
                resource_type=ResourceType.MILVUS,
                actions=[Action.READ],
                description="Read from Milvus collections",
            ),
            Permission(
                id="milvus_write",
                name="Write Milvus",
                resource_type=ResourceType.MILVUS,
                actions=[Action.CREATE, Action.UPDATE],
                description="Write to Milvus collections",
            ),
            Permission(
                id="milvus_manage",
                name="Manage Milvus",
                resource_type=ResourceType.MILVUS,
                actions=[Action.MANAGE, Action.DELETE],
                description="Manage Milvus collections and indices",
            ),
            
            # MCP permissions
            Permission(
                id="mcp_use",
                name="Use MCP Tools",
                resource_type=ResourceType.MCP,
                actions=[Action.EXECUTE],
                description="Use MCP tools and resources",
            ),
            Permission(
                id="mcp_admin",
                name="Administer MCP",
                resource_type=ResourceType.MCP,
                actions=[Action.MANAGE],
                description="Manage MCP configuration",
            ),
            
            # Admin permissions
            Permission(
                id="admin_users",
                name="Manage Users",
                resource_type=ResourceType.ADMIN,
                actions=[Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
                description="Manage user accounts",
            ),
            Permission(
                id="admin_roles",
                name="Manage Roles",
                resource_type=ResourceType.ADMIN,
                actions=[Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
                description="Manage roles and permissions",
            ),
            Permission(
                id="admin_system",
                name="System Administration",
                resource_type=ResourceType.ADMIN,
                actions=[Action.MANAGE],
                description="Full system administration",
            ),
        ]
        
        # Add permissions
        for perm in default_permissions:
            self.permissions[perm.id] = perm
        
        # Default Roles
        default_roles = [
            Role(
                id="viewer",
                name="Viewer",
                description="Read-only access",
                permissions=["doc_read", "search_basic", "analytics_view", "kg_query", "milvus_read"],
            ),
            Role(
                id="analyst",
                name="Analyst",
                description="Analyst with advanced search and export capabilities",
                permissions=[
                    "doc_read", "doc_export",
                    "search_basic", "search_advanced",
                    "analytics_view", "analytics_export",
                    "kg_query",
                    "milvus_read",
                    "mcp_use",
                ],
            ),
            Role(
                id="editor",
                name="Editor",
                description="Create and modify content",
                permissions=[
                    "doc_read", "doc_write", "doc_export",
                    "search_basic", "search_advanced",
                    "analytics_view",
                    "kg_query", "kg_modify",
                    "milvus_read", "milvus_write",
                    "mcp_use",
                ],
            ),
            Role(
                id="admin",
                name="Administrator",
                description="Full system access",
                permissions=[
                    "doc_read", "doc_write", "doc_delete", "doc_export",
                    "search_basic", "search_advanced",
                    "analytics_view", "analytics_export",
                    "kg_query", "kg_modify",
                    "milvus_read", "milvus_write", "milvus_manage",
                    "mcp_use", "mcp_admin",
                    "admin_users", "admin_roles", "admin_system",
                ],
            ),
            Role(
                id="developer",
                name="Developer",
                description="API and integration access",
                permissions=[
                    "doc_read", "doc_write",
                    "search_basic", "search_advanced",
                    "kg_query",
                    "milvus_read", "milvus_write",
                    "mcp_use",
                ],
                parent_roles=["analyst"],  # Inherit from analyst
            ),
        ]
        
        # Add roles
        for role in default_roles:
            self.roles[role.id] = role
        
        logger.info(
            f"Initialized default RBAC with {len(self.permissions)} permissions "
            f"and {len(self.roles)} roles"
        )

    def _load_config(self, config_path: Path):
        """
        Load RBAC configuration from file
        
        Args:
            config_path: Path to configuration file
        """
        
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            
            # Load permissions
            for perm_data in config.get("permissions", []):
                perm = Permission(**perm_data)
                self.permissions[perm.id] = perm
            
            # Load roles
            for role_data in config.get("roles", []):
                role = Role(**role_data)
                self.roles[role.id] = role
            
            logger.info(
                f"Loaded RBAC config: {len(self.permissions)} permissions, "
                f"{len(self.roles)} roles"
            )
            
        except Exception as e:
            logger.error(f"Failed to load RBAC config: {e}")
            self._initialize_default_rbac()

    def check_permission(
        self,
        user_id: str,
        resource_type: ResourceType,
        action: Action,
        resource_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if user has permission to perform action on resource
        
        Args:
            user_id: User ID
            resource_type: Type of resource
            action: Action to perform
            resource_id: Optional resource ID for resource-specific checks
            context: Optional context for condition evaluation
            
        Returns:
            True if permitted, False otherwise
        """
        
        user = self.users.get(user_id)
        if not user or not user.active:
            return False
        
        # Get all user permissions
        user_permissions = self._get_user_permissions(user)
        
        # Check each permission
        for perm_id in user_permissions:
            perm = self.permissions.get(perm_id)
            if not perm:
                continue
            
            # Check resource type and action
            if perm.resource_type == resource_type and action in perm.actions:
                # Check conditions if any
                if perm.conditions:
                    if not self._evaluate_conditions(perm.conditions, context):
                        continue
                
                return True
        
        return False

    def _get_user_permissions(self, user: User) -> Set[str]:
        """
        Get all permissions for a user (including inherited)
        
        Args:
            user: User object
            
        Returns:
            Set of permission IDs
        """
        
        # Check cache
        if user.id in self._permission_cache:
            return self._permission_cache[user.id]
        
        permissions = set(user.direct_permissions)
        
        # Get permissions from roles (with inheritance)
        for role_id in user.roles:
            permissions.update(self._get_role_permissions(role_id))
        
        # Cache result
        self._permission_cache[user.id] = permissions
        
        return permissions

    def _get_role_permissions(
        self,
        role_id: str,
        visited: Optional[Set[str]] = None,
    ) -> Set[str]:
        """
        Get all permissions for a role (including inherited)
        
        Args:
            role_id: Role ID
            visited: Set of visited roles to prevent cycles
            
        Returns:
            Set of permission IDs
        """
        
        if visited is None:
            visited = set()
        
        # Prevent cycles
        if role_id in visited:
            return set()
        
        visited.add(role_id)
        
        role = self.roles.get(role_id)
        if not role:
            return set()
        
        permissions = set(role.permissions)
        
        # Get inherited permissions
        for parent_role_id in role.parent_roles:
            permissions.update(
                self._get_role_permissions(parent_role_id, visited)
            )
        
        return permissions

    def _evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        context: Optional[Dict[str, Any]],
    ) -> bool:
        """
        Evaluate permission conditions
        
        Args:
            conditions: Permission conditions
            context: Context for evaluation
            
        Returns:
            True if conditions are met
        """
        
        if not context:
            return False
        
        for key, expected in conditions.items():
            actual = context.get(key)
            
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False
        
        return True

    def add_user(
        self,
        user_id: str,
        username: str,
        roles: List[str],
        email: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> User:
        """
        Add a new user
        
        Args:
            user_id: User ID
            username: Username
            roles: List of role IDs
            email: User email
            attributes: Additional user attributes
            
        Returns:
            Created user
        """
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            roles=roles,
            attributes=attributes or {},
        )
        
        self.users[user_id] = user
        
        # Clear permission cache
        self._permission_cache.pop(user_id, None)
        
        logger.info(f"Added user {username} with roles {roles}")
        
        return user

    def update_user_roles(
        self,
        user_id: str,
        roles: List[str],
    ):
        """
        Update user roles
        
        Args:
            user_id: User ID
            roles: New list of role IDs
        """
        
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user.roles = roles
        user.updated_at = datetime.utcnow()
        
        # Clear permission cache
        self._permission_cache.pop(user_id, None)
        
        logger.info(f"Updated roles for user {user_id}: {roles}")

    def grant_permission(
        self,
        user_id: str,
        permission_id: str,
    ):
        """
        Grant direct permission to user
        
        Args:
            user_id: User ID
            permission_id: Permission ID
        """
        
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if permission_id not in self.permissions:
            raise ValueError(f"Permission {permission_id} not found")
        
        if permission_id not in user.direct_permissions:
            user.direct_permissions.append(permission_id)
            user.updated_at = datetime.utcnow()
            
            # Clear permission cache
            self._permission_cache.pop(user_id, None)
            
            logger.info(f"Granted permission {permission_id} to user {user_id}")

    def revoke_permission(
        self,
        user_id: str,
        permission_id: str,
    ):
        """
        Revoke direct permission from user
        
        Args:
            user_id: User ID
            permission_id: Permission ID
        """
        
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if permission_id in user.direct_permissions:
            user.direct_permissions.remove(permission_id)
            user.updated_at = datetime.utcnow()
            
            # Clear permission cache
            self._permission_cache.pop(user_id, None)
            
            logger.info(f"Revoked permission {permission_id} from user {user_id}")

    def create_role(
        self,
        role_id: str,
        name: str,
        permissions: List[str],
        description: Optional[str] = None,
        parent_roles: Optional[List[str]] = None,
    ) -> Role:
        """
        Create a new role
        
        Args:
            role_id: Role ID
            name: Role name
            permissions: List of permission IDs
            description: Role description
            parent_roles: Parent roles for inheritance
            
        Returns:
            Created role
        """
        
        role = Role(
            id=role_id,
            name=name,
            description=description,
            permissions=permissions,
            parent_roles=parent_roles or [],
        )
        
        self.roles[role_id] = role
        
        # Clear all permission caches
        self._permission_cache.clear()
        
        logger.info(f"Created role {name} with permissions {permissions}")
        
        return role

    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information including effective permissions
        
        Args:
            user_id: User ID
            
        Returns:
            User information if found
        """
        
        user = self.users.get(user_id)
        if not user:
            return None
        
        # Get all permissions
        permissions = self._get_user_permissions(user)
        
        # Get permission details
        permission_details = [
            self.permissions[pid].dict()
            for pid in permissions
            if pid in self.permissions
        ]
        
        return {
            "user": user.dict(),
            "effective_permissions": list(permissions),
            "permission_details": permission_details,
            "roles": [
                self.roles[rid].dict()
                for rid in user.roles
                if rid in self.roles
            ],
        }


# Global RBAC service instance
rbac_service = RBACService()


# Decorator for permission checks
def require_permission(
    resource_type: ResourceType,
    action: Action,
):
    """
    Decorator to require permission for a function
    
    Args:
        resource_type: Resource type
        action: Required action
        
    Returns:
        Decorator function
    """
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id from kwargs or context
            user_id = kwargs.get("user_id")
            if not user_id:
                # Try to get from request context
                from fastapi import Request
                request = kwargs.get("request")
                if request and hasattr(request.state, "user_id"):
                    user_id = request.state.user_id
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated",
                )
            
            # Check permission
            if not rbac_service.check_permission(
                user_id,
                resource_type,
                action,
                context=kwargs.get("context"),
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {resource_type}.{action}",
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator