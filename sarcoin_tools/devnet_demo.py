#!/usr/bin/env python3
"""Run a two-node Sarcoin development-chain smoke test with no third-party modules."""

import argparse
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
from decimal import Decimal


def eventually(check, description, timeout=90):
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        try:
            result = check()
            if result:
                return result
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            last_error = exc
        time.sleep(0.2)
    raise RuntimeError("Timed out waiting for " + description) from last_error


class Node:
    def __init__(self, daemon, cli, directory, rpc_port, p2p_port):
        self.daemon = daemon
        self.cli = cli
        self.directory = directory
        self.rpc_port = rpc_port
        self.p2p_port = p2p_port
        self.process = None
        self.log = None
        self.starts = 0
        self.directory.mkdir()

    def rpc(self, method, *args, wallet=None, named=False):
        command = [str(self.cli), "-regtest", "-datadir=" + str(self.directory),
                   "-rpcconnect=127.0.0.1", "-rpcport=" + str(self.rpc_port)]
        if wallet:
            command.append("-rpcwallet=" + wallet)
        if named:
            command.append("-named")
        command += [method] + [str(arg) for arg in args]
        result = subprocess.run(command, capture_output=True, text=True, timeout=20,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if result.returncode:
            # Do not include command arguments or RPC diagnostics in the JSON report.
            raise RuntimeError("RPC failed: " + method)
        output = result.stdout.strip()
        try:
            return json.loads(output, parse_float=Decimal)
        except json.JSONDecodeError:
            return output

    def start(self):
        self.starts += 1
        self.log = (self.directory / ("process-%d.log" % self.starts)).open("ab")
        command = [str(self.daemon), "-regtest", "-server=1",
                   "-datadir=" + str(self.directory), "-listen=1", "-connect=0",
                   "-bind=127.0.0.1:" + str(self.p2p_port),
                   "-port=" + str(self.p2p_port), "-rpcbind=127.0.0.1",
                   "-rpcallowip=127.0.0.1", "-rpcport=" + str(self.rpc_port),
                   "-dnsseed=0", "-fixedseeds=0", "-listenonion=0",
                   "-discover=0", "-natpmp=0", "-printtoconsole=1"]
        self.process = subprocess.Popen(command, stdout=self.log, stderr=subprocess.STDOUT,
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

        def ready():
            if self.process.poll() is not None:
                raise subprocess.CalledProcessError(self.process.returncode, "bitcoind")
            return self.rpc("getblockchaininfo")

        eventually(ready, "node RPC startup")

    def stop(self):
        process = self.process
        if process is None:
            return
        try:
            if process.poll() is None:
                try:
                    self.rpc("stop")
                except (RuntimeError, subprocess.TimeoutExpired, OSError):
                    pass
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    # Only terminate the exact child created by this test.
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=10)
        finally:
            if self.log is not None:
                self.log.close()
                self.log = None
            self.process = None


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bindir", required=True, type=Path,
                        help="Directory containing the custom bitcoind and bitcoin-cli binaries")
    parser.add_argument("--data-root", required=True, type=Path,
                        help="Parent directory; a new random run directory is always created")
    parser.add_argument("--report", required=True, type=Path, help="JSON result file")
    args = parser.parse_args()
    report = {"passed": False, "network": "sarcoin-devnet", "stage": "preflight"}
    nodes = []
    reservations = []
    exit_code = 1
    try:
        manifest = json.loads((Path(__file__).parent / "genesis.json").read_text(encoding="utf-8-sig"))
        expected = manifest.get("genesis_hash")
        require(isinstance(expected, str) and re.fullmatch(r"[0-9a-fA-F]{64}", expected),
                "genesis.json must contain a 64-character genesis_hash")
        expected = expected.lower()
        report["genesis"] = expected
        suffix = ".exe" if os.name == "nt" else ""
        daemon = (args.bindir / ("bitcoind" + suffix)).resolve()
        cli = (args.bindir / ("bitcoin-cli" + suffix)).resolve()
        require(daemon.is_file() and cli.is_file(), "Custom node binaries were not found")
        args.data_root.mkdir(parents=True, exist_ok=True)
        run_directory = Path(tempfile.mkdtemp(prefix="sarcoin-demo-", dir=args.data_root)).resolve()
        # Reserve four independent loopback ports until each node is launched.
        ports = []
        for _ in range(4):
            reserved = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            reserved.bind(("127.0.0.1", 0))
            reservations.append(reserved)
            ports.append(reserved.getsockname()[1])
        a = Node(daemon, cli, run_directory / "node-a", ports[0], ports[1])
        b = Node(daemon, cli, run_directory / "node-b", ports[2], ports[3])
        nodes = [a, b]
        print("Preserved run directory:", run_directory, flush=True)
        report["stage"] = "startup"
        for index, node in enumerate(nodes):
            for reserved in reservations[index * 2:index * 2 + 2]:
                reserved.close()
            node.start()
            require(node.rpc("getblockhash", 0) == expected,
                    "Genesis mismatch: use the custom Sarcoin binaries")
            require(node.rpc("getblockcount") == 0, "Expected a fresh chain")
        report["version"] = a.rpc("getnetworkinfo")["subversion"]
        a.rpc("createwallet", "wallet_name=miner", "load_on_startup=true", named=True)
        b.rpc("createwallet", "wallet_name=receiver", "load_on_startup=true", named=True)
        mining_address = a.rpc("getnewaddress", wallet="miner")
        receiver_address = b.rpc("getnewaddress", wallet="receiver")
        require(mining_address.startswith("sarcrt1") and receiver_address.startswith("sarcrt1"),
                "Unexpected address prefix: expected sarcrt1")
        report["stage"] = "connect"
        a.rpc("addnode", "127.0.0.1:" + str(b.p2p_port), "onetry")
        eventually(lambda: a.rpc("getconnectioncount") >= 1 and b.rpc("getconnectioncount") >= 1,
                   "two-node connection")
        report["stage"] = "mine"
        hashes = a.rpc("generatetoaddress", 101, mining_address)
        require(len(hashes) == 101, "Did not mine 101 blocks")
        eventually(lambda: b.rpc("getblockcount") == 101, "receiver block synchronization")
        require(a.rpc("getbalance", wallet="miner") >= Decimal("1"), "Coinbase did not mature")
        report["stage"] = "transfer"
        txid = a.rpc("sendtoaddress", "address=" + receiver_address, "amount=1", "fee_rate=1",
                     wallet="miner", named=True)
        report["txid"] = txid
        require(len(a.rpc("generatetoaddress", 1, mining_address)) == 1, "Confirmation mining failed")
        eventually(lambda: b.rpc("getblockcount") == 102, "confirmation block synchronization")

        def received():
            balance = b.rpc("getbalance", wallet="receiver")
            transaction = b.rpc("gettransaction", txid, wallet="receiver")
            return balance == Decimal("1") and transaction.get("confirmations", 0) >= 1

        eventually(received, "confirmed receiver balance")
        report["confirmations"] = b.rpc("gettransaction", txid, wallet="receiver")["confirmations"]
        report["balance"] = str(b.rpc("getbalance", wallet="receiver"))
        report["height"] = b.rpc("getblockcount")
        report["stage"] = "restart"
        a.stop()
        b.stop()
        b.start()
        require(b.rpc("getblockhash", 0) == expected, "Genesis mismatch after restart")
        eventually(lambda: "receiver" in b.rpc("listwallets"), "receiver wallet autoload")
        require(b.rpc("getblockcount") == report["height"], "Chain height changed after restart")
        require(b.rpc("getbalance", wallet="receiver") == Decimal("1"),
                "Receiver balance was not preserved")
        require(b.rpc("gettransaction", txid, wallet="receiver")["confirmations"] >= 1,
                "Transaction confirmation was not preserved")
        report["restart_verified"] = True
        report["passed"] = True
        report["stage"] = "complete"
        exit_code = 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as exc:
        report["error_type"] = type(exc).__name__
        print("Test failed during " + report["stage"] + ": " + str(exc), file=sys.stderr)
    finally:
        for reserved in reservations:
            reserved.close()
        for node in reversed(nodes):
            try:
                node.stop()
            except (OSError, subprocess.SubprocessError) as exc:
                report["passed"] = False
                report["cleanup_error_type"] = type(exc).__name__
                exit_code = 1
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False), flush=True)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
