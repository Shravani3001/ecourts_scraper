from flask import Flask, render_template, request, send_from_directory
import ecourt_scraper
import os

app = Flask(__name__)
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        state = request.form.get("state")
        district = request.form.get("district")
        complex_name = request.form.get("complex_name")
        court_name = request.form.get("court_name")
        case_type = request.form.get("case_type")
        date_input = request.form.get("date_input")

        pdfs = ecourt_scraper.fetch_ecourts_cause_lists(
            state, district, complex_name,
            court_name if court_name else None,
            case_type, date_input
        )

        result_file = ecourt_scraper.generate_result_file(
            state, district, complex_name, court_name, case_type, date_input, pdfs
        )

        # Prepare message
        if pdfs:
            message = f"✅ Downloaded {len(pdfs)} PDF(s)."
        else:
            message = "⚠️ No PDFs found or CAPTCHA required."

        # Instead of showing result on same page, redirect to new template
        return render_template("cause_result.html", message=message, result_file=result_file)

    return render_template("index.html")
    

@app.route("/download/<filename>")
def download_file(filename):
    """Serve JSON result files from /data folder."""
    directory = os.path.join(os.getcwd(), "data")
    return send_from_directory(directory, filename, as_attachment=True)

@app.route("/cnr-details", methods=["POST"])
def cnr_details():
    cnr = request.form.get("cnr")
    result = ecourt_scraper.fetch_case_details_by_cnr(cnr)

    if "error" in result:
        return render_template(
            "cnr_result.html",
            cnr=cnr,
            message=f"⚠️ {result['error']}",
            cnr_url=result.get("url", "#"),
            details=None
        )

    return render_template(
        "cnr_result.html",
        cnr=cnr,
        message=result["status_text"],
        cnr_url=result["url"],
        details=result["details"],
        json_file=result["json_path"],
        pdf_file=result["pdf_path"]
    )

if __name__ == "__main__":
    app.run(debug=False)