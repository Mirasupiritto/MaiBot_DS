"""Import the copied EAC dafeiyu emoji pack into MaiBot without VLM calls."""

from __future__ import annotations

import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

from sqlmodel import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.common.database.database import get_db_session
from src.common.database.database_model import ImageType, Images
from src.common.utils.image_path import serialize_stored_image_path


SOURCE_DIR = PROJECT_ROOT / "data" / "imports" / "dafeiyu-001" / "memes"
TARGET_DIR = PROJECT_ROOT / "data" / "emoji"

TAG_DESCRIPTIONS = {
    "angry": "生气,恼火,气鼓鼓",
    "baka": "嫌弃,笨蛋,吐槽",
    "color": "花痴,喜欢,心动",
    "confused": "疑惑,问号,不明白",
    "cpu": "加班,忙碌,脑袋过载",
    "daily": "日常,悠闲,随意",
    "fool": "拒绝,不要,制止",
    "givemoney": "求打赏,要钱,期待",
    "happy": "开心,高兴,得意",
    "like": "比心,喜欢,感谢",
    "meow": "猫爪动作,卖萌,招手",
    "morning": "早安,打招呼,元气",
    "sad": "难过,委屈,求饶",
    "see": "震惊,围观,看见",
    "shy": "害羞,脸红,偷看",
    "sigh": "无语,叹气,无奈",
    "sleep": "睡觉,困倦,晚安",
    "surprised": "惊吓,意外,吃惊",
    "work": "躺平,摸鱼,不想工作",
}

STEM_DESCRIPTIONS = {
    "bixin": "比心",
    "buyao": "不要",
    "deyi": "得意",
    "ganfan": "干饭,白米饭",
    "haixiu": "害羞",
    "huachi": "花痴",
    "jiaban": "加班",
    "jiazai": "加载中",
    "maozhua": "猫爪动作",
    "ok": "OK,赞同",
    "piaole": "飘了,得意忘形",
    "qiurao": "求饶",
    "shengqi": "生气",
    "shuijiao": "睡觉",
    "tangping": "躺平",
    "toukan": "偷看",
    "wenhao": "问号,疑惑",
    "wuyu": "无语",
    "xia": "吓到",
    "xianqi": "嫌弃",
    "yaoqian": "要钱,求打赏",
    "yun": "晕倒,头晕",
    "zaoshanghao": "早上好,早安",
    "zhenjing": "震惊",
}


def build_description(image_path: Path) -> str:
    tag = image_path.parent.name.lower()
    stem = image_path.stem.lower()
    parts = [STEM_DESCRIPTIONS.get(stem, ""), TAG_DESCRIPTIONS.get(tag, tag), "蓝色大肥鱼,虎鲸娘"]
    return ",".join(part for part in parts if part)


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    image_paths = sorted(path for path in SOURCE_DIR.rglob("*") if path.is_file())
    if not image_paths:
        raise RuntimeError(f"No emoji images found in {SOURCE_DIR}")

    imported = 0
    updated = 0
    with get_db_session() as session:
        for source_path in image_paths:
            content = source_path.read_bytes()
            image_hash = hashlib.sha256(content).hexdigest()
            suffix = source_path.suffix.lower() or ".jpg"
            target_path = TARGET_DIR / f"dafeiyu_{image_hash[:16]}{suffix}"
            if not target_path.exists():
                shutil.copy2(source_path, target_path)

            record = session.exec(
                select(Images).where(
                    Images.image_hash == image_hash,
                    Images.image_type == ImageType.EMOJI,
                )
            ).first()
            description = build_description(source_path)
            now = datetime.now()
            if record is None:
                record = Images(
                    image_hash=image_hash,
                    description=description,
                    full_path=serialize_stored_image_path(target_path),
                    image_type=ImageType.EMOJI,
                    query_count=0,
                    is_registered=True,
                    is_banned=False,
                    no_file_flag=False,
                    record_time=now,
                    register_time=now,
                    vlm_processed=True,
                )
                imported += 1
            else:
                record.description = description
                record.full_path = serialize_stored_image_path(target_path)
                record.is_registered = True
                record.is_banned = False
                record.no_file_flag = False
                record.register_time = record.register_time or now
                record.vlm_processed = True
                updated += 1
            session.add(record)

    print(f"emoji-import complete: total={len(image_paths)} imported={imported} updated={updated}")


if __name__ == "__main__":
    main()
