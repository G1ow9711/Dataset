# 焊缝点云与标注数据集

本仓库同步两个原始数据集及其导出字段释义。原文件内容、命名和目录结构均保留。

## 下载

两个压缩包位于 [dataset-20261008 Release](https://github.com/G1ow9711/Dataset/releases/tag/dataset-20261008)。Git clone 仅下载说明、清单和 PDF；数据集请从 Release 下载。

| 文件 | 字节数 | 用途 |
|---|---:|---|
| [9月20日.rar](https://github.com/G1ow9711/Dataset/releases/download/dataset-20261008/9.20.rar) | 889924675 | 第一批数据集 |
| [标注数据20261004.zip](https://github.com/G1ow9711/Dataset/releases/download/dataset-20261008/20261004.zip) | 2037074114 | 第二批标注数据集 |
| [焊缝导出数据释义.pdf](焊缝导出数据释义.pdf) | 659574 | 标签和字段释义，以 PDF 原文为准 |

## 文件完整性

`SHA256SUMS.txt` 记录三个原文件的 SHA256。`manifest.json` 记录两个解压目录内所有文件的相对路径、字节数、SHA256 和 CRC32。

第一批数据集含 296 个文件，解压后 4820370764 字节；第二批含 433 个文件，解压后 7599598154 字节。保留原数据中的隐藏 `.samples` 目录。

RAR 已逐成员核对 SHA256 和长度；ZIP 已逐成员核对 CRC32 和长度。Release 上传完成后，另用 GitHub 返回的附件 SHA256 核对压缩包。

解压布局为 `9月20日/...`，以及第二批的 `真值/...`。为对应清单，可把第二批解压到 `标注数据20261004` 文件夹下。

## 下载并校验

运行 `python download.py --output DataSet`，脚本下载两个 Release 压缩包及仓库 PDF，并验证 SHA256。需要 Python 3.10 或更高版本。

本次同步日期：2026-10-08。仓库未额外授予数据使用许可。

GitHub 会规范化 Release 附件名称；`download.py` 按校验清单下载，并保存为原始中文文件名。
