import os
import sys
import json
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError:
    epub = None

BOOKS_DIR = "books"
BOOKMARKS_FILE = "bookmarks.json"
LINES_PER_PAGE = 25

# --- Bookmark Utilities ---
def load_bookmarks():
    if not Path(BOOKMARKS_FILE).exists():
        return {}
    with open(BOOKMARKS_FILE, "r") as f:
        return json.load(f)

def save_bookmarks(bookmarks):
    with open(BOOKMARKS_FILE, "w") as f:
        json.dump(bookmarks, f, indent=2)

# --- TXT Reader ---
def read_txt(path, start_line=0):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_pages = len(lines) // LINES_PER_PAGE + 1
    page = start_line // LINES_PER_PAGE

    while True:
        os.system("clear")
        print(f"📖 {os.path.basename(path)} — Page {page+1}/{total_pages}")
        print("-" * 40)
        start = page * LINES_PER_PAGE
        end = start + LINES_PER_PAGE
        print("".join(lines[start:end]))
        print("-" * 40)
        print("[n]ext  [p]rev  [s]earch  [q]uit")
        cmd = input(">> ").lower()

        if cmd == "n" and end < len(lines):
            page += 1
        elif cmd == "p" and page > 0:
            page -= 1
        elif cmd == "s":
            keyword = input("Search: ")
            matches = [i for i, line in enumerate(lines) if keyword.lower() in line.lower()]
            print(f"Found {len(matches)} matches")
            if matches:
                page = matches[0] // LINES_PER_PAGE
        elif cmd == "q":
            break

    return page * LINES_PER_PAGE

# --- EPUB Reader ---
def read_epub(path, start_page=0):
    if epub is None:
        print("EPUB support not available. Install ebooklib and bs4.")
        return 0

    book = epub.read_epub(path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            chapters.append(soup.get_text())

    page = start_page
    total_pages = len(chapters)

    while True:
        os.system("clear")
        print(f"📖 {os.path.basename(path)} — Chapter {page+1}/{total_pages}")
        print("-" * 40)
        print(chapters[page][:3000])
        print("-" * 40)
        print("[n]ext  [p]rev  [q]uit")
        cmd = input(">> ").lower()
        if cmd == "n" and page + 1 < total_pages:
            page += 1
        elif cmd == "p" and page > 0:
            page -= 1
        elif cmd == "q":
            break

    return page

# --- PDF Reader ---
def read_pdf(path, start_page=0):
    if fitz is None:
        print("PDF support not available. Install PyMuPDF.")
        return 0

    doc = fitz.open(path)
    page = start_page
    total_pages = len(doc)

    while True:
        os.system("clear")
        print(f"📖 {os.path.basename(path)} — Page {page+1}/{total_pages}")
        print("-" * 40)
        print(doc[page].get_text())
        print("-" * 40)
        print("[n]ext  [p]rev  [q]uit")
        cmd = input(">> ").lower()
        if cmd == "n" and page + 1 < total_pages:
            page += 1
        elif cmd == "p" and page > 0:
            page -= 1
        elif cmd == "q":
            break

    return page

# --- Main Menu ---
def main():
    os.makedirs(BOOKS_DIR, exist_ok=True)
    bookmarks = load_bookmarks()

    books = sorted([f for f in os.listdir(BOOKS_DIR) if f.endswith(('.txt', '.epub', '.pdf'))])
    if not books:
        print("No supported books found in 'books/' directory.")
        return

    print("📚 Your Library:")
    for i, book in enumerate(books):
        print(f"{i+1}. {book}")
    choice = int(input("Select book #: ")) - 1
    book = books[choice]
    path = os.path.join(BOOKS_DIR, book)
    ext = Path(book).suffix.lower()

    last_pos = bookmarks.get(book, 0)

    if ext == ".txt":
        new_pos = read_txt(path, start_line=last_pos)
    elif ext == ".epub":
        new_pos = read_epub(path, start_page=last_pos)
    elif ext == ".pdf":
        new_pos = read_pdf(path, start_page=last_pos)
    else:
        print("Unsupported file type.")
        return

    bookmarks[book] = new_pos
    save_bookmarks(bookmarks)
    print("✅ Progress saved.")

if __name__ == "__main__":
    main()
