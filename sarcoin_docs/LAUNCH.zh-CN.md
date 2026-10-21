# 飒币发行路线

当前交付为独立开发链原型：有自己的创世和地址，借用 regtest 运行模式；没有公网主网和预售。

## 1. 冻结发行规则

名称已定为“飒币 / sarcoin”。主网前需确定总量、初始奖励、出块时间、减半周期、挖矿算法、
初始难度、难度调整、是否预挖和上线时间。本次默认采用 Bitcoin 风格奖励，无开发者预分配；
这些开发默认值不表示最终经济规则已经批准。

当前目标间隔字段是600秒，但允许即时生成块且不调难，不能据此推算实际发行时间。
公开 SHA256d 新链算力很小时易被既有算力重组，需要专门评估网络安全。

## 2. 实现主网

在 `src/kernel/chainparams.cpp` 实现独立主网参数，重新生成主网创世和有效 PoW，
设定生产用难度与重调规则、magic、P2P/RPC端口、地址编码和激活规则。
清理 Bitcoin 种子、历史 BIP34Hash、minimum chain work、assume-valid 和 assumeutxo。
当前开发网创世不是主网创世，开发币余额不会自动带入主网。
同步适配 `src/chainparamsbase.cpp`、钱包链标识、GUI、帮助和显示单位。

## 3. 独立测试网

部署至少两个独立可达的节点。本次仅为同一台电脑上的两个进程。
测试跨机器同步、挖矿、转账、重启、重组、调难、减半与钱包备份恢复，
移植上游测试中固定的创世、地址与参数，建立持续测试。
RPC保持本机绑定，对其他用户开放的是P2P节点；不要裸露钱包RPC。

## 4. GitHub发布

当前仓库：[wusar/sarcoin](https://github.com/wusar/sarcoin)，开发分支 `sarcoin-devnet`。
原生 fork 已创建，以下命令保留给后续维护；本机离线导入提交与线上上游历史不相同。

创建 `bitcoin/bitcoin` 的原生 fork，命名 `sarcoin`，保留上游历史和MIT版权。
本地基线来自经校验的官方源码包，不能称为完整上游 Git 历史或已完成 GitHub 原生 fork。
登录后在新克隆的原生 fork 中，从 v31.1 建分支应用本地补丁，不强推导入根提交覆盖上游：

```bash
git fetch https://github.com/bitcoin/bitcoin.git tag v31.1
git switch -c sarcoin-devnet v31.1
git apply --check /path/to/sarcoin-devnet.patch
git apply /path/to/sarcoin-devnet.patch
git add .
git commit -m "Add isolated Sarcoin development chain and demo"
git push -u origin sarcoin-devnet
```

先 `--check`，补丁仅含定制修改，不含钱包、二进制或发行包生成文件。
开发版使用明确的 devnet 标签。主网验证通过后，从自己的源码构建安装包，
附 commit、构建说明、SHA256和签名；不可把Bitcoin原版安装包改名当飒币发行。

## 5. 启动主网

公开上线时间、创世与发行规则，启动种子节点和矿工，让外部用户独立编译、连接并验证奖励。
准备运维、漏洞响应与升级流程。上传源码、上链、上交易所、获得市场价值是分别独立的事项；
后两者不会因 fork 自动实现。
