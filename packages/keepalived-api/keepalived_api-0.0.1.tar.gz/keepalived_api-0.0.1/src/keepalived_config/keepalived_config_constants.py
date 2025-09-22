class KeepAlivedConfigConstants:
    INDENT_SIZE = 4
    
    # Configuration parameter descriptions and validation rules
    PARAM_DESCRIPTIONS = {
        # VRRP instance parameters
        "state": "VRRP instance state (MASTER or BACKUP)",
        "interface": "Network interface to run VRRP on",
        "virtual_router_id": "Virtual router ID (1-255)",
        "priority": "Instance priority (1-255, higher is more preferred)",
        "advert_int": "Advertisement interval in seconds (1-255)",
        "auth_type": "Authentication type (PASS or AH)",
        "auth_pass": "Authentication password (8 characters max for PASS)",
        
        # Virtual server parameters
        "delay_loop": "Delay timer for health checks in seconds",
        "lb_algo": "Load balancing algorithm (rr, wrr, lc, wlc, lblc, dh, sh, sed, nq)",
        "lb_kind": "Load balancing kind (NAT, DR, or TUN)",
        "protocol": "Service protocol (TCP, UDP, or SCTP)",
        
        # Real server parameters
        "weight": "Server weight for load balancing",
        
        # Health check parameters
        "connect_timeout": "Connection timeout for health checks",
        "delay_before_retry": "Delay before retrying a failed health check",
    }
    
    PARAM_VALIDATION_RULES = {
        # VRRP instance parameters
        "virtual_router_id": {"type": int, "min": 1, "max": 255},
        "priority": {"type": int, "min": 1, "max": 255},
        "advert_int": {"type": int, "min": 1, "max": 255},
        "state": {"type": str, "allowed": ["MASTER", "BACKUP"]},
        "auth_type": {"type": str, "allowed": ["PASS", "AH"]},
        
        # Virtual server parameters
        "delay_loop": {"type": int, "min": 1, "max": 65535},
        "lb_algo": {"type": str, "allowed": ["rr", "wrr", "lc", "wlc", "lblc", "dh", "sh", "sed", "nq"]},
        "lb_kind": {"type": str, "allowed": ["NAT", "DR", "TUN"]},
        "protocol": {"type": str, "allowed": ["TCP", "UDP", "SCTP"]},
        
        # Real server parameters
        "weight": {"type": int, "min": 0, "max": 65535},
        
        # Health check parameters
        "connect_timeout": {"type": int, "min": 1, "max": 65535},
        "delay_before_retry": {"type": int, "min": 1, "max": 65535},
    }
    
    @staticmethod
    def get_indent(level: int) -> str:
        return " " * KeepAlivedConfigConstants.INDENT_SIZE * level