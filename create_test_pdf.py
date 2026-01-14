from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "Chapter 1: Newton's Laws of Motion")
    
    text = c.beginText(100, 730)
    text.setFont("Helvetica", 12)
    lines = [
        "Newton's First Law: An object at rest stays at rest.",
        "Newton's Second Law: F = ma.",
        "Newton's Third Law: For every action, there is an equal and opposite reaction."
    ]
    for line in lines:
        text.textLine(line)
        
    c.drawText(text)
    c.save()

if __name__ == "__main__":
    os.makedirs("input", exist_ok=True)
    create_test_pdf("input/newton.pdf")
