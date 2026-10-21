# 飒币 Sarcoin

基于 Bitcoin Core **v31.1** 的独立开发链实验，币种标识 **sarcoin**。

**当前是开发版，尚未正式主网上线或公开发行。开发币不是 BTC，不承诺任何价值。**

## 当前实现

- 独立创世区块、P2P magic、端口、地址编码和数据目录。
- 两节点挖矿、同步和转账测试，以及重启后的余额检查。
- 仅启用改造后的 `-regtest` 开发网络，其他网络启动会报错。
- 创世输出为不可花费 OP_RETURN，没有分配给开发者的币或私钥。

| 参数 | 开发版值 |
|---|---|
| 网络 / 启动参数 | sarcoin-devnet-v1 / `-regtest` |
| 地址前缀 | `sarcrt1…` |
| 默认 P2P / RPC | 39444 / 39443 |
| 网络 magic | `73 61 72 d1` |
| Linux 数据目录 | `~/.sarcoin/sarcoin-devnet` |
| Windows 数据目录 | `%LOCALAPPDATA%/Sarcoin/sarcoin-devnet` |
| 共识 | SHA256d，开发用极低难度，关闭难度重调 |
| 区块奖励 / 减半 | 初始 50 币 / 每 210,000 块 |
| 精度 / 奖励成熟度 | 10⁻⁸ / 100 块 |
| 理论上限 | 按 Bitcoin 整数奖励衰减，小于 2,100 万枚 |

创世哈希：`062ff332a9aec7ee65b1e84f503aad64b2bafd4c17d98825bcb9173a5f8b0eb2`。
完整参数见 [genesis.json](sarcoin_tools/genesis.json)。这些是开发参数，不是最终主网规则。

## 编译和演示（Ubuntu / WSL）

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake pkgconf python3 libboost-dev libevent-dev libsqlite3-dev
bash sarcoin_tools/build.sh
python3 sarcoin_tools/genesis.py
python3 sarcoin_tools/devnet_demo.py --bindir build/bin --data-root sarcoin-local --report sarcoin-local/report.json
```

演示自动启动两个本机节点，挖 101 块使奖励成熟，跨节点转账 1 币，再挖一块确认，
关闭并重启接收节点，检查余额和交易。每次创建新目录，结束停止本次节点。
报告 `passed: true` 才算通过；钱包、cookie 和区块数据仅留本机并被 Git 忽略。

二进制暂沿用 `bitcoind`、`bitcoin-cli` 名称，P2P 客户端名为 `SarcoinDev`。
必须使用本源码编译的二进制，Bitcoin 官方安装包不包含飒币参数。GUI 尚未品牌适配。
原版测试中的 Bitcoin 固定参数需要移植，本项目尚未通过完整上游测试套件。

## 正式发行与来源

见 [发行路线](sarcoin_docs/LAUNCH.zh-CN.md) 和 [官方来源](sarcoin_docs/SOURCES.md)。
上传源码只是发布软件，正式发行还需要冻结主网共识、公开节点与挖矿、可验证的钱包和安装包。

上游为 [Bitcoin Core v31.1](https://github.com/bitcoin/bitcoin/releases/tag/v31.1)，
保留 [MIT / COPYING](COPYING) 和 [上游 README](README.upstream.md)。
GitHub 原生 fork：[wusar/sarcoin](https://github.com/wusar/sarcoin)，飒币开发代码在 `sarcoin-devnet` 分支，
从官方 `v31.1` 标签分出并保留上游历史。本机最初的离线导入基线来自官方源码包；它的提交号与线上原生 fork 不同。
