import os
import resend
import smtplib
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
    Emails the generated PDF to the teacher using completely free Gmail SMTP.
    """
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("⚠️ Dev Mode: GMAIL_SENDER or GMAIL_PASSWORD not set. Skipping email.")
        return

    # 1. Create the email message container
    msg = EmailMessage()
    msg['Subject'] = "Your SkillSwap Teaching Certificate is here!"
    msg['From'] = f"SkillSwap Team <{sender_email}>"
    msg['To'] = teacher_email
    
    # 2. Add the email body text
    msg.set_content(
        "Congratulations! Attached is your official teaching certificate.\n\n"
        "You can upload this to the platform whenever you are ready to claim "
        "your Time Credits based on current market demand.\n\n"
        "Best regards,\nSkillSwap Team"
    )

    # 3. Read and attach the PDF
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            
        msg.add_attachment(
            pdf_bytes, 
            maintype='application', 
            subtype='pdf', 
            filename='SkillSwap_Certificate.pdf'
        )
    except Exception as e:
        print(f"❌ Failed to read PDF attachment: {e}")
        return

    # 4. Log into Gmail and send!
    try:
        # Connect to Gmail's secure SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            
        print(f"✅ Email sent successfully to {teacher_email} via Gmail!")
    except Exception as e:
        print(f"❌ Failed to send email via Gmail: {e}")