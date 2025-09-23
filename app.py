import os
import re
import fitz  
from PyPDF2 import PdfWriter


KEYWORDS = [
    "opinion", "editorial", "op-ed", "letters to the editor",
    "columns", "commentary", "viewpoint"
]

def is_editorial_page(text: str) -> bool:
    text_lower = text.lower()
    return any(re.search(rf"\b{kw}\b", text_lower) for kw in KEYWORDS)

def extract_editorial_pages(input_folder: str, output_file: str):
    writer = PdfWriter()

    for pdf_name in os.listdir(input_folder):
        if not pdf_name.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(input_folder, pdf_name)
        print(f"[INFO] Processing: {pdf_path}")

        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            if is_editorial_page(text):
                print(f"  -> Extracting page {page_num + 1}")
                # Create a temporary PDF of this single page
                single_page_pdf = fitz.open()
                single_page_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
                temp_path = f"temp_{os.getpid()}_{page_num}.pdf"
                single_page_pdf.save(temp_path)
                single_page_pdf.close()

                # Append to final writer
                with open(temp_path, "rb") as f:
                    writer.append(f)

                os.remove(temp_path)

        doc.close()

    with open(output_file, "wb") as f_out:
        writer.write(f_out)

    print(f"[SUCCESS] Consolidated file created: {output_file}")

if __name__ == "__main__":
    INPUT_FOLDER = "newspapers"
    OUTPUT_FILE = "editorials.pdf"
    extract_editorial_pages(INPUT_FOLDER, OUTPUT_FILE)
