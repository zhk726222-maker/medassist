import os
import time
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 默沙东诊疗手册中文版 - 常见疾病和症状
URLS = [
    # 已验证可访问的页面
    "https://www.msdmanuals.cn/home/lung-and-airway-disorders/asthma/asthma",
    "https://www.msdmanuals.cn/home/brain-spinal-cord-and-nerve-disorders/stroke/overview-of-stroke",
    "https://www.msdmanuals.cn/home/digestive-disorders/gastritis-and-peptic-ulcer-disease/peptic-ulcer-disease",
    "https://www.msdmanuals.cn/home/bone-joint-and-muscle-disorders/osteoporosis/osteoporosis",
    "https://www.msdmanuals.cn/home/immune-disorders/allergic-reactions-and-other-hypersensitivity-disorders/overview-of-allergic-reactions",
    "https://www.msdmanuals.cn/home/heart-and-blood-vessel-disorders/symptoms-of-heart-and-blood-vessel-disorders/chest-pain",
    "https://www.msdmanuals.cn/home/blood-disorders/anemia/overview-of-anemia",
    # 从症状页爬取的真实链接
    "https://www.msdmanuals.cn/home/brain-spinal-cord-and-nerve-disorders/headaches/overview-of-headache",
    "https://www.msdmanuals.cn/home/lung-and-airway-disorders/symptoms-of-lung-disorders/shortness-of-breath",
    "https://www.msdmanuals.cn/home/digestive-disorders/symptoms-of-digestive-disorders/lump-in-throat",
    "https://www.msdmanuals.cn/home/digestive-disorders/gastrointestinal-bleeding/gastrointestinal-bleeding",
    "https://www.msdmanuals.cn/home/brain-spinal-cord-and-nerve-disorders/symptoms-of-brain-spinal-cord-and-nerve-disorders/memory-loss",
    "https://www.msdmanuals.cn/home/brain-spinal-cord-and-nerve-disorders/symptoms-of-brain-spinal-cord-and-nerve-disorders/weakness",
    "https://www.msdmanuals.cn/home/kidney-and-urinary-tract-disorders/symptoms-of-kidney-disorders/blood-in-urine",
    "https://www.msdmanuals.cn/home/eye-disorders/symptoms-of-eye-disorders/blurred-vision",
    "https://www.msdmanuals.cn/home/eye-disorders/symptoms-of-eye-disorders/sudden-vision-loss",
    "https://www.msdmanuals.cn/home/heart-and-blood-vessel-disorders/symptoms-of-heart-and-blood-vessel-disorders/palpitations",
    "https://www.msdmanuals.cn/home/ear-nose-and-throat-disorders/symptoms-of-nose-and-throat-disorders/nasal-congestion-and-discharge",
    "https://www.msdmanuals.cn/home/kidney-and-urinary-tract-disorders/symptoms-of-kidney-disorders/excessive-or-frequent-urination",
    "https://www.msdmanuals.cn/home/children-s-health-issues/symptoms-in-infants-and-children/diarrhea-in-children",
]

SAVE_DIR = "data/raw"

def make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=2,
                  status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

session = make_session()

def fetch_and_clean(url: str) -> str:
    resp = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # 默沙东手册正文在article标签里
    content = soup.find("article") or soup.find("main") or soup
    
    # 去掉脚注、导航、广告等干扰内容
    for tag in content.find_all(["nav", "footer", "aside", "script", "style"]):
        tag.decompose()

    text = content.get_text(separator="\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)

def main():
    os.makedirs(SAVE_DIR, exist_ok=True)
    success = 0
    failed = []

    for i, url in enumerate(URLS):
        filename = url.rstrip("/").split("/")[-1][:50]
        filepath = os.path.join(SAVE_DIR, f"{filename}.txt")

        # 如果文件已存在就跳过,避免重复抓取
        if os.path.exists(filepath):
            print(f"已存在,跳过 ({i+1}/{len(URLS)}): {filename}")
            success += 1
            continue

        print(f"正在抓取 ({i+1}/{len(URLS)}): {filename}")
        try:
            text = fetch_and_clean(url)
            if len(text) < 200:
                print(f"  内容太少({len(text)}字符),跳过")
                failed.append(url)
                continue
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"  已保存: {len(text)} 字符")
            success += 1
        except Exception as e:
            print(f"  失败: {e}")
            failed.append(url)
        time.sleep(2)

    print(f"\n完成: 成功{success}/{len(URLS)}")
    if failed:
        print(f"失败{len(failed)}个:")
        for u in failed:
            print(f"  {u}")

if __name__ == "__main__":
    main()