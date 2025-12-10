# -*- coding: utf-8 -*-
"""
same_pinyin_finder.py

功能：
    - 基于拼音的同音候选生成。
    - 支持：
        1) 使用词表：给定一个词，找出词表中拼音完全一致的其它词（"你好" -> "你号" 等）。
        2) 无词表降级：根据汉字拼音枚举同音字，按位替换生成候选（结果不保证都是真实词）。

依赖：
    pip install pypinyin

示例：

    from same_pinyin_finder import SamePinyinFinder

    # 方式1：直接传词表
    finder = SamePinyinFinder(words=["你好", "你号", "您好", "笑死", "小子"])

    print(finder.get_candidates("你好"))
    # 可能输出：['你号']

    # 方式2：从词典文件构建（如 jieba 的 dict.txt / dict.txt.big）
    finder = SamePinyinFinder.from_dict_file("dict.txt.big")
    print(finder.get_candidates("你好"))

    # 方式3：完全没词表，只用“同拼音换字”降级：
    finder = SamePinyinFinder()  # 不传词表
    print(finder.get_candidates("你好", use_word_list=False, use_char_fallback=True))

"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Dict, Set, List, Optional

from pypinyin import lazy_pinyin


@dataclass
class SamePinyinFinder:
    """
    同拼音候选生成器。

    参数：
        words:
            初始词表（可选）。
            - 传入可迭代的词列表：["你好", "你号", ...]
            - 不传则只启用“按字同拼音替换”的降级模式（结果可能包含大量无意义组合）。

    属性（不建议外部直接动）：
        words: 去重后的词集合。
    """

    words: Iterable[str] = field(default_factory=list)

    # 内部索引：拼音串 -> 词集合
    _pinyin_to_words: Dict[str, Set[str]] = field(init=False, default_factory=dict)
    # 内部索引：拼音串 -> 字集合（延迟构建，用于“无词表”降级）
    _pinyin_to_chars: Optional[Dict[str, Set[str]]] = field(init=False, default=None)

    def __post_init__(self) -> None:
        # 把 words 转成去重后的 set[str]
        word_set: Set[str] = set()
        for w in self.words:
            if w is None:
                continue
            s = str(w).strip()
            if not s:
                continue
            word_set.add(s)
        self.words = word_set  # type: ignore[assignment]

        # 构建「拼音串 -> 词」索引
        for w in self.words:
            p = self.word_to_pinyin(w)
            if not p:
                continue
            self._pinyin_to_words.setdefault(p, set()).add(w)

    # ---------------- 公共方法 ----------------

    @classmethod
    def from_dict_file(
        cls,
        path: str,
        encoding: str = "utf-8",
        separator: Optional[str] = None,
        word_col: int = 0,
    ) -> "SamePinyinFinder":
        """
        从词典文件构建 SamePinyinFinder。

        适配常见格式（如 jieba 的 dict.txt / dict.txt.big: "词 频 词性"）：
            - 默认用任意空白分隔，取第 word_col 列作为词。

        参数：
            path:
                词典文件路径。
            encoding:
                文件编码，默认 'utf-8'。
            separator:
                列分隔符：
                    - None：用任意空白分隔（str.split()）。
                    - 其他字符串：用 line.split(separator)。
            word_col:
                哪一列是“词”，从 0 开始计数。

        返回：
            SamePinyinFinder 实例。
        """
        words: List[str] = []
        with open(path, "r", encoding=encoding, errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if separator is None:
                    parts = line.split()
                else:
                    parts = line.split(separator)
                if len(parts) <= word_col:
                    continue
                w = parts[word_col].strip()
                if not w:
                    continue
                words.append(w)

        return cls(words=words)

    @staticmethod
    def word_to_pinyin(text: str) -> str:
        """
        把一串中文（词/短语）转成「无声调拼音串」。

        例如：
            "你好" -> "nihao"
            "笑死" -> "xiaosi"
        非中文字符会被忽略。
        """
        # errors='ignore'：遇到非汉字（数字、英文字母等）直接跳过
        syllables = lazy_pinyin(text, errors="ignore")
        return "".join(syllables)

    def get_candidates(
        self,
        text: str,
        *,
        use_word_list: bool = True,
        use_char_fallback: bool = True,
        include_original: bool = False,
        max_per_char: int = 20,
    ) -> List[str]:
        """
        获取给定文本的同拼音候选词/短语。

        行为：
            1) 若 use_word_list=True 且构建时提供了词表：
                - 返回词表中与 text 拼音完全一致的其它词。
            2) 若 use_char_fallback=True：
                - 对 text 每个汉字，用同拼音的其它汉字按位替换，生成若干候选。
                - 不依赖词表，但结果不保证是真实存在的词，只保证“字的拼音一样”。

        参数：
            text:
                输入文本（通常是词或短语，如 "你好"、"笑死"）。
            use_word_list:
                是否使用词表索引（前提是构建实例时传入了词表）。
            use_char_fallback:
                是否启用“字级别同拼音替换”的降级模式，用于没词表或想多些候选时。
            include_original:
                是否保留原词本身在结果里，默认 False（一般不需要把自己当候选）。
            max_per_char:
                字级别替换时，每个拼音最多取多少个同音字，防止组合爆炸。

        返回：
            候选列表（已去重、排序）。
        """
        text = text.strip()
        if not text:
            return []

        candidates: Set[str] = set()

        # --- 1) 基于词表：拼音完全一致 ---
        if use_word_list and self._pinyin_to_words:
            p = self.word_to_pinyin(text)
            if p:
                same_words = self._pinyin_to_words.get(p, set())
                candidates.update(same_words)

        # --- 2) 无词表降级：按位用“同拼音汉字”替换 ---
        if use_char_fallback:
            char_level = self._char_level_candidates(
                text=text,
                max_per_char=max_per_char,
            )
            candidates.update(char_level)

        if not include_original:
            candidates.discard(text)

        # 排个序，保证结果稳定
        return sorted(candidates)

    # ---------------- 内部方法 ----------------

    def _ensure_char_index(self) -> None:
        """
        构建「拼音 -> 字集合」索引，仅在第一次需要时扫描一次 Unicode CJK 基本区。
        """
        if self._pinyin_to_chars is not None:
            return

        mapping: Dict[str, Set[str]] = {}

        # CJK Unified Ideographs 基本区：4E00–9FFF
        for code in range(0x4E00, 0x9FFF + 1):
            ch = chr(code)
            # 使用 lazy_pinyin 将单字转成拼音（不带声调）
            p_list = lazy_pinyin(ch, errors="ignore")
            if not p_list:
                continue
            p = p_list[0]
            if not p:
                continue
            mapping.setdefault(p, set()).add(ch)

        self._pinyin_to_chars = mapping

    def _char_level_candidates(self, text: str, max_per_char: int) -> Set[str]:
        """
        根据“每个字的拼音”寻找所有同音字，按位替换生成候选。

        注意：
            - 不依赖词表。
            - 结果只是保证“每个位置的字拼音不变”，组合是否真实存在完全不保证。
        """
        self._ensure_char_index()
        assert self._pinyin_to_chars is not None

        result: Set[str] = set()

        for i, ch in enumerate(text):
            # 只处理 CJK 基本区汉字
            if not ("\u4e00" <= ch <= "\u9fff"):
                continue

            p_list = lazy_pinyin(ch, errors="ignore")
            if not p_list:
                continue
            p = p_list[0]
            same_chars = self._pinyin_to_chars.get(p, set())
            if not same_chars:
                continue

            # 限制每个位置最多替换 max_per_char 个同音字，避免爆炸
            count = 0
            for alt in same_chars:
                if alt == ch:
                    continue
                new_word = text[:i] + alt + text[i + 1 :]
                result.add(new_word)
                count += 1
                if count >= max_per_char:
                    break

        return result
