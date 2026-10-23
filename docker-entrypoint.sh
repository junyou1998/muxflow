#!/bin/bash
set -e

# Enforce UTF-8 encoding across all processes
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# Default to Unraid nobody:users (99:100) if not specified
PUID=${PUID:-99}
PGID=${PGID:-100}
UMASK=${UMASK:-022}

umask "$UMASK"

# Setup group
if ! getent group muxgroup >/dev/null 2>&1; then
    groupadd -o -g "$PGID" muxgroup 2>/dev/null || groupmod -o -g "$PGID" "$(getent group "$PGID" | cut -d: -f1)" 2>/dev/null || true
fi

# Setup user
if ! id -u muxuser >/dev/null 2>&1; then
    useradd -o -u "$PUID" -g "$PGID" -d /config -s /bin/sh muxuser 2>/dev/null || usermod -o -u "$PUID" "$(id -nu "$PUID")" 2>/dev/null || true
fi

# Ensure /config and /storage directories exist
mkdir -p /config /storage

# Ensure /config is owned by the designated user
chown -R "$PUID":"$PGID" /config 2>/dev/null || true

# Execute command
if [ "$(id -u)" = "0" ]; then
    exec gosu "$PUID":"$PGID" "$@"
else
    exec "$@"
fi
