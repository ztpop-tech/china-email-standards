---
title: "邮件存储 I/O 基准测试：fio/iostat 与 RAID 选型"
source: "https://ztpop.net/kb/email-storage-io-benchmark.html"
license: CC-BY 4.0
---

# 邮件存储 I/O 基准测试：fio/iostat 与 RAID 选型

## 概述

邮件系统的存储 I/O 模式以大量小文件的随机读写为主。Maildir 格式下每封邮件为一个独立文件，写入时先创建 tmp 目录下的临时文件再原子移动到 new 目录，读取时按需打开邮件文件读取正文和附件。这种小文件的创建/移动/读取模式要求存储系统具备高 IOPS 和高随机写入吞吐能力。选择存储方案时需根据用户规模估算峰值 IOPS 需求，再通过 fio 和 iostat 工具进行基准测试。

## fio 模拟 Maildir I/O 模式

fio 是一个灵活的开源 I/O 基准测试工具，支持模拟多种 I/O 工作负载。邮件系统的 I/O 特征为：90% 的操作 ≤16KB，60% 为随机写操作，40% 为随机读操作。使用 fio 的 randrw 模式设置 rwmixread=40 可模拟邮件系统的混合读写比例，文件大小分布采用正态分布模拟不同大小邮件的真实场景。测试文件数量应远大于实际邮箱数以避免缓存命中偏高。

```
# fio 模拟 Maildir 存储工作负载
fio --name=maildir-sim --rw=randrw --rwmixread=40 \
    --bs=4k-16k --size=10G --numjobs=8 --runtime=300 \
    --time_based --ioengine=libaio --direct=1 \
    --filename=/mnt/mailstore/fio-test \
    --group_reporting

# 高并发小文件写入测试
fio --name=peak-write --rw=randwrite --bs=4k \
    --size=1G --numjobs=16 --nrfiles=10000 \
    --filesize=4k-256k --runtime=120 --time_based \
    --directory=/mnt/mailstore/fio-multi/ --group_reporting
```

## iostat 实时监控与 RAID 选型

iostat 可实时监控存储设备的 IOPS、吞吐量和平均等待时间（await）。邮件系统关键指标：iowait 不应超过 10%，await 应控制在 10ms 以内（SSD）或 25ms 以内（HDD）。RAID 级别选择直接影响邮件写入性能和冗余能力：RAID 10 提供最佳随机读写性能（无校验计算开销），RAID 5/6 的写入惩罚在大量小文件写入场景下尤为显著。裸盘直通配合应用层复制可在邮件集群中替代硬件 RAID。

```
# 持续监控存储 I/O 状态
iostat -x 2 30 | tee /tmp/io-mon.log

# 重点观察指标
iostat -x 1 | awk 'NR>6 {printf "dev=%s r/s=%d w/s=%d await=%.1f\n",$1,$4,$5,$10}'

# 磁盘延时分布
ioping -c 100 /mnt/mailstore/

# RAID 10 创建示例（4 块 SSD）
mdadm --create /dev/md0 --level=10 --raid-devices=4 \
      /dev/sdb /dev/sdc /dev/sdd /dev/sde
mkfs.xfs -d su=64k -d sw=4 /dev/md0
mount -o noatime,nodiratime,logbsize=256k /dev/md0 /var/vmail
```

## 踩坑与排错

SSD 写入寿命（DWPD/TBW）在邮件系统高写入场景下可能被低估——每日百万级邮件写入可产生数 TB 的写入放大，建议选用企业级 SSD（≥1 DWPD）并开启 TRIM。ext4 文件系统在单目录超过 10 万文件时性能急剧下降，Maildir 哈希子目录设计可缓解但需确保 hash 深度足够。fio 测试中 benchmark-size 建议为实际邮件分区大小的 2 倍以覆盖文件系统缓存的影响。

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/email-storage-io-benchmark.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
