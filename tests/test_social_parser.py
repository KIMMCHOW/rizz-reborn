"""
tests/test_social_parser.py
pytest 测试套件 · social_parser.py
"""

import pytest
import json
from pathlib import Path

from tools.social_parser import (
    detect_platform,
    platform_display,
    scan_directory,
    read_text_file,
    parse_json_export,
    scan_signals,
    generate_report,
)


# ─────────────────────────────────────────────
# 纯函数
# ─────────────────────────────────────────────

class TestDetectPlatform:
    def test_weibo(self) -> None:
        assert detect_platform("微博_2024.txt") == "weibo"
        assert detect_platform("WB_001.jpg") == "weibo"

    def test_xiaohongshu(self) -> None:
        assert detect_platform("小红书截图.png") == "xiaohongshu"
        assert detect_platform("xhs_01.jpg") == "xiaohongshu"
        assert detect_platform("rednote_post.txt") == "xiaohongshu"

    def test_moments(self) -> None:
        assert detect_platform("朋友圈截图.jpg") == "moments"
        assert detect_platform("wechat_moments.png") == "moments"

    def test_douyin(self) -> None:
        assert detect_platform("抖音视频.jpg") == "douyin"
        assert detect_platform("dy_001.png") == "douyin"

    def test_unknown(self) -> None:
        assert detect_platform("random_file.jpg") == "未知平台"
        assert detect_platform("untitled.txt") == "未知平台"


class TestPlatformDisplay:
    def test_known_platforms(self) -> None:
        assert platform_display("weibo") == "微博"
        assert platform_display("xiaohongshu") == "小红书"
        assert platform_display("moments") == "微信朋友圈"
        assert platform_display("douyin") == "抖音"
        assert platform_display("instagram") == "Instagram"

    def test_unknown(self) -> None:
        assert platform_display("未知平台") == "未知来源"
        assert platform_display("random") == "random"


class TestScanSignals:
    def test_positive_signals(self) -> None:
        result = scan_signals("今天和你在一起很开心，期待下次见面！")
        assert "积极信号" in result
        assert "开心" in result["积极信号"] or "期待" in result["积极信号"]

    def test_low_mood_signals(self) -> None:
        result = scan_signals("今天心情不好，失眠了，好难过")
        assert "情绪低落" in result
        assert "难过" in result["情绪低落"]

    def test_love_related(self) -> None:
        result = scan_signals("暗恋一个人很久了，想表白")
        assert "感情相关" in result
        assert "暗恋" in result["感情相关"]

    def test_no_signal(self) -> None:
        result = scan_signals("今天吃了火锅")
        assert result == {}

    def test_catches_multiple_categories(self) -> None:
        result = scan_signals("想你啊，好难过")
        assert len(result) >= 2  # "积极信号" or "情绪低落"


# ─────────────────────────────────────────────
# 文件操作
# ─────────────────────────────────────────────

class TestReadTextFile:
    def test_read_normal_file(self, tmp_path: Path) -> None:
        f = tmp_path / "note.txt"
        f.write_text("这是内容", encoding="utf-8")
        assert read_text_file(str(f)) == "这是内容"

    def test_truncate_long_file(self, tmp_path: Path) -> None:
        f = tmp_path / "long.txt"
        f.write_text("x" * 10000, encoding="utf-8")
        result = read_text_file(str(f), max_chars=100)
        assert len(result) <= 100 + 50  # allow for truncation msg
        assert "[... 内容过长" in result

    def test_read_nonexistent(self) -> None:
        result = read_text_file("/no/such/file.txt")
        assert "[读取失败" in result

    def test_encoding_errors_ignored(self, tmp_path: Path) -> None:
        f = tmp_path / "weird.txt"
        f.write_bytes(b"\x00\xff\xfe bad content")
        result = read_text_file(str(f))
        assert isinstance(result, str)


class TestParseJsonExport:
    def test_list_format(self, tmp_path: Path) -> None:
        f = tmp_path / "export.json"
        f.write_text(json.dumps([
            {"text": "微博内容1", "created_at": "2024-01-01"},
            {"text": "微博内容2", "time": "2024-01-02"},
        ]), encoding="utf-8")
        posts = parse_json_export(str(f))
        assert len(posts) == 2
        assert posts[0]["text"] == "微博内容1"

    def test_dict_with_data_key(self, tmp_path: Path) -> None:
        f = tmp_path / "export.json"
        f.write_text(json.dumps({"data": [
            {"content": "小红书笔记", "timestamp": "2024-01-01"},
        ]}), encoding="utf-8")
        posts = parse_json_export(str(f))
        assert len(posts) == 1
        assert posts[0]["text"] == "小红书笔记"

    def test_empty_json(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.json"
        f.write_text("{}", encoding="utf-8")
        assert parse_json_export(str(f)) == []

    def test_max_50_items(self, tmp_path: Path) -> None:
        f = tmp_path / "many.json"
        items = [{"text": f"post_{i}"} for i in range(100)]
        f.write_text(json.dumps(items), encoding="utf-8")
        posts = parse_json_export(str(f))
        assert len(posts) == 50

    def test_invalid_json(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.json"
        f.write_text("not json", encoding="utf-8")
        assert parse_json_export(str(f)) == []

    def test_handles_other_keys(self, tmp_path: Path) -> None:
        f = tmp_path / "other.json"
        f.write_text(json.dumps([
            {"description": "微博描述", "date": "2024-01-01"},
            {"body": "帖子正文", "timestamp": "2024-01-02"},
        ]), encoding="utf-8")
        posts = parse_json_export(str(f))
        assert len(posts) == 2


class TestScanDirectory:
    def test_empty_dir(self, tmp_path: Path) -> None:
        result = scan_directory(str(tmp_path))
        assert result["images"] == []
        assert result["texts"] == []

    def test_finds_images_and_texts(self, tmp_path: Path) -> None:
        (tmp_path / "a.jpg").write_text("x")
        (tmp_path / "b.png").write_text("y")
        (tmp_path / "note.txt").write_text("note")
        (tmp_path / "readme.md").write_text("md")
        (tmp_path / "data.json").write_text("{}")
        result = scan_directory(str(tmp_path))
        assert len(result["images"]) == 2
        assert len(result["texts"]) == 3

    def test_report_md_excluded(self, tmp_path: Path) -> None:
        (tmp_path / "report.md").write_text("x")
        result = scan_directory(str(tmp_path))
        names = {p["name"] for p in result["others"]}
        assert "report.md" not in names

    def test_nonexistent_dir(self) -> None:
        result = scan_directory("/no/such/path")
        assert result["images"] == []
        assert result["texts"] == []

    def test_subdirectory_scan(self, tmp_path: Path) -> None:
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "deep.jpg").write_text("x")
        result = scan_directory(str(tmp_path))
        assert any(p["rel"].startswith("sub") for p in result["images"])

    def test_others_category(self, tmp_path: Path) -> None:
        (tmp_path / "video.mp4").write_text("x")
        result = scan_directory(str(tmp_path))
        assert len(result["others"]) == 1


class TestGenerateReport:
    def test_empty_directory(self, tmp_path: Path) -> None:
        result = generate_report(str(tmp_path), "小美")
        assert "社交媒体内容报告" in result
        assert "⚠️" in result

    def test_returns_string(self, tmp_path: Path) -> None:
        result = generate_report(str(tmp_path), "小美")
        assert isinstance(result, str)

    def test_with_image_files(self, tmp_path: Path) -> None:
        (tmp_path / "weibo_01.jpg").write_text("x")
        (tmp_path / "小红书截图.png").write_text("x")
        result = generate_report(str(tmp_path), "小美")
        assert "图片清单" in result

    def test_with_text_files(self, tmp_path: Path) -> None:
        (tmp_path / "note.txt").write_text("今天很开心，想你！", encoding="utf-8")
        result = generate_report(str(tmp_path), "小美")
        assert "文字内容" in result
        assert "积极信号" in result

    def test_output_path_writes_file(self, tmp_path: Path) -> None:
        out = tmp_path / "report.md"
        generate_report(str(tmp_path), "小美", str(out))
        assert out.exists()