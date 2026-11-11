from content_pipeline import (
    ContentPipeline,
    ContentProject,
    MockImageGenerator,
    PipelineException,
)

MENU = """
=== AI Content Creator Studio ===
1. Generate gambar (project baru)
2. Generate video dari gambar (mock)
3. Lihat semua project & estimasi biaya
0. Keluar
"""


def tanya(label: str, default: str = "") -> str:
    try:
        value = input(label).strip()
    except EOFError:
        return default
    return value or default


def tanya_pilihan(label: str, maks: int) -> int:
    raw = tanya(label)
    try:
        value = int(raw)
    except ValueError:
        raise PipelineException("INPUT", f"{raw!r} bukan angka") from None
    if not 1 <= value <= maks:
        raise PipelineException("SELECT", f"pilihan harus 1..{maks}")
    return value - 1


def tampil_gambar(project: ContentProject) -> None:
    for nomor, gambar in enumerate(project.gambar_list, start=1):
        print(f"  {nomor}. [{gambar.provider}] style={gambar.style} biaya=USD {gambar.biaya:.2f}")
        print(f"     prompt: {gambar.prompt}")
        print(f"     url   : {gambar.url}")


def menu_generate(pipeline: ContentPipeline) -> None:
    prompt = tanya("Prompt: ")
    style = tanya("Style (mis. cinematic/anime/3d, default realistic): ", "realistic")
    project = pipeline.jalankan(prompt, style)
    gambar = project.gambar_list[0]
    print(f"\nGambar berhasil dibuat oleh provider {gambar.provider}.")
    tampil_gambar(project)
    print(f"Estimasi biaya project: USD {project.estimasi_biaya():.2f}")


def tampil_video_item(nomor: int, video) -> None:
    print(f"  {nomor}. [{video.provider}] biaya=USD {video.biaya:.2f}")
    print(f"     motion: {video.motion_prompt}")
    print(f"     url   : {video.url}")
    print(f"     sumber: {video.source_image.url}")


def tampil_video(project: ContentProject) -> None:
    for nomor, video in enumerate(project.video_list, start=1):
        tampil_video_item(nomor, video)


def menu_generate_video(pipeline: ContentPipeline) -> None:
    print("Sumber video: 1. Project yang sudah ada  2. Gambar eksternal")
    sumber = tanya_pilihan("Pilih sumber [1/2]: ", 2)

    if sumber == 1:
        sumber_gambar = tanya("Path/URL gambar eksternal: ")
        motion = tanya("Motion prompt (default 'slow zoom in'): ", "slow zoom in")
        video = pipeline.jalankan_video_eksternal(sumber_gambar, motion)
        print("\nVideo berhasil dibuat (mock) dari gambar eksternal.")
        tampil_video_item(1, video)
        return

    if not pipeline.projects:
        print("Belum ada project. Pilih sumber 2 (gambar eksternal) atau generate gambar dulu.")
        return
    for nomor, project in enumerate(pipeline.projects, start=1):
        print(f"  {nomor}. {project.prompt} ({len(project.gambar_list)} gambar)")
    index_project = tanya_pilihan("Pilih project: ", len(pipeline.projects))
    project = pipeline.projects[index_project]
    tampil_gambar(project)
    index_gambar = tanya_pilihan("Pilih gambar sumber video: ", len(project.gambar_list))
    motion = tanya("Motion prompt (default 'slow zoom in'): ", "slow zoom in")
    video = pipeline.jalankan_video(project, index_gambar, motion)
    print("\nVideo berhasil dibuat (mock).")
    tampil_video(project)
    print(f"Estimasi biaya project: USD {project.estimasi_biaya():.2f}")


def menu_lihat(pipeline: ContentPipeline) -> None:
    if not pipeline.projects and not pipeline.video_eksternal:
        print("Belum ada project.")
        return
    total = 0.0
    for nomor, project in enumerate(pipeline.projects, start=1):
        biaya = project.estimasi_biaya()
        total += biaya
        print(
            f"  {nomor}. {project.prompt} | style={project.style} | "
            f"gambar={len(project.gambar_list)} | video={len(project.video_list)} | "
            f"biaya=USD {biaya:.2f}"
        )
        if project.gambar_terpilih:
            print(f"     gambar video: {project.gambar_terpilih.url}")
        for video in project.video_list:
            print(f"     video: {video.motion_prompt} -> {video.url}")
    if pipeline.video_eksternal:
        print("Video dari gambar eksternal:")
        for nomor, video in enumerate(pipeline.video_eksternal, start=1):
            tampil_video_item(nomor, video)
            total += video.biaya
    print(f"Total estimasi biaya semua project: USD {total:.2f}")


def main() -> None:
    pipeline = ContentPipeline(MockImageGenerator())
    print("Selamat datang di AI Content Creator Studio (Tahap 1: Teks -> Gambar).")
    while True:
        print(MENU)
        pilihan = tanya("Pilih menu: ")
        try:
            if pilihan == "1":
                menu_generate(pipeline)
            elif pilihan == "2":
                menu_generate_video(pipeline)
            elif pilihan == "3":
                menu_lihat(pipeline)
            elif pilihan == "0":
                break
            else:
                print("Menu tidak dikenal.")
        except PipelineException as error:
            print(f"Error: {error}")
        except KeyboardInterrupt:
            print()
            break
    print("Selesai.")


if __name__ == "__main__":
    main()
