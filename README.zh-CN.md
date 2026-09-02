# MZP351HV00TR 无损安装工具

这是 MazerPi 3.51 英寸 480x320 DPI 电阻触摸屏的独立优化仓库，面向已经配置好自己系统的客户。

本工具不会替换操作系统，不会替换内核，不使用 DKMS，也不会修改客户的软件、网络和用户数据。它只启用系统已经自带的内核驱动和 Device Tree Overlay。

## 安装器会做什么

1. 自动找到 Raspberry Pi 启动分区。
2. 检查系统是否自带所需的 Overlay。
3. 先用时间戳备份客户原有的 `config.txt`。
4. 在启动分区放入独立的 `mzp351hv00tr.txt`。
5. 只在原 `config.txt` 末尾加入一个有明确开始和结束标记的配置块。

安装器不会覆盖整个 `config.txt`；重复执行也不会重复追加。

## 在客户现有系统中安装

下载并解压本仓库，然后执行：

```bash
cd P035260107-easy-setup
sudo bash install.sh --reboot
```

安装器会自动识别新系统的 `/boot/firmware/config.txt` 和旧路径 `/boot/config.txt`，并以实际 Overlay 文件判断兼容性，而不只是判断系统名称。

## 不启动树莓派，直接配置现有 SD 卡

离线安装只修改小容量 FAT 启动分区，不会挂载或修改 Linux 系统分区。

### Windows

插入 SD 卡后，双击 `install-windows.cmd`。工具会自动查找 Raspberry Pi 启动分区。

对应的 PowerShell 命令是：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-offline.ps1
```

如果电脑上有多个可能的启动分区，请指定盘符：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-offline.ps1 E:
```

### macOS

```bash
bash install.sh --boot-dir /Volumes/bootfs
```

### Linux 电脑

```bash
bash install.sh --boot-dir /media/$USER/bootfs
```

成功后请安全弹出 SD 卡。

## 卸载

已经启动的 Raspberry Pi：

```bash
sudo bash uninstall.sh --reboot
```

离线 SD 卡：

```bash
bash uninstall.sh --boot-dir /path/to/bootfs
```

卸载器只移除自己管理的配置块。屏幕配置片段会保留为带时间戳的 `.disabled-*` 文件，同时再生成一份 `config.txt` 备份。

Windows 离线 SD 卡可以直接双击 `uninstall-windows.cmd`。

## 故障诊断

```bash
sudo bash diagnose.sh | tee mzp351-diagnostic.txt
```

诊断报告包含型号、内核、Overlay、DRM、触摸和背光状态，不会收集密码、Wi-Fi 凭证或用户文件。

## 重要兼容性说明

- 目标设备为 Raspberry Pi Zero、Zero W/WH 和 Zero 2 W/2 WH，系统需要提供现代 KMS 和相关 Overlay。
- 屏幕占用 25 个 GPIO。如果客户已经配置了其他 DPI 屏、ADS7846 或冲突的 GPIO，安装器会停止，不会静默覆盖。
- 如果以前已按原说明书引用 `mzp351hv00tr-new.txt` 或 `mzp351hv00tr-old.txt`，需要先从 `config.txt` 删除原 include 行。
- 在实物屏幕完成新时序验证前，本仓库保留原厂的 12 MHz 参数。

设计原因和待完成的实机验证见 [技术说明](docs/TECHNICAL-NOTES.md)。
