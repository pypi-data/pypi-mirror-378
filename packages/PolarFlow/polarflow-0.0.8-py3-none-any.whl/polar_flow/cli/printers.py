# utils/console.py
from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from fnmatch import fnmatchcase
from typing import TYPE_CHECKING, Any

import typer
from rich import box
from rich.columns import Columns
from rich.console import Console, Group
from rich.json import JSON as RICH_JSON
from rich.panel import Panel
from rich.pretty import Pretty
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .commands.utils import no_val_nested, version_nested

if TYPE_CHECKING:
    from polar_flow._vendor.slurm_client.types import Unset

Renderable = Table | Columns | Group

_console = Console()


# 圆角面板
def _panel(
    msg: str | Text,
    *,
    title: str | None = None,
    style: str = "none",
    border: str = "cyan",
) -> Panel:
    return Panel(
        msg if isinstance(msg, Text) else Text(str(msg)),
        title=title,
        title_align="left",
        box=box.ROUNDED,  # 圆角
        border_style=border,  # 边框颜色
        expand=True,
        style=style,  # 面板内文字的基础样式
        padding=(1, 2),
    )


def print_info(msg: str | Text, title: str = "INFO") -> None:
    _console.print(_panel(msg, title=title, border="cyan"))


def print_success(msg: str | Text, title: str = "OK") -> None:
    _console.print(_panel(msg, title=title, border="green"))


def print_warning(msg: str | Text, title: str = "WARN") -> None:
    _console.print(_panel(msg, title=title, border="yellow"))


def print_error(msg: str | Text, title: str = "ERROR") -> None:
    _console.print(_panel(msg, title=title, border="red"))


def print_debug(msg: str | Text, title: str = "DEBUG", debug: bool = False) -> None:
    if debug:
        _console.print(_panel(Text(str(msg), style="dim"), title=title, border="bright_black"))


def print_client_we(warnings: Unset | list[Any], errors: Unset | list[Any]) -> None:
    if errors:
        print_error(
            "\n".join(
                [
                    f"{e.to_dict().get('error')}[{e.to_dict().get('error_number')}]: '{e.to_dict().get('description')}' from '{e.to_dict().get('source')}'"
                    for e in errors
                ],
            ),
        )
        raise typer.Exit(1)
    if warnings:
        print_warning(
            "\n".join(
                [
                    f"'{w.to_dict().get('description')}' from '{w.to_dict().get('source')}'"
                    for w in warnings
                ],
            ),
        )


# 打印键值对
def print_kv(title: str, mapping: dict[str, object], as_what: str) -> None:
    if as_what == "table":
        table = Table(title=title, safe_box=True, expand=False)
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta", overflow="fold")

        for k, v in mapping.items():
            table.add_row(str(k), str(v))

        _console.print(table)
    else:
        table = Table(title=title, show_lines=True, expand=True, box=None)
        table.add_column("Key", style="bold cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        for k, v in mapping.items():
            table.add_row(str(k), Pretty(v, expand_all=True))

        _console.print(table)


def print_kv_grouped(
    title: str,
    groups: dict[str, dict[str, object]],
    as_what: str = "table",
    *,
    group_order: Iterable[str] | None = None,
    sort_keys: bool = True,
    empty_placeholder: str = "—",
) -> None:
    """
    分组打印键值对：
      - groups: { group_name: { key: value, ... }, ... }
      - as_what: "table" -> 值以 str 渲染；其他 -> Pretty(v, expand_all=True)
      - group_order: 指定分组顺序（可选），未列出的分组排后面
      - show_empty_groups: 是否打印空分组
    """
    # 基础表格风格与列
    if as_what == "table":
        tbl = Table(title=title, safe_box=True, expand=False)
        tbl.add_column("Group", style="bold yellow", no_wrap=True)
        tbl.add_column("Key", style="cyan", no_wrap=True)
        tbl.add_column("Value", style="magenta", overflow="fold")
    else:
        tbl = Table(title=title, show_lines=True, expand=False, box=box.SIMPLE_HEAVY)
        tbl.add_column("Group", style="bold yellow", no_wrap=True)
        tbl.add_column("Key", style="bold cyan", no_wrap=True)
        tbl.add_column("Value", style="magenta")

    # 准备分组顺序
    all_group_names = list(groups.keys())
    ordered: list[str] = []
    if group_order:
        seen = set()
        for g in group_order:
            if g in all_group_names and g not in seen:
                ordered.append(g)
                seen.add(g)
        for g in all_group_names:
            if g not in seen:
                ordered.append(g)
    else:
        ordered = all_group_names[:]

    for g in ordered:
        inner = groups.get(g, {})

        # 组头行
        tbl.add_row(f"[bold]{g}[/bold]", "", "")

        # 组内键排序
        keys = list(inner.keys())
        if sort_keys:
            keys.sort()

        if keys:
            for k in keys:
                v = inner[k]
                rendered = str(v) if as_what == "table" else Pretty(v, expand_all=True)
                tbl.add_row("", str(k), rendered)
        else:
            # 空分组的占位
            tbl.add_row("", empty_placeholder, empty_placeholder)

        if g != ordered[-1]:
            tbl.add_section()

    _console.print(tbl)


@dataclass(frozen=True)
class Annotation:
    """
    注释系统：路径匹配（glob 风格）

    示例：
    - "meta.cluster"
    - "jobs[*].nodes"
    - "jobs[*].tasks[*].gpu.memory"
    - "statistics.**"         （双星表示多级通配）
    - "**.id"                 （匹配所有层级下名为 id 的键）
    - "warnings[*]" / "errors[*]"

    匹配规则：
    - 路径以点分段，列表用 [index] 或 [*]。
    - 使用 fnmatch 的大小写敏感通配（* ? []），并扩展 ** 为跨层级。
    - 我们将对象的真实路径渲染为同样格式后做匹配。
    """

    text: str
    style: str = "dim italic"


def _normalize_path(segments: Sequence[str]) -> str:
    # segment 已包含 [i] 或 [*] 等，直接以 '.' 连接，列表索引前面不加点
    out = []
    for s in segments:
        if s.startswith("["):
            out.append(s)
        else:
            if out:
                out.append(".")
            out.append(s)
    return "".join(out) or "root"


def _expand_globstar(pattern: str) -> list[str]:
    # 将 ** 处理为两种等价形态以增强匹配概率
    # 例如 "a.**.b" -> ["a.*.b"（近似）, "a.**.b"（原样）]
    # 由于我们最终用 fnmatch，对 ** 与 * 实际没有层级概念，保留原样即可。
    return [pattern]


def _match_path(pattern: str, path: str) -> bool:
    # 允许 **，但 fnmatch 不理解层级；这里做一个近似：
    # - 直接用 fnmatch；用户可以通过 "**" 提示“任意多段”，对我们等价于 "*"
    # - 同时把 "**" 替换成 "*" 再匹配一次增加容错
    candidates = _expand_globstar(pattern)
    for pat in candidates:
        if fnmatchcase(path, pat):
            return True
        if "**" in pat:
            pat2 = pat.replace("**", "*")
            if fnmatchcase(path, pat2):
                return True
    return False


def _find_annotation(ann: Mapping[str, Annotation] | None, path: str) -> Annotation | None:
    if not ann:
        return None
    # 采用“最长/最具体优先”：按 pattern 长度和分段数排序
    best_key = None
    best_score = (-1, -1)
    for pat, _ in ann.items():
        if _match_path(pat, path):
            score = (len(pat), pat.count(".") + pat.count("["))
            if score > best_score:
                best_score = score
                best_key = pat
    return ann.get(best_key) if best_key else None


def print_json_ex(  # noqa: PLR0913
    title: str,
    data: Any,
    *,
    # 展示行为
    expand: bool = False,
    sort_keys: bool = False,
    show_types: bool = False,
    show_raw: bool = True,
    # 大数据控制
    depth_limit: int = 6,
    max_children_per_dict: int = 200,
    max_items_per_list: int = 200,
    preview_max: int = 120,
    deep_preview_max: int = 240,
    # 列表 → 表格的判定
    table_homogeneous_ratio: float = 0.8,
    table_max_keys: int = 16,
    # 折叠/展开控制（按路径通配）
    expand_paths: Sequence[str] = (),
    collapse_paths: Sequence[str] = (),
    # 键排序优先（命中的键会按给定顺序靠前）
    key_priority: Sequence[str] = ("meta", "statistics", "warnings", "errors"),
    # 注释：路径 -> Annotation
    annotations: Mapping[str, str | Annotation] | None = None,
    # 侧边注释面板相关
    show_side_notes_for_tables: bool = True,
    notes_panel_title: str = "注释",
    notes_panel_width: int | None = None,  # 固定列宽
    show_side_notes_for_dicts: bool = True,
    dict_notes_min_hits: int = 2,  # 至少命中多少条注释才展示侧栏
    dict_notes_max_depth: int = 4,  # 超过该深度就不再画侧栏，避免过深层级拥挤
    dict_notes_panel_title: str = "相关信息",
    dict_notes_panel_width: int | None = None,
) -> None:
    """
    通用大 JSON 打印器（Rich）。
    - 任意结构；对巨型对象做分层截断 & 预览，支持路径注释和按路径强制展开/折叠。
    - 列表里“同构字典”为主的场景自动表格化（可折叠）。
    """
    console = _console

    # 标准化注释映射
    ann_map: dict[str, Annotation] = {}
    if annotations:
        for k, v in annotations.items():
            ann_map[k] = v if isinstance(v, Annotation) else Annotation(text=str(v))

    # 处理 NO_VAL
    data = no_val_nested(data)
    data = version_nested(data)

    # 包装非 Mapping
    if not isinstance(data, Mapping):
        data = {"root": data}

    console.rule(f"[bold magenta]{title}")

    # 优先区块
    sections_order = list(key_priority)
    shown: set[str] = set()

    # 渲染函数们
    def _is_homogeneous_list_of_dicts(seq: list[Any], min_ratio: float) -> bool:
        if not seq:
            return False
        dicts = [x for x in seq if isinstance(x, Mapping)]
        return bool(dicts) and (len(dicts) / len(seq) >= min_ratio)

    def _collect_keys(
        seq: Iterable[Mapping[str, Any]],
        max_keys: int,
        *,
        sort_keys: bool = False,
    ) -> list[list[str]]:
        """
        将所有 key 按出现频率降序、同频按字典序排序后，
        按 max_keys 分页返回（list of pages）。

        Arg:
            seq: 由 mapping 组成的可迭代对象
            max_keys: 每页最多的 key 数，必须 > 0
            sort_keys: 是否对“每一页”内再按字母序排序
        Return:
            形如 [["k1","k2",...], ["kN+1",...], ...]
        """
        if max_keys <= 0:
            raise ValueError("max_keys must be > 0")

        c = Counter()
        for d in seq:
            c.update(d.keys())

        # 全量排序：频率降序 + 字典序
        ordered_keys = [k for k, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]

        # 分页
        pages = [ordered_keys[i : i + max_keys] for i in range(0, len(ordered_keys), max_keys)]

        # 可选：页内再排序为字母序（不改变跨页的全局顺序）
        if sort_keys:
            pages = [sorted(page) for page in pages]

        return pages

    def _value_preview(v: Any, max_len: int) -> str:
        try:
            if isinstance(v, (str, int, float, bool)) or v is None or isinstance(v, (list, dict)):
                s = json.dumps(v, ensure_ascii=False)
            else:
                s = repr(v)
        except Exception:  # noqa: BLE001
            s = str(v)
        if len(s) > max_len:
            s = s[: max_len - 1] + "…"
        return s

    def _should_expand(path: str, level: int) -> bool:
        # 规则：命中 collapse_paths → 折叠；命中 expand_paths → 展开；
        # 否则用全局 expand 与深度限制判断。
        for pat in collapse_paths:
            if _match_path(pat, path):
                return False
        for pat in expand_paths:
            if _match_path(pat, path):
                return True
        if level >= depth_limit:
            return False
        return bool(expand)

    def _annotated_label(label: str, path: str, extra: str | None = None) -> Text:
        t = Text(label, style="yellow")
        if extra:
            t.append(f" {extra}", style="dim")
        a = _find_annotation(ann_map, path)
        if a:
            t.append(" # ", style="dim")
            t.append(a.text, style=a.style)
        return t

    def _collect_column_notes(path: str, cols: list[str]) -> list[tuple[str, str]]:
        """
        收集当前表格列（字段）在注释映射中的命中，返回 (列名, 注释文本) 列表。
        列路径规则：<path>.<col>（与 annotations 的路径匹配一致）
        """
        notes: list[tuple[str, str]] = []
        for col in cols:
            col_path = f"{path}.{col}" if path != "root" else col
            ann = _find_annotation(ann_map, col_path)
            if ann:
                notes.append((col, ann.text))
        return notes

    def _render_notes_panel_for_table(path: str, cols: list[str]) -> Panel | None:
        """
        构造一个右侧注释面板，把表格列命中的注释汇总展示。
        没有命中注释则返回 None。
        """
        hits = _collect_column_notes(path, cols)
        if not hits:
            return None

        note_tbl = Table(
            box=box.SIMPLE,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
        )
        note_tbl.add_column("Field", style="yellow", no_wrap=True)
        note_tbl.add_column("Annotation", overflow="fold", ratio=1)

        for field, tip in hits:
            note_tbl.add_row(field, tip)

        return Panel(
            note_tbl,
            title=notes_panel_title,
            title_align="left",
            border_style="magenta",
            width=notes_panel_width,
            expand=False,
        )

    def _render_list_as_table(
        label: str | None,
        path: str,
        seq: list[Mapping[str, Any]],
    ) -> Renderable:
        """
        默认返回 Table（当只有一页列时）；
        若列按 max_keys 分页产生多页，则把多张 Table 用 Group 纵向拼接；
        若开启 show_side_notes_for_tables 且有注释命中，则返回 Columns：
        左侧是 Group(所有表)，右侧是注释面板。
        """
        # 收集所有分页列
        pages: list[list[str]] = list(
            _collect_keys(seq, table_max_keys),
        )  # 这里的 _collect_keys 已改为分页版
        all_cols_union: list[str] = sorted({k for page in pages for k in page})

        tables: list[Table] = []

        for page_cols in pages:
            table = Table(
                title=label or None,
                box=box.SIMPLE_HEAVY,
                header_style="bold cyan",
                show_lines=False,
                title_style="bold",
            )
            table.add_column("#", style="dim", no_wrap=True)
            for k in page_cols:
                table.add_column(k, overflow="fold", no_wrap=False)

            max_rows = (
                max_items_per_list if _should_expand(path, level=0) else min(50, max_items_per_list)
            )
            for idx, item in enumerate(seq[:max_rows]):
                row = [str(idx)]
                for k in page_cols:
                    v = item.get(k, None)
                    row.append(_value_preview(v, deep_preview_max if expand else preview_max))
                table.add_row(*row)

            if len(seq) > max_rows:
                table.caption = f"... ({len(seq) - max_rows} more rows)"

            tables.append(table)

        if len(tables) == 1:
            single_table = tables[0]
            if show_side_notes_for_tables:
                notes_panel = _render_notes_panel_for_table(path, all_cols_union)
                if notes_panel is not None:
                    return Columns([single_table, notes_panel], expand=True, equal=False, padding=1)
            return single_table

        stacked = Group(*tables)

        if show_side_notes_for_tables:
            notes_panel = _render_notes_panel_for_table(path, all_cols_union)
            if notes_panel is not None:
                return Columns([stacked, notes_panel], expand=True, equal=False, padding=1)

        return stacked

    def _collect_child_key_notes(path: str, items: list[tuple[str, Any]]) -> list[tuple[str, str]]:
        """
        收集“当前字典节点的直接子键”的注释，返回 (字段名, 注释文本)。
        匹配路径：<path>.<key>
        """
        hits: list[tuple[str, str]] = []
        for k, _ in items:
            child_path = f"{path}.{k}" if path != "root" else k
            ann = _find_annotation(ann_map, child_path)
            if ann:
                hits.append((str(k), ann.text))
        return hits

    def _render_notes_panel_for_keys(
        hits: list[tuple[str, str]],
        *,
        title: str,
        width: int | None,
    ) -> Panel:
        note_tbl = Table(
            box=box.SIMPLE,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
        )
        note_tbl.add_column("Field", style="yellow", no_wrap=True)
        note_tbl.add_column("Annotation", overflow="fold", ratio=1)
        for field, tip in hits:
            note_tbl.add_row(field, tip)
        return Panel(
            note_tbl,
            title=title,
            title_align="left",
            border_style="magenta",
            width=width,
            expand=False,
        )

    def _sorted_items(d: Mapping[str, Any]) -> Iterable[tuple[str, Any]]:
        keys = list(d.keys())
        # 先按 key_priority 中的顺序，然后再按 sort_keys
        prio_index = {k: i for i, k in enumerate(key_priority)}
        keys.sort(key=lambda k: (prio_index.get(k, len(key_priority)), k if sort_keys else 0))
        if not sort_keys:
            # 把优先键提到前面
            prioritized = [k for k in keys if k in prio_index]
            others = [k for k in d if k not in prio_index]
            seq = prioritized + others
            return ((k, d[k]) for k in seq)
        return ((k, d[k]) for k in keys)

    def _add_to_tree(tree: Tree, obj: Any, *, path_segments: list[str], level: int) -> None:
        path = _normalize_path(path_segments)
        can_expand = _should_expand(path, level)

        if isinstance(obj, Mapping):
            # 控制 children 数量
            items = list(_sorted_items(obj))
            total = len(items)
            if not can_expand:
                # 折叠预览
                preview = "{ " + ", ".join(
                    f"{k}: {_value_preview(v, preview_max)}" for k, v in items[:5]
                )
                preview += " , … }" if total > 5 else " }"
                tree.add(Text(preview, style="white"))
                return

            show_n = total if can_expand else min(max_children_per_dict, total)
            visible_items = items[:show_n]

            side_panel = None
            if show_side_notes_for_dicts and level <= dict_notes_max_depth:
                hits = _collect_child_key_notes(path, visible_items)
                if len(hits) >= dict_notes_min_hits:
                    side_panel = _render_notes_panel_for_keys(
                        hits,
                        title=dict_notes_panel_title,
                        width=dict_notes_panel_width,
                    )

            if side_panel is None:
                # 原始渲染：直接把子节点挂到当前树节点下
                for k, v in visible_items:
                    child = tree.add(
                        _annotated_label(str(k), f"{path}.{k}" if path != "root" else k)
                    )
                    _add_to_tree(child, v, path_segments=[*path_segments, k], level=level + 1)
                if show_n < total:
                    tree.add(Text(f"... ({total - show_n} more keys)", style="dim italic"))
            else:
                # 带侧栏：在当前层级构造一个临时子树”
                # 左侧放这棵子树，右侧放注释面板，用 Columns 并排显示。
                tmp_root = Tree(Text("", style=""))  # 空标签子树容器
                for k, v in visible_items:
                    child = tmp_root.add(
                        _annotated_label(str(k), f"{path}.{k}" if path != "root" else k)
                    )
                    _add_to_tree(child, v, path_segments=[*path_segments, k], level=level + 1)
                if show_n < total:
                    tmp_root.add(Text(f"... ({total - show_n} more keys)", style="dim italic"))

                tree.add(Columns([tmp_root, side_panel], expand=True, equal=False, padding=1))

        elif isinstance(obj, list):
            n = len(obj)
            if n == 0:
                tree.add(Text("[]", style="dim"))
                return

            if _is_homogeneous_list_of_dicts(obj, table_homogeneous_ratio):
                dicts = [x for x in obj if isinstance(x, Mapping)]
                table = _render_list_as_table(label=None, path=path, seq=dicts)
                tree.add(table)
                if n > len(dicts):
                    tree.add(
                        Text(f"... ({n - len(dicts)} non-dict items hidden)", style="dim italic"),
                    )
                return

            # 普通列表
            if not can_expand:
                # 折叠预览：前若干项 + 数量提示
                head_n = min(10, n)
                preview_elems = ", ".join(_value_preview(v, preview_max) for v in obj[:head_n])
                suffix = " , … ]" if n > head_n else " ]"
                tree.add(Text(f"[ {preview_elems}{suffix}", style="white"))
                return

            show_n = min(max_items_per_list, n)
            for i, v in enumerate(obj[:show_n]):
                child = tree.add(Text(f"[{i}]", style="cyan"))
                _add_to_tree(child, v, path_segments=[*path_segments, f"[{i}]"], level=level + 1)
            if show_n < n:
                tree.add(Text(f"... ({n - show_n} more items)", style="dim italic"))

        else:
            # 基本类型
            pv = _value_preview(obj, deep_preview_max if can_expand else preview_max)
            t = Text(pv, style="white")
            if show_types and obj is not None:
                t.append(f"  ({type(obj).__name__})", style="dim")
            tree.add(t)

    # 渲染优先区块
    for sec in sections_order:
        if isinstance(data, Mapping) and sec in data:
            root = Tree(Text(sec, style="bold cyan"))
            # label 上补注释
            label = _annotated_label(sec, sec)
            root.label = label
            _add_to_tree(root, data[sec], path_segments=[sec], level=0)
            console.print(Panel(root, title=sec, border_style="cyan", expand=True))
            shown.add(sec)

    # 其它
    if isinstance(data, Mapping):
        others: MutableMapping[str, Any] = {k: v for k, v in data.items() if k not in shown}
        if others:
            root = Tree(Text("others", style="bold cyan"))
            _add_to_tree(root, others, path_segments=["others"], level=0)
            console.print(Panel(root, title="others", border_style="blue", expand=True))
    else:
        # 极端情况（非 Mapping 已在前面包裹）
        root = Tree(Text("root", style="bold cyan"))
        _add_to_tree(root, data, path_segments=["root"], level=0)
        console.print(Panel(root, title="root", border_style="blue", expand=True))

    if show_raw:
        console.rule("[dim]Raw JSON (folded)")
        console.print(
            Panel(
                RICH_JSON.from_data(data, indent=2, highlight=True, sort_keys=sort_keys),
                border_style="dim",
                expand=True,
            ),
        )


class PrintProgress:
    def __init__(self, text: str = "[bold cyan]请稍候，正在处理...[/]") -> None:
        self.progress = Progress(
            SpinnerColumn(style="cyan"),
            TextColumn(text),
            TimeElapsedColumn(),
            transient=True,
            console=_console,
        )

    def __enter__(self) -> Progress:
        self.progress.__enter__()
        self.task_id = self.progress.add_task("loading", total=None)
        return self.progress

    def __exit__(self, exc_type, exc, tb) -> None:
        return self.progress.__exit__(exc_type, exc, tb)
