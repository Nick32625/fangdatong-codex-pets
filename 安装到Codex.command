#!/bin/bash
set -euo pipefail

PACKAGE_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PET_ROOT="${CODEX_HOME:-$HOME/.codex}/pets"
PET_IDS=(khalil-suit-handdrawn khalil-15live-handdrawn khalil-blue-handdrawn khalil-farmer-handdrawn)
VERIFY_ONLY=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --verify-only) VERIFY_ONLY=true; shift ;;
    --pet-dir)
      if [[ $# -lt 2 || -z "$2" || "$2" != /* ]]; then
        echo '--pet-dir 需要一个绝对目录路径。' >&2
        exit 2
      fi
      PET_ROOT="$2"
      shift 2
      ;;
    *) echo "无法识别的选项：$1" >&2; exit 2 ;;
  esac
done

cd "$PACKAGE_DIR"
if [[ ! -f SHA256SUMS ]]; then
  echo '安装包尚未完整，缺少校验清单。请使用已完成的分享包。' >&2
  exit 1
fi
shasum -a 256 -c SHA256SUMS
for pet_id in "${PET_IDS[@]}"; do
  [[ -f "$PACKAGE_DIR/$pet_id/pet.json" && -f "$PACKAGE_DIR/$pet_id/spritesheet.webp" ]] || {
    echo "缺少桌宠文件：$pet_id" >&2
    exit 1
  }
done

if [[ "$VERIFY_ONLY" == true ]]; then
  echo '安装包完整性检查通过，尚未安装。'
  exit 0
fi

mkdir -p "$PET_ROOT"
for pet_id in "${PET_IDS[@]}"; do
  destination="$PET_ROOT/$pet_id"
  if [[ -e "$destination" ]]; then
    mkdir -p "$PACKAGE_DIR/安装前备份"
    backup_root="$(mktemp -d "$PACKAGE_DIR/安装前备份/backup.XXXXXX")"
    cp -R "$destination" "$backup_root/$pet_id"
    echo "已有同名桌宠已备份至：$backup_root/$pet_id"
  fi
  mkdir -p "$destination"
  cp "$PACKAGE_DIR/$pet_id/spritesheet.webp" "$destination/spritesheet.webp"
  cp "$PACKAGE_DIR/$pet_id/pet.json" "$destination/pet.json"
  echo "已安装：$pet_id"
done

echo
echo '四款方小同已安装。请在 Codex 的桌宠设置中点“刷新”，再选择喜欢的款式。'
echo "安装位置：$PET_ROOT"
