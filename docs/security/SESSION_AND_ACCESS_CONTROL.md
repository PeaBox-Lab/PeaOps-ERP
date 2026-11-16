# Session and Access Control - v0.8.1

Access tokens are short lived and carry user, company and permission claims. Login also issues a random refresh token; only its SHA-256 hash is stored. Logout revokes the refresh session. Refresh does not extend the refresh-session expiry.

A centralized route policy makes health/login/refresh public, protects report reads with `reports:view`, other reads with `data:view`, and assigns domain permissions to recognized mutations. Unknown mutations require `data:write`, avoiding accidental public exposure.

This is a pilot foundation. Token-family rotation, theft detection, device/session listing, per-endpoint domain review, MFA/SSO and external identity providers remain future work.
