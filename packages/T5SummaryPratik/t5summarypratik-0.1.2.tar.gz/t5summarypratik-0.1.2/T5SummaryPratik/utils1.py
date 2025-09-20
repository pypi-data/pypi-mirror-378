import json
from T5SummaryPratik.pipeline1 import MedicalSummarizationPipeline

import json
def setx1(json_data):
    """
    Dynamically extract the last 'extracted_content' from any JSON structure.
    """
    with open(json_data, "r", encoding="utf-8") as f:
        data = json.load(f)

    extracted_content_values = []
    def recursive_find(obj, key, results):
        """Recursively search for all values of a key in nested JSON."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == key:
                    results.append(v)
                recursive_find(v, key, results)
        elif isinstance(obj, list):
            for item in obj:
                recursive_find(item, key, results)

    recursive_find(data, 'extracted_content', extracted_content_values)

    if extracted_content_values:
        # Return the last extracted_content value
        return extracted_content_values[-1]
    else:
        return "" 

# Factory function for the enhanced pipeline
def create_medical_pipeline():
    """Factory function to create medical pipeline instance"""
    return MedicalSummarizationPipeline()

def quick_medical_summarize(text, summary_type="medical_comprehensive", length="large"):
    """Quick medical summarization without evaluation"""
    pipeline = create_medical_pipeline()
    result = pipeline.medical_summarize_and_evaluate(text, summary_type=summary_type, length=length)
    return result['summary']

ls = []

def get1(file_path):
    # Create medical pipeline instead of travel pipeline
    pipeline = create_medical_pipeline()

    sample_text = setx1(file_path)
    reference = sample_text

    # Medical-specific summary styles
    medical_styles = ["medical_comprehensive", "doctor_search", "appointment_booking", "hospital_search"]
    metrices = []

    for style in medical_styles:
        result = pipeline.medical_summarize_and_evaluate(
            sample_text,
            reference_summary=reference,
            summary_type=style,
            length="comprehensive"  # Use comprehensive for medical content
        )
        ls.append(result["summary"])
        metrices.append(result['evaluation'])

    # Use enhanced comparison for medical summaries
    summaries_to_compare = {
        "Comprehensive Medical": ls[0],
        "Doctor Search Focused": ls[1],
        "Appointment Booking Focused": ls[2],
        "Hospital Search Focused": ls[3]
    }

    pipeline.compare_medical_summaries(summaries_to_compare, metrices, "medical_summaries.json")