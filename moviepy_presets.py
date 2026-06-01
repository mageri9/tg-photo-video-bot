from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Dict
import numpy as np
import cv2
import imageio.v3 as iio

from moviepy.editor import VideoClip


@dataclass(frozen=True)
class KenBurnsPreset:
    # zoom: 1.0 = без зума, 1.15 = приблизить на 15%
    zoom_start: float
    zoom_end: float

    # start/end — центр кадрирования в долях от изображения (0..1)
    # (0.5,0.5) = центр, (0.2,0.5) = левее центра
    start: Tuple[float, float]
    end: Tuple[float, float]


PRESETS: Dict[str, KenBurnsPreset] = {
    "zoom_in":   KenBurnsPreset(1.00, 1.15, (0.50, 0.50), (0.50, 0.50)),
    "zoom_out":  KenBurnsPreset(1.15, 1.00, (0.50, 0.50), (0.50, 0.50)),

    "pan_left":  KenBurnsPreset(1.08, 1.08, (0.25, 0.50), (0.75, 0.50)),
    "pan_right": KenBurnsPreset(1.08, 1.08, (0.75, 0.50), (0.25, 0.50)),

    "pan_up":    KenBurnsPreset(1.08, 1.08, (0.50, 0.25), (0.50, 0.75)),
    "pan_down":  KenBurnsPreset(1.08, 1.08, (0.50, 0.75), (0.50, 0.25)),

    "diag":      KenBurnsPreset(1.02, 1.14, (0.35, 0.35), (0.65, 0.65)),
}


def make_ken_burns_clip(
    image_path: str,
    preset: str = "zoom_in",
    duration: float = 6.0,
    fps: int = 30,
    out_size: Tuple[int, int] = (1280, 720),
) -> VideoClip:
    """
    Делает VideoClip из 1 изображения с Ken Burns (zoom/pan).
    Внутри использует VideoClip(make_frame=...), где make_frame(t) -> numpy RGB frame.
    """

    if preset not in PRESETS:
        raise ValueError(f"Unknown preset '{preset}'. Available: {list(PRESETS)}")

    p = PRESETS[preset]

    img = iio.imread(image_path)  # RGB numpy array
    if img.ndim == 2:
        img = np.stack([img, img, img], axis=-1)
    if img.shape[2] == 4:
        img = img[:, :, :3]

    H, W = img.shape[:2]
    out_w, out_h = out_size
    out_ar = out_w / out_h

    def frame_at_time(t: float) -> np.ndarray:
        # прогресс 0..1
        if duration <= 0:
            u = 1.0
        else:
            u = min(max(t / duration, 0.0), 1.0)

        # zoom
        z = p.zoom_start + (p.zoom_end - p.zoom_start) * u

        # размер окна кропа в исходных координатах (чтобы после resize получить out_size)
        crop_w = int(W / z)
        crop_h = int(crop_w / out_ar)

        # если по высоте не помещается — пересчёт от высоты
        max_crop_h = int(H / z)
        if crop_h > max_crop_h:
            crop_h = max_crop_h
            crop_w = int(crop_h * out_ar)

        crop_w = max(2, min(crop_w, W))
        crop_h = max(2, min(crop_h, H))

        # центр (в пикселях) двигается от start к end
        cx = int((p.start[0] + (p.end[0] - p.start[0]) * u) * W)
        cy = int((p.start[1] + (p.end[1] - p.start[1]) * u) * H)

        x1 = int(np.clip(cx - crop_w // 2, 0, W - crop_w))
        y1 = int(np.clip(cy - crop_h // 2, 0, H - crop_h))

        crop = img[y1:y1 + crop_h, x1:x1 + crop_w]
        frame = cv2.resize(crop, (out_w, out_h), interpolation=cv2.INTER_CUBIC)
        return frame

    clip = VideoClip(make_frame=frame_at_time, duration=duration).set_fps(fps)
    return clip


def render_ken_burns_mp4(
    image_path: str,
    out_mp4_path: str,
    preset: str = "zoom_in",
    duration: float = 6.0,
    fps: int = 30,
    out_size: Tuple[int, int] = (1280, 720),
) -> str:
    clip = make_ken_burns_clip(
        image_path=image_path,
        preset=preset,
        duration=duration,
        fps=fps,
        out_size=out_size,
    )

    # yuv420p + faststart — чтобы Telegram/мобилки открывали без сюрпризов
    clip.write_videofile(
        out_mp4_path,
        fps=fps,
        codec="libx264",
        audio=False,
        preset="veryfast",
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
        verbose=False,
        logger=None,
    )
    clip.close()
    return out_mp4_path