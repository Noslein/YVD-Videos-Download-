import os
import sys
import subprocess
import shutil
from yt_dlp import YoutubeDL
import platform

# script.py
# Baixa um vídeo do YouTube em 1080p ou 720p e salva em C:\Users\Downloads
# Requisito: ffmpeg (para mesclar video+audio) e yt-dlp (o script tenta instalar se faltar)

# substitui a constante fixa DOWNLOAD_DIR por uma detecção automática
def get_downloads_folder():
    home = os.path.expanduser("~")
    system = platform.system()
    if system == "Windows":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                val, _ = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")
                # valor pode conter %USERPROFILE% -> expandir
                downloads = os.path.expandvars(val)
                downloads = os.path.expanduser(downloads)
                return downloads
        except Exception:
            return os.path.join(home, "Downloads")
    else:
        # tenta XDG user-dirs (Linux)
        try:
            cfg = os.path.join(home, ".config", "user-dirs.dirs")
            if os.path.isfile(cfg):
                with open(cfg, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("XDG_DOWNLOAD_DIR"):
                            import re
                            m = re.match(r'XDG_DOWNLOAD_DIR=(?P<q>["\']?)(?P<path>.*?)(?P=q)$', line.strip())
                            if m:
                                path = m.group("path")
                                path = path.replace("$HOME", home)
                                path = os.path.expandvars(path)
                                path = os.path.expanduser(path)
                                return path
        except Exception:
            pass
        return os.path.join(home, "Downloads")

DOWNLOAD_DIR = get_downloads_folder()

def ensure_yt_dlp():
    try:
        import yt_dlp  # noqa: F401
    except Exception:
        print("Instalando yt-dlp (necessário)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    finally:
        global YoutubeDL

def download_youtube(url: str):
    # tenta 1080p, cai para 720p; mescla para mp4 (precisa ffmpeg no PATH)
    # tenta localizar ffmpeg no PATH, senão usa o caminho do Chocolatey
    ffmpeg_exec = shutil.which("ffmpeg")
    ffmpeg_dir = os.path.dirname(ffmpeg_exec) if ffmpeg_exec else r"C:\ProgramData\chocolatey\bin"

    ydl_opts = {
        "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best[height<=720]+bestaudio/best[height<=720]",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4",
        "ffmpeg_location": ffmpeg_dir,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print("Erro ao baixar:", e)
        sys.exit(1)

def main():
    # se a pasta não existir, cria (evita sair para usuários que moveram a pasta)
    if not os.path.isdir(DOWNLOAD_DIR):
        try:
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            print(f"Pasta de destino criada: {DOWNLOAD_DIR}")
        except Exception:
            print(f"Pasta de destino não existe e não pôde ser criada: {DOWNLOAD_DIR}")
            sys.exit(1)

    url = input("Cole o link do YouTube e pressione Enter: ").strip()
    if not url:
        print("Nenhum link fornecido. Saindo.")
        sys.exit(0)

    # aviso curto: baixe apenas conteúdo com permissão
    print("Todos os direitos reservados ao autor(a) ou autores do vídeo.")
    ensure_yt_dlp()
    download_youtube(url)
    print("Concluído. Verifique sua pasta de Downloads.")

if __name__ == "__main__":
    main()