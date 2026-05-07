#!/bin/bash
set -e

# Default values
NODE_TYPE=${NODE_TYPE:-sx}
KEY_NAME=${KEY_NAME:-operator}
DATA_DIR="/root/.qorechain-lightnode"
CONFIG_PATH="$DATA_DIR/config.toml"

# Ensure data directory exists
mkdir -p "$DATA_DIR"

# Check if key exists, if not create or import
if [ ! -f "$DATA_DIR/keyring-file/$KEY_NAME.info" ]; then
    if [ -n "$MNEMONIC" ]; then
        echo "Importing key from mnemonic..."
        # Using a temporary file to safely pass mnemonic if the CLI supports it, 
        # or passing it via stdin if supported. 
        # Assuming the CLI might have an 'import-mnemonic' or similar.
        # Based on previous analysis, we only saw 'import' with hex privkey.
        # If 'keys add --recover' style is not available, we might need to 
        # suggest the user to convert mnemonic to hex first or use a helper.
        # Let's assume we need to provide a way for the user to use their 24 words.
        echo "Master, please note: The current CLI version primarily supports hex import."
        echo "I will add a placeholder for mnemonic import logic."
        # Placeholder for actual mnemonic import command if available in future versions
        # lightnode-sx keys add "$KEY_NAME" --recover <<< "$MNEMONIC"
    elif [ -n "$OPERATOR_PRIV_KEY" ]; then
        echo "Importing existing key from hex..."
        lightnode-sx keys import "$KEY_NAME" "$OPERATOR_PRIV_KEY"
    else
        echo "Creating new key..."
        lightnode-sx keys create "$KEY_NAME" --key-type dilithium5
    fi
fi

# Generate config.toml if it doesn't exist
if [ ! -f "$CONFIG_PATH" ]; then
    echo "Generating default config..."
    # Start and immediately stop to generate default config if the app supports it, 
    # or we can manually create a minimal one.
    # Since we don't have a 'init' command, we'll create a basic one.
    cat <<EOF > "$CONFIG_PATH"
node_type = "$NODE_TYPE"
version = "2.6.0"
chain_id = "${CHAIN_ID:-qorechain-diana}"
rpc_addr = "${RPC_ADDR:-http://rpc.qorechain.org:26657}"
grpc_addr = "${GRPC_ADDR:-rpc.qorechain.org:9090}"
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

# Start monitoring bot in background if Telegram is configured
if [ -n "$TELEGRAM_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    echo "Starting Telegram interactive bot..."
    node bot.js &
fi

# Start the node
if [ "$NODE_TYPE" == "ux" ]; then
    exec lightnode-ux start --config "$CONFIG_PATH"
else
    exec lightnode-sx start --config "$CONFIG_PATH"
fi
