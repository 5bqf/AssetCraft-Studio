#!/bin/bash
# AssetCraft Studio - 分批次自动交付脚本
# 用法: bash deliver.sh <batch_number>
# 从 .delivery/batch_<N>/ 复制文件到工作区并提交

set -e

BATCH="$1"
if [ -z "$BATCH" ]; then
    echo "用法: bash deliver.sh <batch_number>"
    exit 1
fi

BATCH_DIR=".delivery/batch_${BATCH}"
if [ ! -d "$BATCH_DIR" ]; then
    echo "错误: 批次目录 $BATCH_DIR 不存在"
    exit 1
fi

echo "=== AssetCraft Studio 交付批次 $BATCH ==="

# 复制批次文件到工作区
cp -r "$BATCH_DIR"/* . 2>/dev/null || true

# 创建 feature 分支 (仅批次2、3需要)
BRANCH=""
case "$BATCH" in
    2) BRANCH="feature/generator-module" ;;
    3) BRANCH="feature/design-coordinator" ;;
    4) BRANCH="feature/asset-exporter" ;;
esac

if [ -n "$BRANCH" ]; then
    git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"
    git add -A
    git commit -m "$(cat .delivery/commit_msg_${BATCH}.txt)"
    echo "已提交到分支: $BRANCH"
    git checkout main
    git merge "$BRANCH" --no-ff -m "$(cat .delivery/merge_msg_${BATCH}.txt)"
    echo "已合并到 main"
else
    git add -A
    git commit -m "$(cat .delivery/commit_msg_${BATCH}.txt)"
    echo "已提交到 main"
fi

echo "=== 批次 $BATCH 交付完毕 ==="
