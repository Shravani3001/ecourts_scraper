# 🏛️ eCourts Cause List & Case Details Scraper

A **Python + Flask web application + CLI tool** that fetches **real-time court cause lists** and **case details by CNR number** from the official [eCourts portal](https://services.ecourts.gov.in/ecourtindia_v6/).

It offers both:

* 🌐 **Web Interface (Flask UI)** — for simple, interactive use
* 💻 **Command-Line Interface (CLI)** — for quick automation and daily use

---

## 🚀 Features

### 🔹 1. Cause List Downloader

* Enter **State, District, Court Complex, Court Name (optional)**, and **Case Type (Civil/Criminal)**.
* Fetches cause list PDF(s) for the entered date (or auto for today/tomorrow via CLI).
* Saves results automatically to the `/data` folder.
* Displays clear status messages:
  ✅ *Downloaded successfully*
  ⚠️ *No PDFs found or CAPTCHA required*

---

### 🔹 2. Case Details by CNR

* Input **CNR number** (e.g., `TSHY010012342022`).
* Displays:

  * Court name & judge
  * Case type, filing number & date
  * Next hearing date (today / tomorrow / upcoming)
* Automatically creates:

  * `data/cnr_<cnr_number>.json`
  * `data/cnr_<cnr_number>.pdf`

---

### 🔹 3. Dual Interface Options

✅ **Web Interface (Flask UI)**
Simple forms for:

* 🏛️ Cause List Fetching
* 🔍 Case Details Lookup

✅ **Command-Line Interface (CLI)**
For fast, headless use — directly from your terminal.

---

## 🧠 Tech Stack

| Component       | Technology Used             |
| --------------- | --------------------------- |
| Backend         | Python 3, Flask             |
| Web Scraping    | `requests`, `BeautifulSoup` |
| File Generation | `json`, `fpdf`              |
| Frontend        | HTML5, CSS3, Jinja2         |
| CLI             | Python `argparse`           |
| Output Format   | PDF & JSON                  |

---

## 🗂️ Folder Structure

```
ecourts_scraper/
│
├── app.py                     # Flask web app
├── ecourt_scraper.py          # Core logic + CLI handler
├── data/                      # Auto-generated PDFs & JSONs
├── templates/
│   ├── index.html             # Home page (UI)
│   ├── cause_result.html      # Cause list result page
│   └── cnr_result.html        # CNR result page
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Shravani3001/ecourts_scraper.git
cd ecourts-scraper
```

### 2️⃣ Install Dependencies

Make sure Python ≥ 3.8 is installed.

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Web App

```bash
python app.py
```

Then open in your browser:

```
http://127.0.0.1:5000
```

---

## 💻 CLI Usage (Optional but Powerful)

The same project also supports **Command Line Interface** for quick fetching.

### ▶️ Run interactively

```bash
python ecourt_scraper.py
```

Prompts you for all inputs including date.

### ▶️ Auto-fetch today’s cause list

```bash
python ecourt_scraper.py --today
```

### ▶️ Auto-fetch tomorrow’s cause list

```bash
python ecourt_scraper.py --tomorrow
```

### ▶️ Fetch case details by CNR number

```bash
python ecourt_scraper.py --cnr TSJN000008342022
```

### ✅ Example Output

```
📅 Fetching cause list for 20-10-2025...
⚠️ No cause list found on eCourts site (or site blocked access).
🗂️ Results saved to data/result_Telangana_Jangoan_ALL_Civil_20_10_2025_20251020_224513.json
✅ Done! Result saved successfully.
```

CLI mode is **optional** — the UI and CLI share the same scraping logic, data storage, and PDF/JSON generation system.

---

## 🧾 Output Samples

### ✅ Cause List JSON

```json
{
  "state": "Telangana",
  "district": "Jangoan",
  "court_complex": "Jangoan, PDJ Court Complex",
  "court_name": "ALL",
  "case_type": "Civil",
  "date": "23-10-2025",
  "downloaded_pdfs": [],
  "status": "No PDFs found"
}
```

### ✅ Case Details JSON

```json
{
  "Next Hearing Date": "25-10-2025",
  "Court Name": "PRL. DISTRICT & SESSIONS JUDGE, JANGOAN",
  "Filing Number": "102/2022",
  "Case Type": "Criminal",
  "Judge Name": "Hon. Justice R. Krishna"
}
```
<img width="942" height="477" alt="Cause_list" src="https://github.com/user-attachments/assets/28da03dc-0388-472e-9bd7-a993643c6ece" />

---

<img width="820" height="509" alt="Case_details" src="https://github.com/user-attachments/assets/ae828b32-4d5e-4f5e-bcbf-add0ec522b19" />

---

<img width="844" height="465" alt="Cause_list_result" src="https://github.com/user-attachments/assets/9e388588-9435-40f4-863c-82bf6a7797b2" />

---

## ⚠️ Notes & Limitations

* eCourts website uses **CAPTCHA**, so automated access may sometimes be blocked.
* The app detects this and alerts the user:

  > ⚠️ Unable to fetch details — CAPTCHA verification required.
* Cause list availability and format differ by state.
* Project is for **educational and research purposes only**.

---

## About Me

**Shravani K**
I'm Shravani, a self-taught and project-driven DevOps engineer passionate about building scalable infrastructure and automating complex workflows.

I love solving real-world problems with tools like Terraform, Ansible, Docker, Jenkins, and AWS — and I’m always learning something new to sharpen my edge in DevOps.

Connect with me:

🌐 GitHub: [Shravani3001](https://github.com/Shravani3001)

💼 LinkedIn: [shravani3001](https://www.linkedin.com/in/shravani3001)


---

