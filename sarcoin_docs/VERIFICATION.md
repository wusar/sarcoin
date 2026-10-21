# 开发版验收记录

日期：2026-10-20。实测环境：WSL2、Ubuntu 26.04 LTS、GCC 15.2、x86_64。

- 官方源码包 SHA256：通过；PGP 签名未独立验证。
- 定制 C++ 节点与 CLI 编译：通过，Release、无 GUI、无 IPC、钱包启用。
- 创世 Python 复算与编译节点实际创世：一致。
- 两个隔离本机节点：创建新钱包，挖101块、同步、转账1币、再挖1块确认：通过。
- 接收节点高度102，余额1.00000000，确认数至少1；停止后重启持久化：通过。
- 默认主网、testnet、testnet4、signet启动拒绝：通过。
- Bitcoin官方原版二进制被演示脚本的创世检查拒绝：通过（预期失败负例）。
- Python语法、Bash语法、Git whitespace diff：通过。
- 定制脚本与文档中的凭据标识扫描：无命中；演示数据目录被Git忽略。

对应机器可读记录：`verification.json`、`network-guard-verification.json`、
`upstream-rejection-verification.json`。交易ID仅为本地开发链的示例记录，不是公网交易。

初次测试发现：上游初始化帮助文本时也构造所有网络参数，所以拒绝其他网络的检查
必须放在实际 `SelectParams` 阶段。该问题已修复，最终端到端测试通过。

未完成：全套上游单元/功能测试、覆盖率审计、GUI适配、跨机器公网测试、生产安全审计、
正式主网参数与上线。

GitHub 发布：已在用户账号建立 [wusar/sarcoin](https://github.com/wusar/sarcoin) 原生 fork；
定制代码位于 `sarcoin-devnet`，基于 `v31.1`，不覆盖上游 `master` 历史。
网页发布不表示已完成正式主网或生产安全审计。
