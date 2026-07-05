import asyncio
from app.services.pdf_parser import extract_resume, parse_resume_with_ai

# Test with fake resume text directly
fake_text = "Aryan Pathak\naryan@example.com\n+91 9876543210\n3 years experience as Product Manager\nSkills: agile, jira, product roadmap"
fake_skills = ["agile", "jira"]

class FakeBase:
    full_name = "Aryan Pathak"
    email = "aryan@example.com"
    phone = "+91 9876543210"
    years_exp = 3

async def test():
    try:
        result = await parse_resume_with_ai(fake_text, fake_skills, FakeBase())
        print("SUCCESS:", result)
    except Exception as e:
        import traceback
        print("ERROR:", type(e).__name__, str(e))
        traceback.print_exc()

asyncio.run(test())
