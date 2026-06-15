
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Optional

from PySide6.QtCore import QTimer, Qt, QEvent
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.disk_cleanup import format_freed_size
from core.detector import SystemInfo, get_live_stats
from core.i18n import t
from core.tweak_state import TweakStatus
from tweaks.base import TweakManager
from ui.components.gauge_widget import GaugeWidget
from ui.components.pill_button import PillButton
from ui.components.surface_card import SurfaceCard
from ui.window_utils import ui_scale_factor
from ui.workers import DiskCleanupWorker, DiskLoadWorker


@dataclass(frozen=True)
class _DiskInfo:
    index: int
    letter: str
    model: str
    free_gb: float
    total_gb: float


def _list_system_disks_fast() -> list[_DiskInfo]:
    import psutil

    fallback: list[_DiskInfo] = []
    for idx, part in enumerate(psutil.disk_partitions(all=False)):
        if not part.mountpoint or part.fstype in ("", "cdrom"):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except OSError:
            continue
        letter = part.device.rstrip("\\")
        if not letter.endswith(":"):
            continue
        fallback.append(
            _DiskInfo(
                index=idx,
                letter=letter,
                model=t("disk_local"),
                free_gb=round(usage.free / (1024 ** 3), 1),
                total_gb=round(usage.total / (1024 ** 3), 1),
            )
        )
    return fallback


def _list_system_disks() -> list[_DiskInfo]:
    from utils.subprocess_helper import run_powershell

    wmi_script = (
        "$out = @(); "
        "Get-CimInstance Win32_DiskDrive | Sort-Object { [int]$_.Index } | ForEach-Object { "
        "  $disk = $_; "
        "  $idx = [int]$disk.Index; "
        "  $model = ($disk.Model -replace '\\s+$','').Trim(); "
        "  $letter = $null; "
        "  $size = [int64]$disk.Size; "
        "  $free = 0L; "
        "  $parts = Get-CimAssociatedInstance -InputObject $disk "
        "    -ResultClassName Win32_DiskPartition -ErrorAction SilentlyContinue; "
        "  foreach ($part in $parts) { "
        "    $logicals = Get-CimAssociatedInstance -InputObject $part "
        "      -ResultClassName Win32_LogicalDisk -ErrorAction SilentlyContinue; "
        "    foreach ($ld in $logicals) { "
        "      if ($ld.DriveType -eq 3 -and $ld.DeviceID) { "
        "        $letter = $ld.DeviceID; "
        "        $free = [int64]$ld.FreeSpace; "
        "        $size = [int64]$ld.Size; "
        "        break "
        "      } "
        "    }; "
        "    if ($letter) { break } "
        "  }; "
        "  if (-not $letter) { return }; "
        "  $out += [PSCustomObject]@{ "
        "    Index = $idx; "
        "    Letter = $letter; "
        "    Model = if ($model) { $model } else { 'Локальный диск' }; "
        "    FreeBytes = $free; "
        "    TotalBytes = $size "
        "  } "
        "}; "
        "$out | ConvertTo-Json -Compress"
    )
    disks = _parse_disk_json(run_powershell(wmi_script, timeout=30))
    if disks:
        return disks

    storage_script = (
        "$out = @(); "
        "Get-Disk | Sort-Object Number | ForEach-Object { "
        "  $disk = $_; "
        "  $part = Get-Partition -DiskNumber $disk.Number -ErrorAction SilentlyContinue | "
        "    Where-Object { $_.DriveLetter } | "
        "    Sort-Object { if ($_.IsBoot) { 0 } elseif ($_.IsSystem) { 1 } else { 2 } } | "
        "    Select-Object -First 1; "
        "  if (-not $part) { return }; "
        "  $pd = Get-PhysicalDisk -DeviceNumber $disk.Number -ErrorAction SilentlyContinue; "
        "  $vol = Get-Volume -DriveLetter $part.DriveLetter -ErrorAction SilentlyContinue; "
        "  $model = if ($pd) { $pd.FriendlyName.Trim() } else { 'Локальный диск' }; "
        "  $out += [PSCustomObject]@{ "
        "    Index = [int]$disk.Number; "
        "    Letter = ([string]$part.DriveLetter + ':'); "
        "    Model = $model; "
        "    FreeBytes = [int64](if ($vol) { $vol.SizeRemaining } else { 0 }); "
        "    TotalBytes = [int64](if ($vol) { $vol.Size } else { $disk.Size }) "
        "  } "
        "}; "
        "$out | ConvertTo-Json -Compress"
    )
    disks = _parse_disk_json(run_powershell(storage_script, timeout=30))
    if disks:
        return disks

    return _list_system_disks_fast()


def _parse_disk_json(result: tuple[int, str, str]) -> list[_DiskInfo]:
    code, out, _ = result
    if code != 0 or not out.strip():
        return []
    try:
        raw = json.loads(out)
        items = raw if isinstance(raw, list) else [raw]
        disks: list[_DiskInfo] = []
        for item in items:
            disks.append(
                _DiskInfo(
                    index=int(item["Index"]),
                    letter=str(item["Letter"]),
                    model=str(item.get("Model") or t("disk_local")).strip(),
                    free_gb=round(int(item.get("FreeBytes", 0)) / (1024 ** 3), 1),
                    total_gb=round(int(item.get("TotalBytes", 0)) / (1024 ** 3), 1),
                )
            )
        return disks
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return []


def compute_optimization_stats(
    manager: TweakManager,
    is_compatible_fn: Callable,
) -> dict[str, int | float]:
    metas = manager.get_all_meta()
    compat = {m.id: is_compatible_fn(m) for m in metas}
    trackable: list[str] = []

    for meta in metas:
        if not compat.get(meta.id, False):
            continue
        state = manager.get_tweak_state(meta.id, compatible=True)
        if state.status in (TweakStatus.ONE_SHOT, TweakStatus.UNKNOWN):
            continue
        trackable.append(meta.id)

    counts = manager.state_detector.count_active(trackable, compat)
    active = counts["active"]
    total = len(trackable)
    percent = round((active / total) * 100) if total else 0.0

    applied_app = 0
    for tid in trackable:
        state = manager.get_tweak_state(tid, compatible=compat.get(tid, True))
        if state.applied_by_app:
            applied_app += 1

    return {
        "percent": percent,
        "active": active,
        "total": total,
        "available": counts["inactive"],
        "applied_app": applied_app,
        "one_shot": counts["one_shot"],
    }


class _HardwareCard(QFrame):

    def __init__(
        self,
        *,
        chip: str,
        title: str,
        device_name: str,
        specs: str,
        usage_label: str = "",
        usage_percent: float | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("hardwareCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(14)

        chip_lbl = QLabel(chip)
        chip_lbl.setObjectName("hwChip")
        chip_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip_lbl.setFixedSize(42, 42)
        layout.addWidget(chip_lbl)

        body = QVBoxLayout()
        body.setSpacing(4)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("hwTitle")
        body.addWidget(title_lbl)
        self._title_lbl = title_lbl

        name_lbl = QLabel(device_name)
        name_lbl.setObjectName("hwName")
        name_lbl.setWordWrap(True)
        name_lbl.setToolTip(device_name)
        body.addWidget(name_lbl)
        self._name_lbl = name_lbl

        specs_lbl = QLabel(specs)
        specs_lbl.setObjectName("hwSpecs")
        body.addWidget(specs_lbl)
        self._specs_lbl = specs_lbl

        usage_caption = None
        if usage_percent is not None:
            usage_row = QHBoxLayout()
            usage_row.setSpacing(8)
            usage_caption = QLabel(usage_label)
            usage_caption.setObjectName("hwUsageLabel")
            self._usage_value = QLabel(f"{usage_percent:.0f}%")
            self._usage_value.setObjectName("hwUsageValue")
            usage_row.addWidget(usage_caption)
            usage_row.addStretch()
            usage_row.addWidget(self._usage_value)
            body.addLayout(usage_row)

            self._bar = QProgressBar()
            self._bar.setObjectName("hwUsageBar")
            self._bar.setRange(0, 100)
            self._bar.setValue(int(usage_percent))
            self._bar.setTextVisible(False)
            self._bar.setFixedHeight(6)
            body.addWidget(self._bar)
        else:
            self._bar = None
            self._usage_value = None
        self._usage_caption = usage_caption

        layout.addLayout(body, stretch=1)

    def update_content(
        self,
        *,
        title: str | None = None,
        device_name: str | None = None,
        specs: str | None = None,
        usage_label: str | None = None,
    ) -> None:
        if title is not None:
            self._title_lbl.setText(title)
        if device_name is not None:
            self._name_lbl.setText(device_name)
            self._name_lbl.setToolTip(device_name)
        if specs is not None:
            self._specs_lbl.setText(specs)
        if usage_label is not None and self._usage_caption is not None:
            self._usage_caption.setText(usage_label)

    def set_usage(self, percent: float, *, subtitle: str = "") -> None:
        if self._bar is not None:
            self._bar.setValue(int(max(0, min(100, percent))))
        if self._usage_value is not None:
            self._usage_value.setText(f"{percent:.0f}%")
        if subtitle and hasattr(self, "_specs_lbl"):
            self._specs_lbl.setText(subtitle)


class _SystemCard(QFrame):

    def __init__(
        self,
        *,
        os_version: str,
        os_build: str,
        disks: list[_DiskInfo],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("systemCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._os_version = os_version
        self._os_build = os_build
        self._disks = disks

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        chip_lbl = QLabel("OS")
        chip_lbl.setObjectName("hwChip")
        chip_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chip_lbl.setFixedSize(42, 42)
        layout.addWidget(chip_lbl, alignment=Qt.AlignmentFlag.AlignTop)

        body = QVBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(6)

        title_lbl = QLabel(t("os_detected"))
        title_lbl.setObjectName("hwTitle")
        body.addWidget(title_lbl)
        self._title_lbl = title_lbl

        os_lbl = QLabel(t("os_build_line", version=os_version, build=os_build or "—"))
        os_lbl.setObjectName("hwName")
        os_lbl.setWordWrap(True)
        body.addWidget(os_lbl)
        self._os_lbl = os_lbl

        self._disk_host = QWidget()
        self._disk_layout = QVBoxLayout(self._disk_host)
        self._disk_layout.setContentsMargins(0, 0, 0, 0)
        self._disk_layout.setSpacing(0)
        body.addWidget(self._disk_host)

        self._disk_rows: list[dict] = []
        self._empty_lbl: QLabel | None = None
        self._populate_disks(disks)

        layout.addLayout(body, stretch=1)

    def _populate_disks(self, disks: list[_DiskInfo]) -> None:
        while self._disk_layout.count():
            item = self._disk_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._disk_rows.clear()
        self._empty_lbl = None
        self._disks = disks

        if disks:
            for disk in disks:
                block = QFrame()
                block.setObjectName("diskBlock")
                block.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                block_layout = QVBoxLayout(block)
                block_layout.setContentsMargins(0, 6, 0, 0)
                block_layout.setSpacing(3)

                idx_lbl = QLabel(t("disk_label", index=disk.index, letter=disk.letter))
                idx_lbl.setObjectName("diskRowTitle")
                idx_lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
                block_layout.addWidget(idx_lbl)

                model_lbl = QLabel(disk.model)
                model_lbl.setObjectName("diskRowModel")
                model_lbl.setWordWrap(False)
                model_lbl.setToolTip(disk.model)
                model_lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
                block_layout.addWidget(model_lbl)

                space_lbl = QLabel(
                    t("disk_space", free=f"{disk.free_gb:.1f}", total=f"{disk.total_gb:.1f}")
                )
                space_lbl.setObjectName("diskRowSpace")
                space_lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
                block_layout.addWidget(space_lbl)
                self._disk_layout.addWidget(block)
                self._disk_rows.append(
                    {
                        "idx_lbl": idx_lbl,
                        "model_lbl": model_lbl,
                        "space_lbl": space_lbl,
                        "disk": disk,
                    }
                )
        else:
            empty = QLabel(t("disks_none"))
            empty.setObjectName("diskRowSpace")
            self._disk_layout.addWidget(empty)
            self._empty_lbl = empty

    def set_disks(self, disks: list[_DiskInfo]) -> None:
        self._populate_disks(disks)

    def retranslate(self) -> None:
        self._title_lbl.setText(t("os_detected"))
        self._os_lbl.setText(
            t("os_build_line", version=self._os_version, build=self._os_build or "—")
        )
        for row in self._disk_rows:
            disk = row["disk"]
            row["idx_lbl"].setText(t("disk_label", index=disk.index, letter=disk.letter))
            row["space_lbl"].setText(
                t("disk_space", free=f"{disk.free_gb:.1f}", total=f"{disk.total_gb:.1f}")
            )
        if self._empty_lbl is not None:
            self._empty_lbl.setText(t("disks_none"))

    def _elide_disk_models(self, width: int) -> None:
        from PySide6.QtGui import QFontMetrics

        max_w = max(80, width - 130)
        for lbl in self.findChildren(QLabel, "diskRowModel"):
            full = lbl.toolTip() or lbl.text()
            lbl.setText(
                QFontMetrics(lbl.font()).elidedText(full, Qt.TextElideMode.ElideRight, max_w)
            )


class DashboardPage(QWidget):

    def __init__(
        self,
        system_info: SystemInfo,
        manager: TweakManager,
        is_compatible_fn: Callable,
        on_quick_action: Optional[Callable[[str], None]] = None,
        *,
        tweak_count: int = 0,
        applied_count: int = 0,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("appPage")
        self._system_info = system_info
        self._manager = manager
        self._is_compatible = is_compatible_fn
        self._on_quick = on_quick_action
        self._tweak_count = tweak_count
        self._applied_count = applied_count

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        header = QLabel(t("nav_dashboard"))
        header.setObjectName("pageTitle")
        root.addWidget(header)
        self._page_header = header

        body = QHBoxLayout()
        body.setSpacing(14)

        left = QVBoxLayout()
        left.setSpacing(10)

        live = get_live_stats()
        info = self._system_info

        cores = info.cpu_cores or 0
        threads = info.cpu_threads or cores
        core_text = t("cpu_cores", n=cores) if threads == cores or not threads else t(
            "cpu_cores_threads", cores=cores, threads=threads
        )

        self._cpu_card = _HardwareCard(
            chip="CPU",
            title=t("cpu_detected"),
            device_name=info.cpu_name or t("cpu_unknown"),
            specs=core_text,
            usage_label=t("usage_label"),
            usage_percent=live["cpu_percent"],
        )
        left.addWidget(self._cpu_card)

        vram = info.gpu_vram_gb
        vram_text = t("vram_gb", gb=f"{vram:g}") if vram > 0 else t("vram_na")
        vendor_labels = {"nvidia": "NVIDIA", "amd": "AMD", "intel": "Intel"}
        vendor = vendor_labels.get(info.gpu_vendor, "GPU")

        self._gpu_card = _HardwareCard(
            chip="GPU",
            title=t("gpu_detected"),
            device_name=info.gpu_name or t("gpu_unknown"),
            specs=f"{vendor} · {vram_text}",
        )
        left.addWidget(self._gpu_card)

        ram_specs = t(
            "ram_usage_specs",
            total=f"{info.ram_total_gb:.1f}",
            used=f"{live['ram_used_gb']:.1f}",
        )
        self._ram_card = _HardwareCard(
            chip="RAM",
            title=t("ram_detected"),
            device_name=t("ram_installed", gb=f"{info.ram_total_gb:.1f}"),
            specs=ram_specs,
            usage_label=t("usage_label"),
            usage_percent=live["ram_percent"],
        )
        left.addWidget(self._ram_card)

        self._system_card = _SystemCard(
            os_version=info.os_version,
            os_build=info.os_build or "—",
            disks=_list_system_disks_fast(),
        )
        left.addWidget(self._system_card)

        self._disk_worker = DiskLoadWorker()
        self._disk_worker.finished_ok.connect(self._on_disks_loaded)
        self._disk_worker.finished.connect(self._on_disk_worker_finished)
        self._disk_worker.start()

        left_host = QWidget()
        left_host.setObjectName("hardwareColumn")
        left_host.setLayout(left)
        left_host.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        left_scroll = QScrollArea()
        left_scroll.setObjectName("hardwareScroll")
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        left_scroll.setWidget(left_host)
        self._left_host = left_host
        self._left_scroll = left_scroll
        left_scroll.viewport().installEventFilter(self)

        hw_title = QLabel(t("section_hardware"))
        hw_title.setObjectName("sectionTitle")
        self._hw_title = hw_title

        left_column = QVBoxLayout()
        left_column.setContentsMargins(0, 0, 0, 0)
        left_column.setSpacing(10)
        left_column.addWidget(hw_title)
        left_column.addWidget(left_scroll, stretch=1)

        left_wrap = QWidget()
        left_wrap.setObjectName("hardwareColumnWrap")
        left_wrap.setLayout(left_column)
        left_wrap.setMinimumWidth(300)
        body.addWidget(left_wrap, stretch=3)

        right = QVBoxLayout()
        right.setSpacing(10)

        opt_card = SurfaceCard(variant="monitor")
        opt_card.setObjectName("optimizationCard")
        self._opt_card = opt_card
        opt_layout = opt_card.content_layout()
        opt_layout.setSpacing(10)

        opt_heading = QLabel(t("opt_windows_title"))
        opt_heading.setObjectName("sectionTitle")
        opt_heading.setWordWrap(True)
        opt_layout.addWidget(opt_heading)
        self._opt_heading = opt_heading

        metrics_block = QWidget()
        metrics_block.setObjectName("optMetricsBlock")
        metrics_block.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        metrics_layout = QVBoxLayout(metrics_block)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(10)

        self._gauge_wrap = QWidget()
        self._gauge_wrap.setObjectName("gaugeWrap")
        self._gauge_wrap.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        gauge_row = QHBoxLayout(self._gauge_wrap)
        gauge_row.setContentsMargins(0, 0, 0, 0)
        gauge_row.setSpacing(0)
        gauge_row.addStretch(1)

        self._opt_gauge = GaugeWidget("", accent="crimson")
        gauge_row.addWidget(self._opt_gauge, 0, Qt.AlignmentFlag.AlignHCenter)
        gauge_row.addStretch(1)
        metrics_layout.addWidget(self._gauge_wrap)

        self._opt_caption = QLabel("")
        self._opt_caption.setObjectName("optCaption")
        self._opt_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._opt_caption.setWordWrap(True)
        self._opt_caption.setMinimumHeight(44)
        self._opt_caption.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        metrics_layout.addWidget(self._opt_caption)
        self._metrics_block = metrics_block
        opt_layout.addWidget(metrics_block)

        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(12)
        stats_grid.setVerticalSpacing(8)
        self._stat_titles: dict[str, QLabel] = {}
        self._stat_labels: dict[str, QLabel] = {}
        for row, (key, title_key) in enumerate(
            [
                ("active", "stat_active_system"),
                ("available", "stat_available_more"),
                ("applied_app", "stat_via_app"),
            ]
        ):
            title_lbl = QLabel(t(title_key))
            title_lbl.setObjectName("optStatTitle")
            title_lbl.setWordWrap(True)
            value_lbl = QLabel("0")
            value_lbl.setObjectName("optStatValue")
            value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            stats_grid.addWidget(title_lbl, row, 0)
            stats_grid.addWidget(value_lbl, row, 1)
            self._stat_titles[key] = title_lbl
            self._stat_labels[key] = value_lbl
        opt_layout.addLayout(stats_grid)

        right.addWidget(opt_card)

        cleanup_card = SurfaceCard()
        cleanup_card.setObjectName("cleanupCard")
        cleanup_layout = cleanup_card.content_layout()
        cleanup_layout.setSpacing(10)

        self._cleanup_btn = PillButton(t("cleanup_btn"), variant="primary")
        self._cleanup_btn.clicked.connect(self._start_cleanup)
        cleanup_layout.addWidget(self._cleanup_btn)

        self._cleanup_status = QLabel(t("cleanup_hint"))
        self._cleanup_status.setObjectName("muted")
        self._cleanup_status.setWordWrap(True)
        cleanup_layout.addWidget(self._cleanup_status)

        self._cleanup_bar = QProgressBar()
        self._cleanup_bar.setObjectName("cleanupProgress")
        self._cleanup_bar.setRange(0, 100)
        self._cleanup_bar.setValue(0)
        self._cleanup_bar.setTextVisible(False)
        self._cleanup_bar.setFixedHeight(8)
        self._cleanup_bar.hide()
        cleanup_layout.addWidget(self._cleanup_bar)

        self._cleanup_result = QLabel("")
        self._cleanup_result.setObjectName("cleanupResult")
        self._cleanup_result.setWordWrap(True)
        self._cleanup_result.hide()
        cleanup_layout.addWidget(self._cleanup_result)

        right.addWidget(cleanup_card)
        self._cleanup_worker: DiskCleanupWorker | None = None
        self._cleanup_stats: tuple[int, int, int] | None = None

        right_wrap = QWidget()
        right_wrap.setObjectName("optimizationColumn")
        right_wrap.setMinimumWidth(max(260, int(252 * ui_scale_factor())))
        right_wrap.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_wrap.setLayout(right)
        self._right_wrap = right_wrap
        body.addWidget(right_wrap, stretch=2)
        self._gauge_wrap.installEventFilter(self)
        right_wrap.installEventFilter(self)

        root.addLayout(body, stretch=1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_live)
        self._timer.start(3000)

        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._sync_layout)

        self._refresh_optimization()
        for delay in (0, 50, 150, 350):
            QTimer.singleShot(delay, self._sync_layout)

    def _optimization_target_width(self) -> int:
        candidates: list[int] = []
        if hasattr(self, "_gauge_wrap"):
            w = self._gauge_wrap.width()
            if w > 0:
                candidates.append(w)
        if hasattr(self, "_opt_card"):
            w = self._opt_card.width()
            if w > 0:
                candidates.append(max(0, w - 24))
        if hasattr(self, "_right_wrap"):
            w = self._right_wrap.width()
            if w > 0:
                candidates.append(max(0, w - 32))
        if candidates:
            return max(candidates)
        return 200

    def _on_disks_loaded(self, disks: object) -> None:
        if isinstance(disks, list):
            self._system_card.set_disks(disks)
            self._schedule_layout_sync()

    def _on_disk_worker_finished(self) -> None:
        worker = self._disk_worker
        self._disk_worker = None
        if worker is not None:
            worker.deleteLater()

    def _schedule_layout_sync(self) -> None:
        self._resize_timer.start(60)

    def _sync_layout(self) -> None:
        self._sync_hardware_column()
        self._sync_optimization_layout()

    def _sync_optimization_layout(self) -> None:
        if not hasattr(self, "_gauge_wrap"):
            return
        width = self._optimization_target_width()
        side = max(GaugeWidget.MIN_SIDE, min(width - 12, GaugeWidget.MAX_SIDE))
        self._opt_gauge.apply_side(side)
        gauge_h = self._opt_gauge.height()
        self._gauge_wrap.setMinimumHeight(gauge_h + 4)
        self._metrics_block.setMinimumHeight(gauge_h + 4 + self._opt_caption.minimumHeight() + 10)
        self._gauge_wrap.updateGeometry()
        self._metrics_block.updateGeometry()
        self._opt_card.updateGeometry()

    def _sync_hardware_column(self) -> None:
        if not hasattr(self, "_left_scroll"):
            return
        vp = self._left_scroll.viewport()
        w = vp.width()
        if w <= 0:
            return
        self._system_card._elide_disk_models(max(80, w - 32))

    def eventFilter(self, watched, event) -> bool:
        if event.type() == QEvent.Type.Resize:
            if hasattr(self, "_left_scroll") and watched is self._left_scroll.viewport():
                self._schedule_layout_sync()
            elif hasattr(self, "_gauge_wrap") and watched is self._gauge_wrap:
                self._schedule_layout_sync()
            elif hasattr(self, "_right_wrap") and watched is self._right_wrap:
                self._schedule_layout_sync()
        return super().eventFilter(watched, event)

    def showEvent(self, event) -> None:
        if not self._timer.isActive():
            self._timer.start(3000)
        self._refresh_optimization()
        self._sync_layout()
        for delay in (0, 80, 200):
            QTimer.singleShot(delay, self._sync_layout)
        super().showEvent(event)

    def resizeEvent(self, event) -> None:
        self._schedule_layout_sync()
        super().resizeEvent(event)

    def retranslate_ui(self) -> None:
        live = get_live_stats()
        info = self._system_info

        self._page_header.setText(t("nav_dashboard"))
        self._hw_title.setText(t("section_hardware"))
        self._opt_heading.setText(t("opt_windows_title"))

        cores = info.cpu_cores or 0
        threads = info.cpu_threads or cores
        core_text = t("cpu_cores", n=cores) if threads == cores or not threads else t(
            "cpu_cores_threads", cores=cores, threads=threads
        )
        self._cpu_card.update_content(
            title=t("cpu_detected"),
            device_name=info.cpu_name or t("cpu_unknown"),
            specs=core_text,
            usage_label=t("usage_label"),
        )

        vram = info.gpu_vram_gb
        vram_text = t("vram_gb", gb=f"{vram:g}") if vram > 0 else t("vram_na")
        vendor_labels = {"nvidia": "NVIDIA", "amd": "AMD", "intel": "Intel"}
        vendor = vendor_labels.get(info.gpu_vendor, "GPU")
        self._gpu_card.update_content(
            title=t("gpu_detected"),
            device_name=info.gpu_name or t("gpu_unknown"),
            specs=f"{vendor} · {vram_text}",
        )

        ram_specs = t(
            "ram_usage_specs",
            total=f"{info.ram_total_gb:.1f}",
            used=f"{live['ram_used_gb']:.1f}",
        )
        self._ram_card.update_content(
            title=t("ram_detected"),
            device_name=t("ram_installed", gb=f"{info.ram_total_gb:.1f}"),
            specs=ram_specs,
            usage_label=t("usage_label"),
        )

        self._system_card.retranslate()

        for key, title_key in (
            ("active", "stat_active_system"),
            ("available", "stat_available_more"),
            ("applied_app", "stat_via_app"),
        ):
            self._stat_titles[key].setText(t(title_key))

        self._cleanup_btn.setText(t("cleanup_btn"))
        cleanup = self._cleanup_worker
        cleanup_running = False
        if cleanup is not None:
            try:
                cleanup_running = cleanup.isRunning()
            except RuntimeError:
                self._cleanup_worker = None
        if not cleanup_running:
            self._cleanup_status.setText(t("cleanup_hint"))
        if self._cleanup_result.isVisible() and self._cleanup_stats is not None:
            bytes_freed, files_deleted, errors = self._cleanup_stats
            err_note = t("cleanup_errors_suffix", errors=errors) if errors else ""
            self._cleanup_result.setText(
                t("cleanup_result", freed=format_freed_size(bytes_freed), files=files_deleted)
                + err_note
            )

        self._refresh_optimization()
        self._schedule_layout_sync()

    def hideEvent(self, event) -> None:
        self._timer.stop()
        super().hideEvent(event)

    def update_status(self, *, applied_count: Optional[int] = None, manager: Optional[TweakManager] = None) -> None:
        if applied_count is not None:
            self._applied_count = applied_count
        if manager is not None:
            self._manager = manager
        self._refresh_optimization()

    def _refresh_optimization(self) -> None:
        stats = compute_optimization_stats(self._manager, self._is_compatible)
        pct = float(stats["percent"])
        self._opt_gauge.set_value(pct, animate=False)
        self._stat_labels["active"].setText(str(stats["active"]))
        self._stat_labels["available"].setText(str(stats["available"]))
        self._stat_labels["applied_app"].setText(str(stats["applied_app"]))
        total = stats["total"]
        self._opt_caption.setText(
            t("opt_caption", active=stats["active"], total=total)
        )

    def _start_cleanup(self) -> None:
        if self._cleanup_worker and self._cleanup_worker.isRunning():
            return
        self._cleanup_btn.setEnabled(False)
        self._cleanup_bar.show()
        self._cleanup_bar.setValue(0)
        self._cleanup_result.hide()
        self._cleanup_status.setText(t("cleanup_preparing"))

        worker = DiskCleanupWorker()
        worker.progress.connect(self._on_cleanup_progress)
        worker.finished_ok.connect(self._on_cleanup_done)
        worker.finished.connect(lambda: self._cleanup_btn.setEnabled(True))
        worker.finished.connect(worker.deleteLater)
        worker.start()
        self._cleanup_worker = worker

    def _on_cleanup_progress(self, current: int, total: int, label: str, freed: int) -> None:
        pct = int((current / max(total, 1)) * 100)
        self._cleanup_bar.setValue(pct)
        self._cleanup_status.setText(t("cleanup_progress", label=label, freed=format_freed_size(freed)))

    def _on_cleanup_done(self, bytes_freed: int, files_deleted: int, errors: int) -> None:
        self._cleanup_stats = (bytes_freed, files_deleted, errors)
        self._cleanup_bar.setValue(100)
        self._cleanup_status.setText(t("cleanup_done"))
        self._cleanup_result.show()
        err_note = t("cleanup_errors_suffix", errors=errors) if errors else ""
        self._cleanup_result.setText(
            t("cleanup_result", freed=format_freed_size(bytes_freed), files=files_deleted)
            + err_note
        )

    def _update_live(self) -> None:
        try:
            stats = get_live_stats()
            self._cpu_card.set_usage(stats["cpu_percent"])
            info = self._system_info
            ram_specs = t(
                "ram_usage_specs",
                total=f"{info.ram_total_gb:.1f}",
                used=f"{stats['ram_used_gb']:.1f}",
            )
            self._ram_card.set_usage(stats["ram_percent"], subtitle=ram_specs)
        except Exception:
            pass
