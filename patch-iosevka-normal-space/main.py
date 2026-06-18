#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "fonttools",
# ]
# ///
from pathlib import Path
import sys
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord

NEW_FAMILY = "Iosevka-Normal-Space"
TARGET_WIDTHS = {
    0x2009: 60,   # THIN SPACE
    0x200A: 20,   # HAIR SPACE
    0x202F: 80,   # NARROW NO-BREAK SPACE
    0x2006: 100,  # SIX-PER-EM SPACE
}

def patch_font(path: Path, output_dir: Path) -> None:
    print(f"patching {path.name}", flush=True)
    font = TTFont(path)
    
    # 修改字形宽度
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    for codepoint, width in TARGET_WIDTHS.items():
        glyph_name = cmap.get(codepoint)
        if glyph_name is None:
            continue
        _, lsb = hmtx[glyph_name]
        hmtx[glyph_name] = (width, lsb)
    
    # 修改字体名称
    name_table = font["name"]
    for record in name_table.names:
        try:
            text = record.toUnicode()
        except Exception:
            continue
        
        if "Iosevka" not in text:
            continue
        
        # 确定替换后的文本
        if record.nameID in (1, 4, 16):  # Family, Full font name, Preferred Family
            new_text = text.replace("Iosevka", NEW_FAMILY, 1)
        elif record.nameID == 6:  # PostScript name
            new_text = text.replace("Iosevka", NEW_FAMILY, 1).replace(" ", "")
        elif record.nameID in (2, 17):  # Subfamily, Preferred Subfamily
            new_text = text  # 保持不变
        else:
            new_text = text.replace("Iosevka", NEW_FAMILY, 1)
        
        # 正确设置 name 记录
        if new_text != text:
            record.string = new_text
    
    # 保存字体
    output = output_dir / path.name.replace("Iosevka", NEW_FAMILY, 1)
    font.save(output)
    print(f"  -> {output.name}", flush=True)

def main() -> None:
    if len(sys.argv) != 2:
        print("usage: patch.py <ttf-directory>")
        raise SystemExit(1)
    
    input_dir = Path(sys.argv[1]).resolve()
    if not input_dir.is_dir():
        print(f"not a directory: {input_dir}")
        raise SystemExit(1)
    
    output_dir = input_dir.with_name(
        input_dir.name + "-patched"
    )
    output_dir.mkdir(exist_ok=True)
    
    fonts = sorted(input_dir.glob("*.ttf"))
    print(f"input : {input_dir}")
    print(f"output: {output_dir}")
    print(f"fonts : {len(fonts)}")
    print()
    
    for font in fonts:
        patch_font(font, output_dir)
    
    print()
    print("done")

if __name__ == "__main__":
    main()