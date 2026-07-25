---
title: "邮件静态数据加密：LUKS 磁盘加密与 Maildir 存储保护"
source: "https://ztpop.net/kb/email-encryption-at-rest.html"
license: CC-BY 4.0
---

# 邮件静态数据加密：LUKS 磁盘加密与 Maildir 存储保护

## 概述

邮件静态数据加密保护存储在磁盘上的邮件数据在物理介质被窃取或未经授权访问时不被读取。TLS 加密保护的是传输过程中的数据，LUKS/dm-crypt 保护的是写入磁盘后的数据。LUKS2 是 Linux 标准磁盘加密方案，在内核层面透明加解密块设备数据，对上层应用（Postfix、Dovecot）完全透明，不需修改邮件服务配置。TPM 集成可实现服务器启动时的自动解密，避免每次重启都需手动输入密码。

## LUKS 磁盘加密配置

LUKS2 使用 dm-crypt 内核模块在块设备上创建加密层。配置数据分区加密的典型流程：使用 cryptsetup 格式化分区并设置密码短语，通过 Clevis 工具将密钥密封到 TPM 芯片中实现自动解锁。LUKS2 支持多密钥槽（默认 8 个），可同时配置密码短语解锁和 TPM 自动解锁，在 TPM 不可用时降级为手动密码输入。加密算法推荐 aes-xts-plain64，密钥长度 512 位。

```
# LUKS2 磁盘加密完整配置
cryptsetup luksFormat --type luks2 \
  --cipher aes-xts-plain64 --key-size 512 \
  --hash sha256 --pbkdf argon2id /dev/sdb1

# 打开加密卷
cryptsetup luksOpen /dev/sdb1 maildata
mkfs.xfs /dev/mapper/maildata
mount /dev/mapper/maildata /var/vmail

# TPM 自动解锁
yum install clevis clevis-luks clevis-tpm2
clevis luks bind -d /dev/sdb1 tpm2 '{"pcr_ids":"7"}'

# 验证自动解锁
cryptsetup luksClose maildata
cryptsetup luksOpen /dev/sdb1 maildata  # 应无需密码

# /etc/crypttab 配置开机自动挂载
echo "maildata /dev/sdb1 none _netdev,tpm2-device=auto" >> /etc/crypttab
```

## 密钥管理与轮换

LUKS 的密钥管理通过密钥槽（Key Slot）实现：每个密钥槽可存储独立的加密密钥，允许多个密码短语解密同一块加密分区。日常运维中，密钥轮换通过添加新密钥槽、验证新密钥可用后擦除旧密钥槽完成，无需在离线期间解密并重新加密所有数据。主密码短语离线安全保管，TPM 自动解锁用于日常运维，恢复密钥存储在硬件安全模块（HSM）或断开网络的气隔设备中。

```
# 密钥轮换操作
# 1. 添加新密钥槽
cryptsetup luksAddKey /dev/sdb1 --key-slot 1

# 2. 验证新密钥可用
cryptsetup luksOpen --test-passphrase --key-slot 1 /dev/sdb1

# 3. 擦除旧密钥槽
cryptsetup luksKillSlot /dev/sdb1 0

# 查看所有密钥槽状态
cryptsetup luksDump /dev/sdb1 | grep -A5 "Key Slot"

# 备份 LUKS 头部（密钥丢失后的最后恢复手段）
cryptsetup luksHeaderBackup /dev/sdb1 \
  --header-backup-file /secure/luks-header-backup.bin
```

## 踩坑与排错

TPM PCR 寄存器值在 BIOS 更新或内核升级后会改变，导致自动解锁失败——需在变更前解绑 Clevis 绑定，变更后重新绑定。加密分区的性能开销约为 3-8%（取决于 CPU 是否支持 AES-NI 硬件加速），生产部署前应使用 fio 在加密卷上实测 I/O 性能下降幅度。加密卷头部损坏将导致所有数据不可恢复——必须将 luksHeaderBackup 备份到独立于服务器的安全位置。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-encryption-at-rest.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
