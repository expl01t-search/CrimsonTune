
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_classify_gpu_usb_network():
    from utils.msi_mode import _classify

    assert "gpu" in _classify("VEN_10DE&DEV_2504", "NVIDIA GeForce RTX 3050")
    assert "network" in _classify("VEN_10EC&DEV_8168", "Realtek PCIe GBE Family Controller")
    assert "usb" in _classify("VEN_8086&DEV_1E31", "Intel(R) USB 3.0 eXtensible Host Controller")
    assert not _classify("VEN_8086&DEV_1234", "Intel Management Engine")


def test_manager_has_msi_and_nvidia_tweaks():
    from tweaks import create_manager

    manager = create_manager()
    ids = {m.id for m in manager.get_all_meta()}
    for tid in (
        "msi_mode_high_priority",
        "nvidia_max_frame_latency",
        "nvidia_disable_runtime_pm",
        "nvidia_driver_perf",
    ):
        assert tid in ids
