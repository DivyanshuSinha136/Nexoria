"""
nexoria.std.alert
====================
Feedback surfaces: a dismissible banner, an auto-dismissing corner
toast, and a compact inline alert for forms/fields.

    from nexoria.std.alert import alert_banner, toast, inline_alert
"""

from __future__ import annotations

from .alerts import alert_banner, toast, inline_alert

__all__ = ["alert_banner", "toast", "inline_alert"]
