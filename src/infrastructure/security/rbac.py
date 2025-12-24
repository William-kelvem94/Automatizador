# -*- coding: utf-8 -*-

"""
RBAC MODULE - Role-Based Access Control
Sistema de controle de acesso baseado em papéis
"""

import json
from typing import Dict, Set, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from ...shared.utils.logger import get_logger


class Permission(Enum):
    """Permissões do sistema"""
    # Tarefas
    TASK_CREATE = "task:create"
    TASK_READ = "task:read"
    TASK_UPDATE = "task:update"
    TASK_DELETE = "task:delete"
    TASK_EXECUTE = "task:execute"

    # Workflows
    WORKFLOW_CREATE = "workflow:create"
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_UPDATE = "workflow:update"
    WORKFLOW_DELETE = "workflow:delete"

    # Usuários e administração
    USER_MANAGE = "user:manage"
    ROLE_MANAGE = "role:manage"
    AUDIT_READ = "audit:read"

    # Sistema
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MONITOR = "system:monitor"
    BACKUP_MANAGE = "backup:manage"

    # APIs e integrações
    API_ACCESS = "api:access"
    WEBHOOK_MANAGE = "webhook:manage"
    INTEGRATION_MANAGE = "integration:manage"


class Role(Enum):
    """Papéis pré-definidos do sistema"""
    GUEST = "guest"
    USER = "user"
    POWER_USER = "power_user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


@dataclass
class User:
    """Usuário do sistema"""
    id: str
    username: str
    email: str
    roles: Set[Role] = field(default_factory=set)
    custom_permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_role(self, role: Role) -> bool:
        """Verificar se usuário tem um papel"""
        return role in self.roles

    def add_role(self, role: Role) -> None:
        """Adicionar papel ao usuário"""
        self.roles.add(role)

    def remove_role(self, role: Role) -> None:
        """Remover papel do usuário"""
        self.roles.discard(role)

    def has_permission(self, permission: Permission) -> bool:
        """Verificar se usuário tem uma permissão"""
        # Verificar permissões customizadas primeiro
        if permission in self.custom_permissions:
            return True

        # Verificar permissões baseadas em papéis
        for role in self.roles:
            if permission in ROLE_PERMISSIONS.get(role, set()):
                return True

        return False

    def grant_permission(self, permission: Permission) -> None:
        """Conceder permissão customizada"""
        self.custom_permissions.add(permission)

    def revoke_permission(self, permission: Permission) -> None:
        """Revogar permissão customizada"""
        self.custom_permissions.discard(permission)


# Definições de permissões por papel
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.GUEST: {
        Permission.TASK_READ,
        Permission.WORKFLOW_READ,
    },
    Role.USER: {
        Permission.TASK_CREATE,
        Permission.TASK_READ,
        Permission.TASK_UPDATE,
        Permission.TASK_EXECUTE,
        Permission.WORKFLOW_READ,
        Permission.API_ACCESS,
    },
    Role.POWER_USER: {
        Permission.TASK_CREATE,
        Permission.TASK_READ,
        Permission.TASK_UPDATE,
        Permission.TASK_DELETE,
        Permission.TASK_EXECUTE,
        Permission.WORKFLOW_CREATE,
        Permission.WORKFLOW_READ,
        Permission.WORKFLOW_UPDATE,
        Permission.WORKFLOW_DELETE,
        Permission.API_ACCESS,
        Permission.WEBHOOK_MANAGE,
    },
    Role.ADMIN: {
        Permission.TASK_CREATE,
        Permission.TASK_READ,
        Permission.TASK_UPDATE,
        Permission.TASK_DELETE,
        Permission.TASK_EXECUTE,
        Permission.WORKFLOW_CREATE,
        Permission.WORKFLOW_READ,
        Permission.WORKFLOW_UPDATE,
        Permission.WORKFLOW_DELETE,
        Permission.USER_MANAGE,
        Permission.AUDIT_READ,
        Permission.SYSTEM_MONITOR,
        Permission.API_ACCESS,
        Permission.WEBHOOK_MANAGE,
        Permission.INTEGRATION_MANAGE,
    },
    Role.SUPER_ADMIN: {
        # Todas as permissões
        permission for permission in Permission
    }
}


@dataclass
class AccessRequest:
    """Requisição de acesso"""
    user: User
    resource: str
    action: str
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def permission(self) -> Optional[Permission]:
        """Converter ação em permissão"""
        # Mapeamento de ações para permissões
        action_mapping = {
            'create': 'create',
            'read': 'read',
            'update': 'update',
            'delete': 'delete',
            'execute': 'execute',
            'manage': 'manage',
            'access': 'access',
            'monitor': 'monitor',
            'config': 'config'
        }

        action_part = action_mapping.get(self.action.lower(), self.action.lower())
        permission_name = f"{self.resource}:{action_part}"

        try:
            return Permission(permission_name)
        except ValueError:
            return None


class AccessControlError(Exception):
    """Erro de controle de acesso"""
    pass


class RBACManager:
    """Gerenciador de RBAC"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.users: Dict[str, User] = {}
        self.custom_roles: Dict[str, Set[Permission]] = {}

        # Inicializar com usuários padrão se necessário
        self._initialize_default_users()

    def _initialize_default_users(self):
        """Inicializar usuários padrão"""
        # Super admin padrão (para setup inicial)
        super_admin = User(
            id="system-admin",
            username="admin",
            email="admin@automator.local",
            roles={Role.SUPER_ADMIN}
        )
        self.users[super_admin.id] = super_admin

        # Usuário guest
        guest = User(
            id="guest",
            username="guest",
            email="guest@automator.local",
            roles={Role.GUEST}
        )
        self.users[guest.id] = guest

    def create_user(self, user_id: str, username: str, email: str,
                   initial_role: Role = Role.USER) -> User:
        """Criar novo usuário"""
        if user_id in self.users:
            raise AccessControlError(f"Usuário {user_id} já existe")

        user = User(
            id=user_id,
            username=username,
            email=email,
            roles={initial_role}
        )

        self.users[user_id] = user
        self.logger.info(f"Usuário criado: {username} ({user_id})")
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Obter usuário por ID"""
        return self.users.get(user_id)

    def delete_user(self, user_id: str) -> bool:
        """Excluir usuário"""
        if user_id in self.users:
            del self.users[user_id]
            self.logger.info(f"Usuário excluído: {user_id}")
            return True
        return False

    def assign_role(self, user_id: str, role: Role) -> bool:
        """Atribuir papel a usuário"""
        user = self.get_user(user_id)
        if not user:
            return False

        user.add_role(role)
        self.logger.info(f"Papel {role.value} atribuído a {user_id}")
        return True

    def revoke_role(self, user_id: str, role: Role) -> bool:
        """Revogar papel de usuário"""
        user = self.get_user(user_id)
        if not user:
            return False

        user.remove_role(role)
        self.logger.info(f"Papel {role.value} revogado de {user_id}")
        return True

    def grant_permission(self, user_id: str, permission: Permission) -> bool:
        """Conceder permissão customizada"""
        user = self.get_user(user_id)
        if not user:
            return False

        user.grant_permission(permission)
        self.logger.info(f"Permissão {permission.value} concedida a {user_id}")
        return True

    def revoke_permission(self, user_id: str, permission: Permission) -> bool:
        """Revogar permissão customizada"""
        user = self.get_user(user_id)
        if not user:
            return False

        user.revoke_permission(permission)
        self.logger.info(f"Permissão {permission.value} revogada de {user_id}")
        return True

    def check_access(self, access_request: AccessRequest) -> bool:
        """Verificar acesso baseado na requisição"""
        user = access_request.user

        # Verificar se usuário está ativo
        if not user.is_active:
            return False

        # Verificar permissão específica
        permission = access_request.permission
        if permission and user.has_permission(permission):
            self.logger.debug(f"Acesso concedido: {user.username} -> {permission.value}")
            return True

        # Verificar regras contextuais adicionais
        if self._check_contextual_rules(access_request):
            return True

        self.logger.warning(f"Acesso negado: {user.username} -> {access_request.resource}:{access_request.action}")
        return False

    def _check_contextual_rules(self, access_request: AccessRequest) -> bool:
        """Verificar regras contextuais de acesso"""
        user = access_request.user
        resource = access_request.resource
        action = access_request.action
        context = access_request.context

        # Regra: Usuários podem sempre acessar seus próprios recursos
        if context.get('owner_id') == user.id:
            return True

        # Regra: Admins podem acessar recursos de emergency
        if action == 'read' and context.get('emergency_access') and user.has_role(Role.ADMIN):
            return True

        # Regra: Usuários power podem executar tarefas compartilhadas
        if (resource == 'task' and action == 'execute' and
            context.get('shared') and user.has_role(Role.POWER_USER)):
            return True

        return False

    def create_custom_role(self, role_name: str, permissions: Set[Permission]) -> None:
        """Criar papel customizado"""
        if role_name in self.custom_roles:
            raise AccessControlError(f"Papel customizado {role_name} já existe")

        self.custom_roles[role_name] = permissions
        self.logger.info(f"Papel customizado criado: {role_name}")

    def delete_custom_role(self, role_name: str) -> bool:
        """Excluir papel customizado"""
        if role_name in self.custom_roles:
            del self.custom_roles[role_name]
            self.logger.info(f"Papel customizado excluído: {role_name}")
            return True
        return False

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Obter todas as permissões de um usuário"""
        user = self.get_user(user_id)
        if not user:
            return set()

        permissions = set()

        # Permissões de papéis
        for role in user.roles:
            permissions.update(ROLE_PERMISSIONS.get(role, set()))

        # Permissões customizadas
        permissions.update(user.custom_permissions)

        return permissions

    def get_role_permissions(self, role: Role) -> Set[Permission]:
        """Obter permissões de um papel"""
        return ROLE_PERMISSIONS.get(role, set())

    def list_users(self, role_filter: Optional[Role] = None) -> List[User]:
        """Listar usuários com filtro opcional por papel"""
        users = list(self.users.values())

        if role_filter:
            users = [u for u in users if role_filter in u.roles]

        return users

    def export_policy(self) -> Dict[str, Any]:
        """Exportar política de acesso completa"""
        return {
            'users': {
                user_id: {
                    'username': user.username,
                    'email': user.email,
                    'roles': [role.value for role in user.roles],
                    'custom_permissions': [p.value for p in user.custom_permissions],
                    'is_active': user.is_active
                }
                for user_id, user in self.users.items()
            },
            'custom_roles': {
                role_name: [p.value for p in permissions]
                for role_name, permissions in self.custom_roles.items()
            },
            'role_permissions': {
                role.value: [p.value for p in permissions]
                for role, permissions in ROLE_PERMISSIONS.items()
            }
        }

    def import_policy(self, policy_data: Dict[str, Any]) -> None:
        """Importar política de acesso"""
        try:
            # Importar usuários
            for user_id, user_data in policy_data.get('users', {}).items():
                roles = {Role(r) for r in user_data.get('roles', [])}
                custom_permissions = {Permission(p) for p in user_data.get('custom_permissions', [])}

                user = User(
                    id=user_id,
                    username=user_data['username'],
                    email=user_data['email'],
                    roles=roles,
                    custom_permissions=custom_permissions,
                    is_active=user_data.get('is_active', True)
                )

                self.users[user_id] = user

            # Importar papéis customizados
            for role_name, permissions in policy_data.get('custom_roles', {}).items():
                self.custom_roles[role_name] = {Permission(p) for p in permissions}

            self.logger.info("Política de acesso importada com sucesso")

        except Exception as e:
            self.logger.error(f"Erro ao importar política: {e}")
            raise AccessControlError(f"Falha na importação: {e}")

    def health_check(self) -> Dict[str, Any]:
        """Verificação de saúde do RBAC"""
        try:
            # Verificar usuários ativos
            active_users = sum(1 for u in self.users.values() if u.is_active)
            total_users = len(self.users)

            # Verificar papéis
            total_roles = len(ROLE_PERMISSIONS) + len(self.custom_roles)

            # Teste básico de acesso
            guest_user = self.get_user('guest')
            if guest_user and guest_user.has_permission(Permission.TASK_READ):
                access_test = True
            else:
                access_test = False

            return {
                'status': 'healthy' if access_test else 'degraded',
                'total_users': total_users,
                'active_users': active_users,
                'total_roles': total_roles,
                'custom_roles': len(self.custom_roles),
                'access_control_working': access_test
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Decorators para controle de acesso
def require_permission(permission: Permission):
    """Decorator para requerer permissão"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Obter usuário do contexto (implementação depende do framework usado)
            # Por enquanto, apenas log
            print(f"Checking permission: {permission.value}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role):
    """Decorator para requerer papel"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Obter usuário do contexto
            print(f"Checking role: {role.value}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Instância global do RBAC
rbac_manager = RBACManager()
