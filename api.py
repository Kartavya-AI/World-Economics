from flask import Flask, request, jsonify
import warnings
import os
from datetime import datetime
from src.world_economics.crew import WorldEconomicsCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = Flask(__name__)

@app.route("/run-analysis", methods=["POST"])
def run_analysis():
    data = request.get_json() or {}

    inputs = {
        "user_query": data.get("question", "What is the impact of rising US interest rates on emerging economies in the global south?"),
        "current_year": str(datetime.now().year)
    }

    try:
        WorldEconomicsCrew().crew().kickoff(inputs=inputs)

        output_file = "final_report.md"
        if not os.path.exists(output_file):
            return jsonify({"status": "error", "message": f"Expected output '{output_file}' not found"}), 500

        with open(output_file, "r", encoding="utf-8") as f:
            report = f.read()

        return jsonify({"status": "success", "report": report}), 200

    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
