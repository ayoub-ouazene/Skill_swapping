import os
import resend
from email.message import EmailMessage
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

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
    Emails the generated PDF to the teacher using Resend.
    """
    # Check if Resend is configured
    if not resend.api_key:
        print("⚠️ Dev Mode: RESEND_API_KEY not set. Skipping email.")
        return

    sender_email = os.getenv("EMAIL_SENDER")
    if not sender_email:
        print("⚠️ Dev Mode: EMAIL_SENDER not set. Skipping email.")
        return

    # Read PDF file as bytes
    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    # Prepare email content
    subject = "Your SkillSwap Teaching Certificate is here!"
    html_content = """
    <html>
        <body>
            <p>Congratulations! Attached is your official teaching certificate.</p>
            <p>You can upload this to the platform whenever you are ready to claim your Time Credits based on current market demand.</p>
            <p>Best regards,<br>SkillSwap Team</p>
        </body>
    </html>
    """
    plain_text = "Congratulations! Attached is your official teaching certificate. You can upload this to the platform whenever you are ready to claim your Time Credits based on current market demand."

    try:
        # Send via Resend
        response = resend.Emails.send({
            "from": sender_email,
            "to": teacher_email,
            "subject": subject,
            "html": html_content,
            "text": plain_text,
            "attachments": [
                {
                    "filename": "SkillSwap_Certificate.pdf",
                    "content": pdf_bytes,  # bytes, Resend will base64 encode
                }
            ]
        })
        print(f"✅ Email sent successfully! Resend ID: {response['id']}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")