from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import re


class PipelineException(Exception):
    def __init__(self, stage: str, reason: str) -> None:
        self.stage = stage
        self.reason = reason
        super().__init__(f"[{stage}] {reason}")


@dataclass(frozen=True)
class GeneratedImage:
    url: str
    prompt: str
    style: str
    provider: str
    biaya: float


@dataclass(frozen=True)
class GeneratedVideo:
    url: str
    source_image: GeneratedImage
    motion_prompt: str
    provider: str
    biaya: float


class ImageGenerator(ABC):
    nama: str = "base"
    biaya_per_gambar: float = 0.0

    def _build_full_prompt(self, prompt: str, style: str) -> str:
        prompt = (prompt or "").strip()
        style = (style or "").strip()
        if not prompt:
            raise PipelineException("IMAGE_GEN", "prompt tidak boleh kosong")
        if style:
            return f"{prompt}, {style} style"
        return prompt

    @abstractmethod
    def generate(self, prompt: str, style: str) -> GeneratedImage:
        raise NotImplementedError


class MockImageGenerator(ImageGenerator):
    nama = "mock"
    biaya_per_gambar = 0.0

    def generate(self, prompt: str, style: str) -> GeneratedImage:
        full = self._build_full_prompt(prompt, style)
        slug = re.sub(r"[^a-z0-9]+", "-", full.lower()).strip("-")[:40] or "image"
        return GeneratedImage(
            url=f"https://mock.local/{slug}.png",
            prompt=full,
            style=style.strip() or "default",
            provider=self.nama,
            biaya=self.biaya_per_gambar,
        )


class MockVideoGenerator:
    nama = "mock-video"
    biaya_per_video = 0.0

    def generate(self, gambar: GeneratedImage, motion_prompt: str) -> GeneratedVideo:
        motion = (motion_prompt or "").strip()
        if not motion:
            raise PipelineException("VIDEO_GEN", "motion prompt tidak boleh kosong")
        slug = re.sub(r"[^a-z0-9]+", "-", f"{gambar.style}-{motion}".lower()).strip("-")[:40]
        return GeneratedVideo(
            url=f"https://mock.local/video-{slug or 'video'}.mp4",
            source_image=gambar,
            motion_prompt=motion,
            provider=self.nama,
            biaya=self.biaya_per_video,
        )


@dataclass
class ContentProject:
    prompt: str
    style: str
    gambar_list: list[GeneratedImage] = field(default_factory=list)
    video_list: list = field(default_factory=list)
    gambar_terpilih: GeneratedImage | None = None

    def tambah_gambar(self, gambar: GeneratedImage) -> None:
        self.gambar_list.append(gambar)

    def tambah_video(self, video: GeneratedVideo) -> None:
        self.video_list.append(video)

    def pilih_untuk_video(self, idx: int) -> GeneratedImage:
        if not 0 <= idx < len(self.gambar_list):
            raise PipelineException(
                "SELECT", f"index {idx} di luar jangkauan (0..{len(self.gambar_list) - 1})"
            )
        self.gambar_terpilih = self.gambar_list[idx]
        return self.gambar_terpilih

    def estimasi_biaya(self) -> float:
        biaya_video = sum(getattr(video, "biaya", 0.0) for video in self.video_list)
        return sum(gambar.biaya for gambar in self.gambar_list) + biaya_video


class ContentPipeline:
    def __init__(
        self,
        generator: ImageGenerator,
        video_generator: MockVideoGenerator | None = None,
    ) -> None:
        self.generator = generator
        self.video_generator = video_generator or MockVideoGenerator()
        self.projects: list[ContentProject] = []
        self.video_eksternal: list[GeneratedVideo] = []

    def jalankan(self, prompt: str, style: str) -> ContentProject:
        project = ContentProject(prompt=(prompt or "").strip(), style=(style or "").strip())
        gambar = self.generator.generate(project.prompt, project.style)
        project.tambah_gambar(gambar)
        self.projects.append(project)
        return project

    def jalankan_video(
        self, project: ContentProject, idx: int, motion_prompt: str
    ) -> GeneratedVideo:
        gambar = project.pilih_untuk_video(idx)
        video = self.video_generator.generate(gambar, motion_prompt)
        project.tambah_video(video)
        return video

    def jalankan_video_eksternal(self, sumber: str, motion_prompt: str) -> GeneratedVideo:
        sumber = (sumber or "").strip()
        if not sumber:
            raise PipelineException("VIDEO_GEN", "sumber gambar eksternal tidak boleh kosong")
        gambar = GeneratedImage(
            url=sumber,
            prompt="(gambar eksternal)",
            style="external",
            provider="external",
            biaya=0.0,
        )
        video = self.video_generator.generate(gambar, motion_prompt)
        self.video_eksternal.append(video)
        return video
