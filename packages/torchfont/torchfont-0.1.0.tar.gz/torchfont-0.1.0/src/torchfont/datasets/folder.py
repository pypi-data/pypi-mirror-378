from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any, cast

import numpy as np
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._f_v_a_r import NamedInstance, table__f_v_a_r
from torch.utils.data import Dataset
from tqdm.auto import tqdm

_KEEP_TABLES = {"cmap", "maxp", "fvar"}


def _load_meta(
    path: Path | str,
    cps_filter: list[int] | None,
) -> tuple[bool, int, np.ndarray]:
    path = Path(path).expanduser().resolve()

    with TTFont(path, lazy=True) as font:
        for tag in list(font.keys()):
            if tag not in _KEEP_TABLES:
                del font[tag]

        if "fvar" in font:
            fvar = cast(table__f_v_a_r, font["fvar"])
            insts: list[NamedInstance] = fvar.instances
            is_var, n_inst = (True, len(insts)) if insts else (False, 1)
        else:
            is_var, n_inst = False, 1

        cmap: dict[int, str] = font.getBestCmap()
        cps = np.fromiter(cmap.keys(), dtype=np.uint32)

        if cps_filter:
            cps = np.intersect1d(
                cps,
                np.asarray(cps_filter, dtype=np.uint32),
                assume_unique=False,
            )

    return is_var, n_inst, cps


class FontFolder(Dataset):
    def __init__(
        self,
        root: Path | str,
        codepoint_filter: list[int] | None = None,
        transform: Callable | None = None,
    ) -> None:
        self.root = Path(root).expanduser().resolve()
        self.paths = sorted(fp for fp in self.root.rglob("*.[oOtT][tT][fF]"))
        self.transform = transform

        loader = partial(_load_meta, cps_filter=codepoint_filter)
        with ProcessPoolExecutor() as ex:
            results = list(
                tqdm(
                    ex.map(loader, self.paths),
                    total=len(self.paths),
                    desc="Loading fonts",
                ),
            )

        is_var, n_inst, cps_list = zip(*results, strict=True)
        self._is_var = np.asarray(is_var, dtype=bool)
        self._n_inst = np.asarray(n_inst, dtype=np.uint32)

        self._cps_counts = np.array([a.size for a in cps_list], dtype=np.uint32)
        self._cps_offsets = np.concatenate([[0], np.cumsum(self._cps_counts)])
        self._flat_cps = np.concatenate(cps_list)

        lens_per_font = self._n_inst * self._cps_counts
        self._sample_offsets = np.concatenate([[0], np.cumsum(lens_per_font)])
        self._inst_offsets = np.concatenate([[0], np.cumsum(self._n_inst)])

        self._unique_cps = np.unique(self._flat_cps)
        self.num_content_classes = len(self._unique_cps)
        self.num_style_classes = int(self._inst_offsets[-1])

    def __len__(self) -> int:
        return int(self._sample_offsets[-1])

    def __getitem__(self, idx: int) -> Any:  # noqa: ANN401
        font_idx = int(np.searchsorted(self._sample_offsets, idx, side="right") - 1)
        local_idx = int(idx - self._sample_offsets[font_idx])

        n_cps = int(self._cps_counts[font_idx])
        inst_idx, cp_idx_local = divmod(local_idx, n_cps)

        cp_start = int(self._cps_offsets[font_idx])
        cp = int(self._flat_cps[int(cp_start + cp_idx_local)])

        style_idx = int(self._inst_offsets[font_idx] + inst_idx)
        content_idx = int(np.searchsorted(self._unique_cps, cp))

        sample = (
            self.paths[font_idx],
            bool(self._is_var[font_idx]),
            inst_idx,
            cp,
            style_idx,
            content_idx,
        )
        return self.transform(*sample) if self.transform else sample
