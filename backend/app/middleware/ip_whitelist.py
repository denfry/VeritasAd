"""
IP Whitelist Middleware.
BigTech Standard - аналог AWS Security Groups, Google Cloud Firewall.

Restricts access to admin endpoints to specific IP addresses only.
"""
from typing import List, Set, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog
import ipaddress

logger = structlog.get_logger(__name__)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to restrict access to specific IP addresses.
    
    Usage:
        app.add_middleware(
            IPWhitelistMiddleware,
            whitelist=["192.168.1.0/24", "10.0.0.1"],
            paths=["/api/v1/admin"],
        )
    """
    
    def __init__(
        self,
        app: ASGIApp,
        whitelist: Optional[List[str]] = None,
        paths: Optional[List[str]] = None,
        enabled: bool = True,
    ):
        super().__init__(app)
        self.enabled = enabled
        self.whitelist: Set[ipaddress.IPv4Network | ipaddress.IPv6Network] = set()
        self.paths = paths or ["/api/v1/admin"]
        
        # Parse whitelist
        if whitelist:
            for ip in whitelist:
                try:
                    # Try as network (CIDR)
                    if "/" in ip:
                        self.whitelist.add(ipaddress.ip_network(ip, strict=False))
                    else:
                        # Single IP - convert to /32 or /128
                        self.whitelist.add(ipaddress.ip_network(ip))
                except ValueError as e:
                    logger.warning("invalid_ip_in_whitelist", ip=ip, error=str(e))
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """
        Extract client IP from request.
        Handles proxies and load balancers.
        """
        # Check X-Forwarded-For header
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Direct connection
        if request.client:
            return request.client.host
        
        return None
    
    def _is_ip_allowed(self, ip: str) -> bool:
        """Check if IP is in whitelist."""
        try:
            client_ip = ipaddress.ip_address(ip)
            
            for network in self.whitelist:
                if client_ip in network:
                    return True
            
            return False
        except ValueError:
            return False
    
    def _should_check_path(self, path: str) -> bool:
        """Check if path should be protected."""
        for protected_path in self.paths:
            if path.startswith(protected_path):
                return True
        return False
    
    async def dispatch(self, request: Request, call_next):
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Check if path should be protected
        if not self._should_check_path(request.url.path):
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        if not client_ip:
            logger.warning("could_not_determine_client_ip", path=request.url.path)
            return await call_next(request)
        
        # Check whitelist
        if self.whitelist and not self._is_ip_allowed(client_ip):
            logger.warning(
                "ip_blocked_by_whitelist",
                ip=client_ip,
                path=request.url.path,
                user_agent=request.headers.get("user-agent"),
            )
            
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Access denied: IP address not in whitelist",
                    "error_code": "IP_NOT_WHITELISTED",
                },
            )
        
        # IP is allowed
        request.state.ip_whitelisted = True
        return await call_next(request)


class IPBlacklistMiddleware(BaseHTTPMiddleware):
    """
    Middleware to block specific IP addresses.
    Useful for blocking malicious actors.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        blacklist: Optional[List[str]] = None,
        paths: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.blacklist: Set[ipaddress.IPv4Address | ipaddress.IPv6Address] = set()
        self.paths = paths or []  # Empty = all paths
        
        if blacklist:
            for ip in blacklist:
                try:
                    self.blacklist.add(ipaddress.ip_address(ip))
                except ValueError:
                    logger.warning("invalid_ip_in_blacklist", ip=ip)
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        if request.client:
            return request.client.host
        return None
    
    def _should_check_path(self, path: str) -> bool:
        if not self.paths:
            return True  # Check all paths
        for protected_path in self.paths:
            if path.startswith(protected_path):
                return True
        return False
    
    async def dispatch(self, request: Request, call_next):
        if not self._should_check_path(request.url.path):
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        
        if client_ip:
            try:
                if ipaddress.ip_address(client_ip) in self.blacklist:
                    logger.warning(
                        "ip_blocked_by_blacklist",
                        ip=client_ip,
                        path=request.url.path,
                    )
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={
                            "detail": "Access denied: IP address is blocked",
                            "error_code": "IP_BLACKLISTED",
                        },
                    )
            except ValueError:
                pass
        
        return await call_next(request)


# In-memory storage for dynamic IP management
_dynamic_blacklist: Set[str] = set()
_dynamic_whitelist: Set[str] = set()


def add_to_blacklist(ip: str) -> None:
    """Add IP to dynamic blacklist."""
    _dynamic_blacklist.add(ip)
    logger.info("ip_added_to_blacklist", ip=ip)


def remove_from_blacklist(ip: str) -> None:
    """Remove IP from dynamic blacklist."""
    _dynamic_blacklist.discard(ip)
    logger.info("ip_removed_from_blacklist", ip=ip)


def add_to_whitelist(ip: str) -> None:
    """Add IP to dynamic whitelist."""
    _dynamic_whitelist.add(ip)
    logger.info("ip_added_to_whitelist", ip=ip)


def remove_from_whitelist(ip: str) -> None:
    """Remove IP from dynamic whitelist."""
    _dynamic_whitelist.discard(ip)
    logger.info("ip_removed_from_whitelist", ip=ip)


def get_blocked_ips() -> List[str]:
    """Get list of blocked IPs."""
    return list(_dynamic_blacklist)


def get_whitelisted_ips() -> List[str]:
    """Get list of whitelisted IPs."""
    return list(_dynamic_whitelist)
