# 官方来源

核验日期：2026-10-20。读取 GitHub 官方 API、源码和 bitcoincore.org 原文。
当前内置网页搜索接口报错，未使用搜索摘要代替正文证据。

- [v31.1 release](https://github.com/bitcoin/bitcoin/releases/tag/v31.1)：2026-07-08 发布。
- [官方源码包](https://bitcoincore.org/bin/bitcoin-core-31.1/bitcoin-31.1.tar.gz)：
  SHA256 `50411d5b43c7e4c90099394759eb6c2add6e7c2dbe728840893d638b6fc6afc9`。
- [官方校验表](https://bitcoincore.org/bin/bitcoin-core-31.1/SHA256SUMS)、
  [PGP签名](https://bitcoincore.org/bin/bitcoin-core-31.1/SHA256SUMS.asc)。已校验下载包 SHA256，未独立校验 PGP 签名。
- [标签对应 commit](https://github.com/bitcoin/bitcoin/commit/9be056a8a72b624dae9623b2f7bded92c2a21c91)：
  `9be056a8a72b624dae9623b2f7bded92c2a21c91`。
- [MIT](https://github.com/bitcoin/bitcoin/blob/v31.1/COPYING)、
  [Linux构建](https://github.com/bitcoin/bitcoin/blob/v31.1/doc/build-unix.md)、
  [Windows构建](https://github.com/bitcoin/bitcoin/blob/v31.1/doc/build-windows.md)。
- [链参数](https://github.com/bitcoin/bitcoin/blob/v31.1/src/kernel/chainparams.cpp)、
  [RPC端口](https://github.com/bitcoin/bitcoin/blob/v31.1/src/chainparamsbase.cpp)、
  [奖励计算](https://github.com/bitcoin/bitcoin/blob/v31.1/src/validation.cpp)。
- [regtest说明](https://developer.bitcoin.org/examples/testing.html)、
  [钱包测试](https://github.com/bitcoin/bitcoin/blob/v31.1/test/functional/wallet_basic.py)。
- [估费问题 #32105](https://github.com/bitcoin/bitcoin/issues/32105)：私有链样本不足，演示显式设置 fee_rate。

v31.1 没有旧教程中的 checkpoints 字段。本链清空 assumeutxo，开发网最低链工作量和 assume-valid 为零。
Bitcoin 官方二进制仅作对照，不随飒币源码发布，也不作为定制链通过测试的证据。
