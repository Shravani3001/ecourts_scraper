import requests
from bs4 import BeautifulSoup
import datetime
import os
import json
from fpdf import FPDF

# -------------------------
# Utility helpers
# -------------------------
def make_folder():
    os.makedirs("data", exist_ok=True)

def download_pdf(url, filename):
    """Download and save a PDF."""
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/pdf"):
            with open(filename, "wb") as f:
                f.write(r.content)
            print(f"✅ Downloaded: {filename}")
            return filename
        else:
            print(f"⚠️ No valid PDF at {url} (Status: {r.status_code})")
    except Exception as e:
        print(f"⚠️ Error downloading {url}: {e}")
    return None

# -------------------------
# Cause list fetching
# -------------------------
def fetch_ecourts_cause_lists(state, district, complex_name, court_name, case_type, date):
    """
    Fetch cause lists from the eCourts site.
    If court_name is None, download all available PDFs in that complex.
    NOTE: many eCourts endpoints require CAPTCHA; this function attempts
    to read PDF links from the target page but may return no PDFs if blocked.
    """
    base_url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"
    print(f"\n📥 Fetching {case_type} cause list for {complex_name} ({'ALL Courts' if not court_name else court_name}) on {date}...")

    try:
        session = requests.Session()
        response = session.get(base_url, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"⚠️ Could not access eCourts site: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)

    pdf_links = []
    for link in links:
        text = link.text.strip().lower()
        href = link["href"]

        # Heuristic: collect links that likely point to cause-list PDFs
        # Keep this simple — site may block or not expose direct PDF links.
        if "cause" in text and href.lower().endswith(".pdf"):
            full_url = href if href.startswith("http") else "https://services.ecourts.gov.in/" + href.lstrip("/")
            pdf_links.append(full_url)

    if not pdf_links:
        print("⚠️ No cause list found on eCourts site for the given inputs (or site blocked access).")
        return []

    downloaded = []
    make_folder()
    for i, pdf_url in enumerate(pdf_links, 1):
        safe_court = court_name if court_name else "ALL"
        safe_complex = complex_name.replace(' ', '_')[:40]
        safe_district = district.replace(' ', '_')[:30]
        filename = f"data/{safe_district}_{safe_complex}_{safe_court}_{case_type}_{i}_{date}.pdf"
        pdf = download_pdf(pdf_url, filename)
        if pdf:
            downloaded.append(pdf)

    return downloaded

# -------------------------
# Result file generation (single canonical function)
# -------------------------
def generate_result_file(state, district, complex_name, court_name, case_type, date_input, pdfs):
    """Save summary JSON after each UI request. Uses timestamp to avoid accidental overwrites."""
    result = {
        "state": state,
        "district": district,
        "court_complex": complex_name,
        "court_name": court_name if court_name else "ALL",
        "case_type": case_type,
        "date": date_input,
        "downloaded_pdfs": pdfs,
        "status": "Success" if pdfs else "No PDFs found"
    }

    # create unique filename per request (timestamp)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_complex = (complex_name.replace(' ', '_')[:20]) if complex_name else "COMPLEX"
    safe_court = (court_name.replace(' ', '_') if court_name else 'ALL')
    safe_district = (district.replace(' ', '_') if district else 'DIST')
    json_path = f"data/result_{safe_district}_{safe_complex}_{safe_court}_{date_input.replace('-', '_')}_{timestamp}.json"

    make_folder()
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"\n🗂️ Results saved to {json_path}")
    return json_path

# -------------------------
# CLI main for manual runs (kept optional)
# -------------------------
def main():
    print("=== 🏛️ eCourts Cause List Downloader ===")
    state = input("Enter State Name: ").strip()
    district = input("Enter District Name: ").strip()
    complex_name = input("Enter Court Complex Name: ").strip()
    court_name = input("Enter Court Name (press Enter to download all courts): ").strip()
    case_type = input("Enter Case Type (Civil or Criminal): ").strip().capitalize()
    date_input = input("Enter Date (DD-MM-YYYY): ").strip()

    try:
        datetime.datetime.strptime(date_input, "%d-%m-%Y")
    except ValueError:
        print("⚠️ Invalid date format. Use DD-MM-YYYY.")
        return

    if case_type not in ["Civil", "Criminal"]:
        print("⚠️ Invalid Case Type. Please enter either 'Civil' or 'Criminal'.")
        return

    make_folder()

    print("\n🔗 Connecting to eCourts portal...")
    pdfs = fetch_ecourts_cause_lists(
        state, district, complex_name,
        court_name if court_name else None,
        case_type, date_input
    )

    # save results (this will create a timestamped json file)
    json_path = generate_result_file(state, district, complex_name, court_name, case_type, date_input, pdfs)
    print("✅ Process completed successfully.")
    print(f"Result JSON: {json_path}")

# -------------------------
# CNR lookup (separate, uses same data folder)
# -------------------------
def fetch_case_details_by_cnr(cnr_number):
    """
    Fetch complete case details using CNR number.
    Attempts to fetch real data from eCourts;
    gracefully handles CAPTCHA or missing data.
    """
    print(f"🔍 Fetching case details for CNR: {cnr_number}")
    url = f"https://services.ecourts.gov.in/ecourtindia_v6/cases/display_case_status.php?cnr={cnr_number}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 400:
            print("⚠️ CAPTCHA or invalid request — eCourts blocked automated access.")
            return {"error": "Unable to fetch details — CAPTCHA verification required.", "url": "https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index&app_token=e0d9490bd40051a40e68c4626754e0c1f29fc01ede3478003f35f239b8e1f794"}
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching details: {e}")
        return {"error": "Unable to fetch details — CAPTCHA verification required.", "url": "https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index&app_token=e0d9490bd40051a40e68c4626754e0c1f29fc01ede3478003f35f239b8e1f794"}

    soup = BeautifulSoup(r.text, "html.parser")

    # Parse case details
    details = {}
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) == 2:
            key = tds[0].text.strip().replace(":", "")
            value = tds[1].text.strip()
            details[key] = value

    if not details:
        print("⚠️ No details found — possibly invalid CNR.")
        return {"error": "No case details found", "url": url}

    # Extract key details and next hearing status
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    next_hearing = details.get("Next Hearing Date", "Not available")
    court = details.get("Court Name", "Not available")
    judge = details.get("Judge Name", "Not available")
    filing_no = details.get("Filing Number", "Not available")

    status_text = "Not listed today or tomorrow."
    if next_hearing and next_hearing not in ("Not available", ""):
        try:
            nh_date = datetime.datetime.strptime(next_hearing, "%d-%m-%Y").date()
            if nh_date == today:
                status_text = "📅 Case listed for today."
            elif nh_date == tomorrow:
                status_text = "📅 Case listed for tomorrow."
            else:
                status_text = f"📅 Next hearing on {next_hearing}."
        except:
            pass

    # Save as JSON (timestamped)
    make_folder()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = f"data/cnr_{cnr_number}_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(details, f, indent=4, ensure_ascii=False)

    # Save as simple text PDF
    pdf_path = f"data/cnr_{cnr_number}_{timestamp}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, f"CNR Number: {cnr_number}\n\n")
    for key, value in details.items():
        pdf.multi_cell(0, 8, f"{key}: {value}")
    pdf.output(pdf_path)

    print(f"✅ Case details saved: {json_path}, {pdf_path}")

    return {
        "cnr": cnr_number,
        "status_text": status_text,
        "details": details,
        "json_path": json_path,
        "pdf_path": pdf_path,
        "url": "https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index&app_token=e0d9490bd40051a40e68c4626754e0c1f29fc01ede3478003f35f239b8e1f794"
    }

import argparse

def cli_handler():
    """Command-line interface for bonus functionality."""
    parser = argparse.ArgumentParser(description="eCourts Cause List & Case Details Scraper")

    parser.add_argument("--today", action="store_true", help="Fetch today's cause list")
    parser.add_argument("--tomorrow", action="store_true", help="Fetch tomorrow's cause list")
    parser.add_argument("--cnr", type=str, help="Fetch case details by CNR number")

    args = parser.parse_args()

    if args.cnr:
        print(f"🔍 Fetching case details for CNR: {args.cnr}")
        result = fetch_case_details_by_cnr(args.cnr)
        print(json.dumps(result, indent=4, ensure_ascii=False))
        return

    if args.today or args.tomorrow:
        state = input("Enter State Name: ").strip()
        district = input("Enter District Name: ").strip()
        complex_name = input("Enter Court Complex Name: ").strip()
        court_name = input("Enter Court Name (press Enter for all courts): ").strip()
        case_type = input("Enter Case Type (Civil or Criminal): ").strip().capitalize()

        date = datetime.date.today()
        if args.tomorrow:
            date += datetime.timedelta(days=1)
        date_input = date.strftime("%d-%m-%Y")

        print(f"\n📅 Fetching cause list for {date_input}...")
        pdfs = fetch_ecourts_cause_lists(state, district, complex_name, court_name, case_type, date_input)
        result_path = generate_result_file(state, district, complex_name, court_name, case_type, date_input, pdfs)
        print(f"✅ Done! Result saved to {result_path}")
    else:
        main()  # fallback to interactive mode


# Run CLI handler when file executed directly
if __name__ == "__main__":
    cli_handler()
