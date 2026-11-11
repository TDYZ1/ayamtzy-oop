# AI Content Creator Studio — Teks -> Gambar -> Video Pipeline

Proyek UTS PPBO 11.OODP.201 (OOP Python). Tahap UTS mengerjakan fitur 1–10:
pipeline teks -> gambar dengan CLI, ABC, polymorphism, dan exception handling.

## Struktur

```
content_pipeline.py   # exception, model, ABC, generator, pipeline
main.py               # CLI
selfcheck.py          # uji manual berbasis assert
docs/class_diagram.md # diagram UML (Mermaid)
laporan_tahap1.docx   # laporan portofolio Tahap 1
```

## Menjalankan

```
python main.py
python selfcheck.py
```

Tanpa dependency eksternal (Python 3.10+).

Menu:
1. Generate gambar (buat project baru)
2. Generate video dari gambar (mock)
3. Lihat semua project + estimasi biaya
0. Keluar

## Provider

Saat ini hanya `MockImageGenerator` (offline, tanpa API key, biaya USD 0.00).
`DALLEImageGenerator` dihapus sementara; fitur UTS nomor 2 belum terpenuhi dan
direncanakan dikembalikan sebelum pengumpulan.

## Mapping fitur UTS

| # | Fitur | Implementasi |
|---|---|---|
| 1 | ABC `ImageGenerator` | `content_pipeline.ImageGenerator` |
| 2 | `DALLEImageGenerator.generate()` | dihapus sementara (belum terpenuhi) |
| 3 | `MockImageGenerator` offline | `content_pipeline.py` |
| 4 | `PipelineException('IMAGE_GEN', ...)` | `_build_full_prompt()` |
| 5 | `_build_full_prompt()` | `ImageGenerator` |
| 6 | `GeneratedImage` (url, prompt, style, provider, biaya) | dataclass |
| 7 | `ContentProject.gambar_list` / `video_list` | dataclass |
| 8 | `pilih_untuk_video(idx)` | `ContentProject` |
| 9 | `ContentPipeline.jalankan()` Tahap 1 | `ContentPipeline` |
| 10 | Info gambar + estimasi biaya | `main.py` |

## Konsep OOP wajib

- **Inheritance / ABC**: `ImageGenerator(ABC)` dengan `@abstractmethod generate()`; `MockImageGenerator` meng-override.
- **Polymorphism**: `ContentPipeline` memanggil `self.generator.generate(...)` lewat tipe base.
- **Exception Handling**: `PipelineException` untuk prompt/index/motion prompt invalid, ditangkap di loop CLI agar program tidak berhenti.

## Video (mock)

Menu 2 menjalankan tahap gambar -> video dengan `MockVideoGenerator` (offline,
biaya USD 0.00). Dua pilihan sumber:
1. Project yang sudah ada: pilih project lalu pilih gambar sumber.
2. Gambar eksternal: masukkan path/URL gambar.
Setelah itu masukkan motion prompt.
Hasil `GeneratedVideo` (url, source_image, motion_prompt, provider, biaya)
disimpan ke `ContentProject.video_list`, jadi jumlah video ikut tampil di menu 3.

## Ditunda ke UAS

Fitur 13–20: `VideoGenerationQueue`, Iterator Pattern, pytest, GUI/API.
Provider video asli (Kling/Higgsfield/Luma) belum diimplementasikan; saat ini mock.
