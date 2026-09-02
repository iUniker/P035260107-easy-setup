# MZP351HV00TR 无损安装工具

这是 MazerPi 3.51 英寸 480x320 DPI 电阻触摸屏的独立优化仓库，面向已经配置好自己系统的客户。

安装器不会替换操作系统或内核，不使用 DKMS，也不会修改客户的软件、网络和用户数据。它只启用 Raspberry Pi OS 已经自带的驱动和 Device Tree Overlay。

美国客户使用的说明见 [English Quick Start](QUICK_START.md)；工程实测见 [Engineering Validation Plan](docs/ENGINEERING-TEST-PLAN.md)。

## 只保留两种客户安装方式

### 1. 在线安装（主推）

在能联网的树莓派里打开终端，或者通过 SSH 登录，运行：

```bash
curl -fsSL https://raw.githubusercontent.com/iUniker/P035260107-easy-setup/main/install.sh | sudo bash -s -- --reboot
```

脚本会检查兼容性，用时间戳备份原有 `config.txt`，只加入屏幕需要的配置，然后自动重启。

### 2. 下载 ZIP（树莓派无法联网）

在任意可以联网的设备上[下载 ZIP](https://github.com/iUniker/P035260107-easy-setup/archive/refs/heads/main.zip)，传到树莓派并解压。在解压文件夹内打开终端，运行：

```bash
sudo bash install.sh --reboot
```

ZIP 方式与在线安装执行相同的检查和配置，安装时不要求树莓派访问 GitHub。

## 安装器会做什么

1. 自动找到 Raspberry Pi 启动分区。
2. 检查树莓派型号、所需 Overlay 和现有冲突配置。
3. 先用时间戳备份原有 `config.txt`。
4. 在启动分区放入 `mzp351hv00tr.txt`。
5. 只在原 `config.txt` 中加入一个有明确起止标记的配置块。

安装器不会覆盖整个 `config.txt`；重复执行也不会重复追加。

## 卸载和诊断

在已下载并解压的文件夹里运行：

```bash
sudo bash uninstall.sh --reboot
sudo bash diagnose.sh | tee mzp351-diagnostic.txt
```

卸载只删除安装器自己管理的配置块，并保留备份。诊断报告不会收集密码、Wi-Fi 凭证或用户文件。

## 重要兼容性说明

- 目标设备为 Raspberry Pi Zero、Zero W/WH 和 Zero 2 W/2 WH，使用提供现代 KMS Overlay 的 Raspberry Pi OS。
- 其他发行版和自定义内核在对应版本完成实测前不承诺支持。
- 屏幕占用 25 个 GPIO；其他 DPI 屏、ADS7846、SPI0、GPIO18 或 GPIO27 设备可能冲突。
- 如果旧说明已经引用 `mzp351hv00tr-new.txt` 或 `mzp351hv00tr-old.txt`，需要先移除旧 include 配置。
- 完成实物时序验证前，保留原厂 12 MHz 参数。
