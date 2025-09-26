import os
import fitz  # PyMuPDF
from PyPDF2 import PdfWriter
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def is_editorial_page(text: str) -> bool:
    """
    Uses a Groq LLM to classify whether a page is an editorial/opinion piece.
    """
    if not text.strip():
        return False

    prompt = f"""
    You are a document classifier.
    Determine if the following page is an 'editorial' or 'opinion piece' 
    from a newspaper. Answer strictly with YES or NO.

    Page content:
    {text}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        answer = response.choices[0].message.content.strip().upper()
        return answer == "YES"
    except Exception as e:
        print(f"[ERROR] LLM classification failed: {e}")
        return False


def extract_editorial_pages(input_folder: str, output_file: str):
    """
    Extracts editorial pages from all PDFs in input_folder
    and saves them into a consolidated PDF.
    """
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
                single_page_pdf = fitz.open()
                single_page_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)

                temp_path = f"temp_{os.getpid()}_{page_num}.pdf"
                single_page_pdf.save(temp_path)
                single_page_pdf.close()

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
