# Sarcoin development-chain tools

This directory contains a reproducible local development-chain demonstration. It
requires **the custom Sarcoin build** of `bitcoind` and `bitcoin-cli`, Python 3.9 or
newer, and no Python packages. Original Bitcoin Core binaries fail the genesis
check. The expected genesis hash is read from `genesis.json`, next to the script.

From the repository root on Windows, after building the custom binaries:

```powershell
python sarcoin_tools/devnet_demo.py --bindir build/bin/Release --data-root sarcoin-local --report sarcoin-local/report.json
```

Use the actual directory containing both `.exe` files. On Linux or macOS:

```sh
python3 sarcoin_tools/devnet_demo.py --bindir build/bin --data-root sarcoin-local --report sarcoin-local/report.json
```

The script creates a fresh random subdirectory beneath `--data-root` every time.
It never deletes previous data. Both nodes bind P2P and RPC only to IPv4 loopback,
use random ports and local RPC cookie authentication, and disable discovery and
automatic outbound peer connections. No wallet passwords, RPC cookies, private
keys, or absolute local paths are written to the JSON report. Wallet files and
process logs remain in the printed run directory; do not publish that directory.

The test starts two nodes, checks each genesis hash, creates separate miner and
receiver wallets, and connects the nodes. It mines 101 blocks to mature the first
reward, transfers one coin using an explicit fee rate of 1 sat/vB, mines a
confirmation block, and verifies the receiver balance. It then stops both nodes,
restarts the receiver, and checks the persisted height, balance, and confirmation.
All nodes started by the test are stopped when it finishes. A successful run exits
with status 0 and writes `"passed": true` to the report. A failure returns status 1
and identifies the failing stage; inspect that run's local logs for details.

These coins exist only in this local development chain and have no assigned
market value. This test does not deploy a public mainnet, operate public seed
nodes, list a coin on an exchange, or establish consensus security. Public release
requires its own reviewed network configuration, independent nodes, reproducible
builds, and ongoing operation.
