"""Auth domain dependencies. Re-exports from core for domain encapsulation."""
from app.core.dependencies import (
    get_current_user,
    get_current_admin_user,
    get_api_key,
    increment_usage,
    verify_supabase_token,
    generate_api_key,
)

__all__ = [
    "get_current_user",
    "get_current_admin_user",
    "get_api_key",
    "increment_usage",
    "verify_supabase_token",
    "generate_api_key",
]
