import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog
import re
import os
import time

def banner():
    os.system("cls" if os.name == "nt" else "clear")
    print("=====================================")
    print("  2026 KAFF1N8T3D")
    print("")
    print("         )  (")
    print("         (   ) )")
    print("          ) ( (")
    print("       _______)__")
    print("   .-^|-(C)------|")
    print("  ( C^|          |")
    print("   '-^|KAFF1N8T3D|")
    print("      '__________'")
    print("       '--------'")
    print("")
    print("  2026 KAFF1N8T3D")
    print("=====================================")
    print("")

def splash_page():

    print(r"""
   __________________________________________________________
 / \                                                          \.
| O |                 GLO Map Downloader v.1.1                 |.
 \__|                                                          |.
    | This program will download the full size image of any    |.
    | map shown on the GLO website. The full size image is     |.
    | already linked in your browser when you load the page,   |.
    | but the site works hard to cover up it's location. It    |.
    | then slices up the full size image into little slices    |.
    | and reconstructs the image. These little slices are      |.
    | what is shown to the world through the browser. This     |.
    | enables you, from the webpage, to zoom into the image    |.
    | and read the small details with clarity, but seemingly   |.
    | you cannot download the fullsize image.                  |.
    |                                                          |.
    | GLO Map Downloader finds the already public -full size   |.
    | image and downloads it to your desired location.         |.
    |                                                          |.
    |                     Instructions:                        |.
    | 1.  Copy and Enter the URL address for the page that     |.
    | displays the map image you desire to download.           |.
    |                                                          |.
    | 2. The Map Name is the default save name, but you can    |.
    | choose another name and a location to save the full      |.
    | size image to.                                           |.
    |   _______________________________________________________|___
    |  /                                                          /.
    \_/__________________________________________________________/.
""")

def clean_filename(name):
    """Remove invalid filename characters and normalize spacing"""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', ' ', name)  # collapse whitespace
    return name.strip()


def get_page_data(page_url):
    """Scrape page for title (from img alt) + IIIF base URL"""
    response = requests.get(page_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # ---- GET IMAGE ----
    img_tag = soup.select_one(".preview-image img")
    if not img_tag:
        raise Exception("Could not find preview image.")

    img_src = img_tag["src"]

    # ---- GET TITLE FROM ALT ----
    if img_tag.has_attr("alt") and img_tag["alt"].strip():
        title = clean_filename(img_tag["alt"])
    else:
        # fallback to h1 if alt missing
        title_tag = soup.find("h1")
        if title_tag:
            title = clean_filename(title_tag.get_text())
        else:
            title = "map_download"

    # Extract filename after /maps/
    filename = img_src.split("/maps/")[-1]

    # Build IIIF base URL
    iiif_base = f"https://historictexasmaps.com/iiif-server/iiif/3/maps%7C{filename}"

    return title, iiif_base


def get_full_size(iiif_base):
    """Fetch JSON metadata to get full image dimensions"""
    response = requests.get(iiif_base)
    response.raise_for_status()

    data = response.json()

    return data["width"], data["height"]


def build_full_image_url(iiif_base, width, height):
    return f"{iiif_base}/0,0,{width},{height}/{width},{height}/0/default.jpg"


def choose_save_location(default_name):
    root = tk.Tk()
    root.withdraw()

    return filedialog.asksaveasfilename(
        defaultextension=".jpg",
        initialfile=default_name,
        filetypes=[("JPEG files", "*.jpg")]
    )


def download_image(title, url, save_path):
    print(f"\nDownloading:\n{title}\n")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        for chunk in response.iter_content(8192):
            f.write(chunk)

    print(f"Saved to: {save_path}\n")


def main():
    while True:
        splash_page()
        try:
            page_url = input("What GLO page has the map document? (or 'q' to quit): ").strip()

            if page_url.lower() == "q":
                break

            # Step 1: Get title + IIIF base
            title, iiif_base = get_page_data(page_url)
            print(f"Title: {title}")
            #print(f"IIIF Base: {iiif_base}")

            # Step 2: Get full size
            width, height = get_full_size(iiif_base)
            print(f"Full size: {width} x {height}")

            # Step 3: Build full image URL
            full_image_url = build_full_image_url(iiif_base, width, height)

            # Step 4: Save dialog with title
            default_name = f"{title}.jpg"
            save_path = choose_save_location(default_name)

            if not save_path:
                print("Save cancelled.\n")
                continue

            # Step 5: Download
            download_image(title, full_image_url, save_path)

        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    os.system("title GLO Map Downloader v.1.1")
    banner()
    time.sleep(2)# pauses for 2 seconds
    os.system("cls" if os.name == "nt" else "clear")
    main()