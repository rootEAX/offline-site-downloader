import subprocess
import sys
import importlib

# pip adı : import adı
REQUIRED_PACKAGES = {
    "requests": "requests",
    "beautifulsoup4": "bs4",
    "tqdm": "tqdm"
}

def install(package):
    print(f"📦 Yükleniyor: {package}")
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        package
    ])

def main():
    print("🔧 Gerekli Python paketleri kontrol ediliyor...\n")

    for pip_name, import_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(import_name)
            print(f"✅ Zaten yüklü: {pip_name}")
        except ImportError:
            try:
                install(pip_name)
                print(f"✅ Kuruldu: {pip_name}")
            except Exception as e:
                print(f"❌ Hata oluştu ({pip_name}): {e}")

    print("\n🎉 Tüm işlemler tamamlandı")

if __name__ == "__main__":
    main()
