from pathlib import Path
from typing import Any, Literal, Union

from vidata.file_manager import FileManager, FileManagerStacked
from vidata.io import load_json
from vidata.loaders import (
    BaseLoader,
    ImageLoader,
    ImageStackLoader,
    MultilabelLoader,
    MultilabelStackedLoader,
    SemSegLoader,
)
from vidata.task_manager import (
    MultiLabelSegmentationManager,
    SemanticSegmentationManager,
    TaskManager,
)

PathLike = Union[str, Path]
TaskLiteral = Literal["semseg", "multilabel"]


def build_image_loader(
    file_type: str, channels: int, backend: str = None, file_stack: bool = False
) -> BaseLoader:
    """Create an image loader.

    Args:
        file_type: File extension (e.g., ".nii.gz", ".png").
        channels: Number of channels; set 1 if images are single-channel.
        backend: Optional backend preference (e.g., "nibabel", "sitk").
        file_stack: If True, expect channel-stacked files (e.g., *_0000, *_0001).

    Returns:
        A configured image loader instance.
    """
    loader_cls = ImageStackLoader if file_stack else ImageLoader
    return loader_cls(ftype=file_type, channels=channels, backend=backend)


def build_target_loader(
    file_type: str,
    num_classes: int,
    task: TaskLiteral = "semseg",
    backend: str | None = None,
    file_stack: bool = False,
) -> BaseLoader:
    """Create a target (label) loader.

    Args:
        file_type: File extension for labels (e.g., ".nii.gz", ".png").
        num_classes: Number of classes (include background if applicable).
        task: Task type, "semseg" or "multilabel".
        backend: Optional backend preference (e.g., "nibabel", "sitk").
        file_stack: If True, expect class-stacked label files (multilabel only).

    Returns:
        A configured target loader instance.

    Raises:
        ValueError: If the task is not one of {"semseg", "multilabel"}.
    """
    if task == "semseg":
        loader_cls = SemSegLoader
    elif task == "multilabel":
        loader_cls = MultilabelStackedLoader if file_stack else MultilabelLoader
    else:
        raise ValueError(f"Task {task} not in 'semseg', 'multilabel'")

    return loader_cls(ftype=file_type, num_classes=num_classes, backend=backend)


def build_file_manager(
    path: PathLike,
    file_type: str,
    pattern: str | None = None,
    file_stack: bool = False,
    split: str | None = None,
    splits_file: str | None = None,
    splits_index: int | None = None,
) -> FileManager:
    """Create a file manager for images or labels.

    Args:
        path: Root directory to search for files.
        file_type: File extension to match (e.g., ".nii.gz", ".png").
        pattern: Optional glob pattern or per-split mapping of patterns.
        file_stack: If True, collapse stack files (e.g., *_0000, *_0001 → single core).
        split: select to corresponding entry of `splits_file`.
        splits_file: Optional JSON file with predefined splits. The content should be a dict or a list of dicts.
        splits_index: Optional index if `splits_file` is a list of dicts.

    Returns:
        A configured file manager instance (stacked or regular).
    """
    manager_cls = FileManagerStacked if file_stack else FileManager

    include_names = None
    if splits_file is not None:
        if not Path(splits_file).exists():
            raise FileNotFoundError(f"splits_file not found: {splits_file}")

        splits = load_json(splits_file)

        if isinstance(splits, list):
            if splits_index is None:
                raise ValueError("splits_index is required if your splits_file contains a list")
            if not (0 <= splits_index < len(splits)):
                raise ValueError(
                    f"splits_index {splits_index} is not in range of your splits file with len {len(splits_file)}"
                )
            splits = splits[splits_index]

        if split not in splits:
            raise ValueError(f"split {split} is not in splits_file with keys {list(splits.keys())}")

        include_names = splits[split]

    return manager_cls(
        path=path,
        file_type=file_type,
        pattern=pattern,
        include_names=include_names,
    )


def build_target_manager(
    task: TaskLiteral = "semseg",
) -> TaskManager:
    """Create a task manager for label semantics.

    Args:
        task: Task type, "semseg" or "multilabel".

    Returns:
        A task manager instance.

    Raises:
        ValueError: If the task is not one of {"semseg", "multilabel"}.
    """
    if task == "semseg":
        tmanager = SemanticSegmentationManager
    elif task == "multilabel":
        tmanager = MultiLabelSegmentationManager
    else:
        raise ValueError(f"Task {task} not in 'semseg', 'multilabel'")
    return tmanager()


def build_image_workflow(
    img_cfg: dict[str, Any],
    split: str | None = None,
    splits_file: PathLike | None = None,
    splits_index: int | None = None,
) -> tuple[BaseLoader, FileManager]:
    """Build the image workflow (loader + file manager) from a config section.

    Args:
        img_cfg: Image config dict with keys:
            - "path" (str | Path)
            - "file_type" (str)
            - "channels" (int)
            - Optional: "pattern" (str | Mapping[str, str]), "file_stack" (bool), "backend" (str)
        split: Optional split name to resolve per-split pattern.
        splits_file: Optional splits JSON path passed to the file manager.
        splits_index: Optional split index (fold) if the splits file is a list.

    Returns:
        (image_loader, image_file_manager)
    """
    # Required Arguments
    path = img_cfg["path"]
    file_type = img_cfg["file_type"]
    channels = img_cfg["channels"]

    # Optional Arguments
    pattern = img_cfg.get("pattern")
    file_stack = img_cfg.get("file_stack", False)
    backend = img_cfg.get("backend")

    image_loader = build_image_loader(file_type, channels, backend, file_stack)
    file_manager = build_file_manager(
        path, file_type, pattern, file_stack, split, splits_file, splits_index
    )
    return image_loader, file_manager


def build_target_workflow(
    target_cfg: dict[str, Any],
    split: str | None = None,
    splits_file: PathLike | None = None,
    splits_index: int | None = None,
) -> tuple[BaseLoader, FileManager, TaskManager]:
    """Build the target workflow (loader + file manager + task manager) from a config section.

    Args:
        target_cfg: Target config dict with keys:
            - "path" (str | Path)
            - "file_type" (str)
            - "classes" (int)
            - "task" ("semseg" | "multilabel")
            - Optional: "pattern" (str | Mapping[str, str]), "file_stack" (bool), "backend" (str)
        split: Optional split name to resolve per-split pattern.
        splits_file: Optional splits JSON path passed to the file manager.
        splits_index: Optional split index (fold) if the splits file is a list.

    Returns:
        (target_loader, target_file_manager, task_manager)
    """
    # Required Arguments
    path = target_cfg["path"]
    file_type = target_cfg["file_type"]
    num_classes = target_cfg["classes"]
    task = target_cfg["task"]

    # Optional Arguments
    pattern = target_cfg.get("pattern")
    file_stack = target_cfg.get("file_stack", False)
    backend = target_cfg.get("backend")

    target_loader = build_target_loader(file_type, num_classes, task, backend, file_stack)
    file_manager = build_file_manager(
        path, file_type, pattern, file_stack, split, splits_file, splits_index
    )
    task_manager = build_target_manager(task)
    return target_loader, file_manager, task_manager
