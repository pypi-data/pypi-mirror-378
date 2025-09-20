"""
HTTP-helpers (cookie logic, charset, Playwright ↔ Curl adapters).
"""

from __future__ import annotations

from http.cookies import SimpleCookie
from typing import Any, Iterable, Mapping, Tuple
from urllib.parse import SplitResult

from ..abstraction.cookies import Cookie

# ───────────────────── RFC 6265 helpers ──────────────────────────────


def cookie_matches(url_parts: SplitResult, cookie: Cookie) -> bool:  # noqa: ANN001
    def domain_match(host: str, cookie_domain: str | None) -> bool:
        if not cookie_domain:
            return True
        host = host.split(":", 1)[0].lower()
        cd = cookie_domain.lstrip(".").lower()
        return host == cd or host.endswith("." + cd)

    def path_match(req_path: str, cookie_path: str | None) -> bool:
        if not cookie_path:
            return True
        if not req_path.endswith("/"):
            req_path += "/"
        cp = cookie_path if cookie_path.endswith("/") else cookie_path + "/"
        return req_path.startswith(cp)

    return (
        domain_match(url_parts.hostname or "", cookie.domain)
        and path_match(url_parts.path or "/", cookie.path)
        and (not cookie.secure or url_parts.scheme == "https")
    )


# ───────────────────── charset helper ────────────────────────────────


def guess_encoding(headers: Mapping[str, str]) -> str:
    ctype = headers.get("content-type", "")
    if "charset=" in ctype:
        return ctype.split("charset=", 1)[1].split(";", 1)[0].strip(" \"'") or "utf-8"
    return "utf-8"


# ───────────────────── Cookie → Header ───────────────────────────────


def compose_cookie_header(
    url_parts: SplitResult,
    current_headers: Mapping[str, str],
    jar: Iterable[Cookie],
) -> Tuple[str, list[Cookie]]:
    """Returns (header string, [cookie list, actually sent])."""
    if "cookie" in current_headers:
        return current_headers["cookie"], []

    kv: list[str] = []
    sent: list[Cookie] = []
    for c in jar:
        if cookie_matches(url_parts, c):
            kv.append(f"{c.name}={c.value}")
            sent.append(c)

    return ("; ".join(kv) if kv else "", sent)


# ───────────────────── Set-Cookie → Cookie objects ───────────────────


def collect_set_cookie_headers(headers: Mapping[str, Any]) -> list[str]:
    """curl_cffi.Headers→list[str] всех *Set-Cookie*."""
    out: list[str] = []
    for k, v in headers.items():
        if k.lower() != "set-cookie":
            continue
        if isinstance(v, (list, tuple)):
            out.extend(v)
        else:
            out.extend(p.strip() for p in str(v).split(",") if p.strip())
    return out


def parse_set_cookie(raw_headers: list[str], default_domain: str) -> list[Cookie]:
    out: list[Cookie] = []
    for raw in raw_headers:
        jar = SimpleCookie()
        jar.load(raw)
        for m in jar.values():
            out.append(
                Cookie(
                    name=m.key,
                    value=m.value,
                    domain=(m["domain"] or default_domain).lower(),
                    path=m["path"] or "/",
                    secure=bool(m["secure"]),
                    http_only=bool(m["httponly"]),
                )
            )
    return out
