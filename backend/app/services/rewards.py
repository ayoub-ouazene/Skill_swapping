import os
import smtplib
from email.message import EmailMessage
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

def generate_certificate_pdf(teacher_name: str, student_name: str, skill_name: str, duration: float, cert_id: str) -> str:
    """
    Generates a beautiful PDF certificate and saves it temporarily.
    Returns the file path.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Add a border
    pdf.rect(5.0, 5.0, 200.0, 287.0)
    
    # Title
    pdf.set_font("helvetica", "B", 24)
    pdf.cell(0, 40, "Official SkillSwap Certificate", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Body
    pdf.set_font("helvetica", "", 16)
    pdf.multi_cell(0, 10, f"This certifies that\n\n**{teacher_name}**\n\nhas successfully taught a {duration}-hour session on\n\n**{skill_name}**\n\nto {student_name}.", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Footer with the secure ID (so the AI can read it later when they upload it!)
    pdf.set_y(-50)
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(0, 10, f"Secure Certificate ID: {cert_id}", align="C")
    
    # Save the file
    os.makedirs("temp_uploads", exist_ok=True)
    file_path = f"temp_uploads/{cert_id}.pdf"
    pdf.output(file_path)
    
    return file_path

def send_certificate_email(teacher_email: str, pdf_path: str):
    """
    Emails the generated PDF to the teacher.
    """
    sender_email = os.getenv("EMAIL_SENDER") # e.g., your startup's gmail
    sender_password = os.getenv("EMAIL_PASSWORD") # Gmail App Password
    
    # If email isn't configured in .env, we just skip sending to avoid crashing during dev
    if not sender_email or not sender_password:
        print(f"⚠️ Dev Mode: Skipped emailing {teacher_email}. PDF saved at {pdf_path}")
        return

    msg = EmailMessage()
    msg['Subject'] = 'Your SkillSwap Teaching Certificate is here!'
    msg['From'] = sender_email
    msg['To'] = teacher_email
    msg.set_content("Congratulations! Attached is your official teaching certificate. You can upload this to the platform whenever you are ready to claim your Time Credits based on current market demand.")

    # Attach the PDF
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename="SkillSwap_Certificate.pdf")

    # Send the email via Gmail SMTP
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")