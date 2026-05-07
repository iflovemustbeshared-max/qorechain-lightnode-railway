#!/bin/bash
set -e

NODE_TYPE=${NODE_TYPE:-sx}
KEY_NAME=${KEY_NAME:-operator}
DATA_DIR="/root/.qorechain-lightnode"
CONFIG_PATH="$DATA_DIR/config.toml"

mkdir -p "$DATA_DIR"

# ── Key setup ────────────────────────────────────────────────
if [ ! -f "$DATA_DIR/keyring-file/$KEY_NAME.info" ]; then
    if [ -n "$OPERATOR_PRIV_KEY" ]; then
        echo "Importing existing key from hex..."
        lightnode-sx keys import "$KEY_NAME" "$OPERATOR_PRIV_KEY" --type dilithium5
    else
        echo "Creating new key..."
        lightnode-sx keys create "$KEY_NAME" --type dilithium5
    fi
fi

# ── Config setup ─────────────────────────────────────────────
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Generating config..."
    cat <<EOF > "$CONFIG_PATH"
node_type = "$NODE_TYPE"
version = "2.12.0"
chain_id = "${CHAIN_ID:-qorechain-diana}"
rpc_addr = "${RPC_ADDR:-http://localhost:26657}"
grpc_addr = "${GRPC_ADDR:-localhost:9090}"
data_dir = "$DATA_DIR"
key_name = "$KEY_NAME"
keyring_backend = "test"

[delegation]
auto_compound = true
compound_interval = "1h"
min_reward_claim = "1000000"
rebalance_enabled = true
min_reputation = 0.5

[telemetry]
enabled = true
validator_interval = "30s"
network_interval = "15s"
bridge_interval = "60s"
tokenomics_interval = "60s"

[dashboard]
enabled = $([ "$NODE_TYPE" == "ux" ] && echo "true" || echo "false")
bind_addr = "0.0.0.0:${PORT:-8420}"

[logging]
log_level = "${LOG_LEVEL:-info}"
log_format = "text"
EOF
fi

# ── Telegram bot (opsional) ───────────────────────────────────
if [ -n "$TELEGRAM_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    echo "Starting Telegram bot..."
    cd /app && node bot.js &
fi

# ── Start node ───────────────────────────────────────────────
echo "Starting lightnode-$NODE_TYPE..."
if [ "$NODE_TYPE" == "ux" ]; then
    exec lightnode-ux start --config "$CONFIG_PATH"
else
    exec lightnode-sx start --config "$CONFIG_PATH"
fi
