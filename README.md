# 焊缝点云与标注数据集

截至2026-10-17，本仓库同步4批原始数据，共 **202个工件目录记录、2358个数据文件**，另附客户字段释义PDF。原压缩包、文件命名和内容保留；工件目录记录包含重复和修订版本，不等于202个独立工件家族。

## 数据范围

| 数据目录 | 工件目录记录 | 文件数 | 原始压缩包 | 下载位置 |
|---|---:|---:|---|---|
| 9月20日 | 22 | 296 | 9月20日.rar | [20261008 Release](https://github.com/G1ow9711/Dataset/releases/tag/dataset-20261008) |
| 标注数据20261004/真值 | 40 | 433 | 标注数据20261004.zip | [20261008 Release](https://github.com/G1ow9711/Dataset/releases/tag/dataset-20261008) |
| 129 | 130 | 1519 | 129.zip，按原字节拆为3卷 | [20261017 Release](https://github.com/G1ow9711/Dataset/releases/tag/dataset-20261017) |
| 真值数据（2026-10-15提供） | 10 | 110 | 真值数据（2026-10-15提供）.rar | [20261017 Release](https://github.com/G1ow9711/Dataset/releases/tag/dataset-20261017) |

逐个工件文件夹见 [DIRECTORY_INDEX.md](DIRECTORY_INDEX.md)。全部成员的相对路径、字节数、SHA256及CRC32见 [manifest.json](manifest.json)。[焊缝导出数据释义.pdf](焊缝导出数据释义.pdf) 保持原版本。

Git clone 只下载说明、清单、脚本和PDF；大体积原始数据放在上述Release。旧Release保留，10月17日只补充缺少的129批次和10月15日补充包。

## 下载与校验

需要Python 3.10或更高版本，无第三方依赖：

```bash
python download.py --output DataSet
```

已有正确文件会跳过。只补下载某一批：

```bash
python download.py --output DataSet --dataset 129
python download.py --output DataSet --dataset supplement
```

仅验证已下载的完整压缩包：

```bash
python download.py --output DataSet --verify-only
```

129.zip原文件为5,813,032,996字节。由于[GitHub单个Release附件须小于2 GiB](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases#storage-and-bandwidth-quotas)，它按原始字节拆为：
- 129.zip.part001：2,000,000,000字节
- 129.zip.part002：2,000,000,000字节
- 129.zip.part003：1,813,032,996字节

下载脚本逐卷验证后，按顺序自动合并为原始129.zip，并再次验证完整ZIP的SHA256。分卷不能单独解压。分卷保留在DataSet/.parts/129.zip，便于续传，因此合并时需为分卷和完整ZIP预留约11.63 GB空间。中断下载会保留.partial文件；服务器支持Range时可以续传。校验不符的已有完整文件不会被覆盖。

补充包在Release中的附件名为supplement-20261015.rar，脚本下载后恢复中文原名。旧两批仍从20261008 Release下载。

## 解压布局

- 第一批直接解压为9月20日/...。
- 第二批ZIP内部根目录为真值；为与清单对应，解压到标注数据20261004目录下。
- 129.zip内部根目录为129，包含AI、真值40-1001、真值50-1007。
- 补充RAR内部根目录为真值数据（2026-10-15提供）。

压缩包解压请使用支持对应ZIP/RAR格式的工具。本仓库不自动覆盖、合并同名工件，也保留原数据中的隐藏.samples目录。训练、验证、测试划分以项目冻结清单为准；目录数量不能代替去重后的样本数量。

## 完整性依据

- SHA256SUMS.txt：四个完整原始压缩包及PDF的SHA256。
- SHA256SUMS.parts.txt：新增Release三个ZIP分卷及补充RAR附件的SHA256。
- 旧两批沿用20261008已验证的成员校验值；本次与服务器逐路径、长度核对729个文件一致。
- 129的1519个ZIP成员全部流式读取，计算SHA256并核对ZIP CRC32、长度；服务器解压目录的路径集合和长度一致。
- 补充RAR的完整SHA256与项目已接入原包一致，全部110个成员流式读取并计算SHA256/CRC32；没有重新生成或修改原包。
- 上传后核对GitHub返回的每个新附件的字节数和SHA256。

这些是原始数据发布和传输校验，不构成标签正确性、模型准确率或验收通过的证明。仓库未额外授予数据使用许可。
