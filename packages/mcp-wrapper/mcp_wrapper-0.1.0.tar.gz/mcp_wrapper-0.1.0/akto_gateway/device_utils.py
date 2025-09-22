"""Device utilities for generating/storing a unique machine identifier."""

import uuid

try:
    import machineid
except ImportError:
    machineid = None

_machine_id = None


def _generate_machine_id() -> str:
    """Return machine ID using py-machineid or fallback to MAC address."""
    if machineid:
        try:
            mid = machineid.id()
            if mid and mid.strip():
                return mid.strip()
        except Exception:
            pass
    return str(uuid.getnode())


def get_machine_id() -> str:
    """Get the machine ID (initialize if not already set)."""
    global _machine_id
    if _machine_id is None:
        _machine_id = _generate_machine_id()
        _machine_id = _machine_id.replace("-", "")
    return _machine_id


def set_machine_id(value: str) -> None:
    """Explicitly set the machine ID."""
    global _machine_id
    _machine_id = value


if __name__ == "__main__":
    print(get_machine_id())
