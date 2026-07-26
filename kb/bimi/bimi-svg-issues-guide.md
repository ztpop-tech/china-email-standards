---
title: "BIMI SVG 问题排查：确保 Tiny-PS 合规"
source: "https://ztpop.net/kb/bimi-svg-issues-guide.html"
license: CC-BY 4.0
---

# BIMI SVG 问题排查：确保 Tiny-PS 合规

## 概述

导致 SVG 文件未通过 BIMI 验证工具 Tiny-PS 合规性检查的原因很多，大多数问题源于 BIMI 要求所有 Logo 图像必须符合 SVG Tiny-PS 标准。

## 什么是 SVG Tiny-PS？

SVG Tiny PS（Portable/Secure，便携/安全）是 SVG（可缩放矢量图形）规范的精简子集，专为在资源受限环境中提供轻量、安全、可移植的矢量图形显示而设计。它保留了渲染可缩放图像所需的核心功能，同时移除了可能带来安全风险或需要大量处理能力的复杂特性。其简洁性和安全性保障了图形在不同平台上的一致、安全渲染。

## SVG Tiny-PS 基础

将 SVG 文件更新为符合 SVG Tiny-PS 标准时，需考虑设备兼容性、性能效率及标准限制。SVG Tiny-PS 仅支持 SVG 元素和属性的有限子集。

### 支持的元素

* 基本形状（`<rect>`、`<circle>`、`<line>`、`<polyline>`、`<polygon>`、`<ellipse>`）
* 基本文本元素（`<text>`、`<tspan>`）
* 简单渐变定义（线性渐变和径向渐变）
* 路径数据（`<path>`）应简化以降低复杂度

### 不支持的标签（需移除）

* 滤镜和效果
* 嵌入图像
* 脚本和动画（`<script>`、`<animate>`、`<set>`、`<animateTransform>` 等）

## 常见错误与解决方案

### 错误 1：文件大小超限

假设你已做对了所有步骤——构建了 Tiny-PS SVG、托管了它、发布了 BIMI 记录——然而遇到了类似以下的错误消息：

```
SVG_FETCH_ERROR: Could not fetch SVG
(Size of response body exceeds the maximum allowed of 65535)
```

此错误表明你的 SVG 文件超过了 Tiny-PS 标准设定的最大大小限制 32KB（32,768 字节）。注意，某些系统可能会设置更高的限制以提供更多灵活性。首要目标是减小 SVG 文件大小，同时保持其完整性和外观。

#### 简化矢量图形

SVG Tiny-PS 专为小型设备设计，简洁是关键。

* **减少节点数量**：简化路径，减少矢量图形中的节点（锚点）数量。可使用矢量图形软件中的路径简化工具实现。
* **限制颜色和渐变**：使用有限的调色板，避免复杂渐变。SVG Tiny-PS 仅支持简单的线性渐变和径向渐变。

#### 优化 SVG 以符合 Tiny-PS

* **使用支持的功能**：确保图形仅使用 SVG Tiny-PS 支持的元素和属性。例如，使用基本形状（矩形、圆形、线条）和简单文本格式。
* **避免不支持的标签**：不使用滤镜、动画和脚本等元素。

#### 验证与优化 SVG 文件

* **SVG 验证**：使用 SVG 验证工具（如 BIMI Group 的 SVG Assistant）确认文件符合规范。
* **文件优化**：使用 SVGO（SVG Optimizer）等工具清理 SVG 代码、移除不必要的元数据、减小文件大小。

### 错误 2：栅格图像嵌入

如果文件大小不是问题，但验证仍然失败，可能是因为 SVG 中嵌入了栅格图像（如 JPEG、PNG）。这也需要修正才能通过验证。你需要将栅格图像转换为矢量格式——这个过程称为矢量化（Vectorization）或描摹（Tracing）。

推荐工具：

* **Adobe Illustrator**：使用"图像描摹"（Image Trace）功能将栅格图像转换为矢量路径
* **Inkscape**：使用"描摹位图"（Trace Bitmap）工具获得类似效果

确保将新生成的文件保存为优化后的 SVG 格式，以使用最简洁的代码渲染图像，并移除大部分不支持的标签。

#### 国内场景补充

国内 BIMI 实施者在准备 SVG Logo 时，建议遵循以下流程：

1. 向设计师索取原始矢量源文件（AI/EPS/CDR 格式），而非从 PNG/JPG 转换
2. 使用 SVGO 或 SVGOMG 在线工具压缩代码
3. 通过 BIMI Group 的 [SVG Assistant Tool](https://bimigroup.org/bimi-svg-assistant-tool/) 验证合规性
4. 确保 SVG 文件托管在 HTTPS 服务器上

---

*本文章由 [ztpop.net 知识库](https://ztpop.net/kb/bimi-svg-issues-guide.html) 镜像发布。采用 [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，可自由引用，仅需标注来源。*
