import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

# ================= AYARLAR =================
BASE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "site_cikti")
HTML_DIR = os.path.join(BASE_DIR, "html")
CSS_DIR = os.path.join(BASE_DIR, "css")
JS_DIR = os.path.join(BASE_DIR, "js")
IMG_DIR = os.path.join(BASE_DIR, "img")

for d in [HTML_DIR, CSS_DIR, JS_DIR, IMG_DIR]:
    os.makedirs(d, exist_ok=True)

visited = set()
queue = deque()

# ================= PROGRESS BARLI DOWNLOAD =================
def download_file(url, folder, label="⬇️ Dosya indiriliyor"):
    try:
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code != 200:
            return None

        filename = os.path.basename(urlparse(url).path)
        if not filename:
            return None

        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        path = os.path.join(folder, filename)

        print(f"\n{label}: {filename}")

        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        percent = int(downloaded * 100 / total)
                        bar = "█" * (percent // 4)
                        print(f"\r[{bar:<25}] %{percent}", end="")

        print()
        return filename

    except Exception as e:
        print("İndirme hatası:", e)
        return None

# ================= CSS İÇİ RESİMLER =================
def process_css_images(css_content, css_url):
    def repl(match):
        img_url = urljoin(css_url, match.group(1))
        fname = download_file(img_url, IMG_DIR, "🖼️ CSS resmi indiriliyor")
        if fname:
            return f'url("../img/{fname}")'
        return match.group(0)

    return re.sub(r'url\(["\']?(.*?)["\']?\)', repl, css_content)

# ================= SAYFA İŞLE =================
def process_page(url, domain):
    if url in visited:
        return

    visited.add(url)

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
    except:
        return

    parsed = urlparse(url)
    name = parsed.path.strip("/").replace("/", "_")
    if not name:
        name = "index"
    html_filename = f"{name}.html"

    # -------- IMG --------
    for img in soup.find_all("img", src=True):
        img_url = urljoin(url, img["src"])
        fname = download_file(img_url, IMG_DIR, "🖼️ Resim indiriliyor")
        if fname:
            img["src"] = f"../img/{fname}"

    # -------- CSS --------
    for link in soup.find_all("link", rel="stylesheet", href=True):
        css_url = urljoin(url, link["href"])
        css_name = os.path.basename(urlparse(css_url).path)
        if not css_name:
            continue

        css_path = os.path.join(CSS_DIR, css_name)
        if not os.path.exists(css_path):
            try:
                css_r = requests.get(css_url, timeout=10)
                css_content = process_css_images(css_r.text, css_url)
                with open(css_path, "w", encoding="utf-8") as f:
                    f.write(css_content)
            except:
                pass

        link["href"] = f"../css/{css_name}"

    # -------- JS --------
    for script in soup.find_all("script", src=True):
        js_url = urljoin(url, script["src"])
        fname = download_file(js_url, JS_DIR, "📜 JS indiriliyor")
        if fname:
            script["src"] = f"../js/{fname}"

    # -------- LİNKLER --------
    for a in soup.find_all("a", href=True):
        link = urljoin(url, a["href"])
        p = urlparse(link)

        if p.netloc == domain:
            clean = p.scheme + "://" + p.netloc + p.path
            if clean not in visited:
                queue.append(clean)

            page_name = p.path.strip("/").replace("/", "_")
            if not page_name:
                page_name = "index"
            a["href"] = page_name + ".html"

    # -------- HTML KAYDET --------
    with open(os.path.join(HTML_DIR, html_filename), "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print(f"✅ Sayfa indirildi: {url}")

# ================= CRAWLER =================
def crawl(start_url):
    parsed = urlparse(start_url)
    domain = parsed.netloc

    queue.append(start_url)

    while queue:
        current = queue.popleft()
        process_page(current, domain)

    print("\n🎉 TÜM SİTE BAŞARIYLA İNDİRİLDİ")
    print(f"📁 Konum: {BASE_DIR}")

# ================= ÇALIŞTIR =================
if __name__ == "__main__":
    start_url = input("Site URL gir: ").strip()
    crawl(start_url)
