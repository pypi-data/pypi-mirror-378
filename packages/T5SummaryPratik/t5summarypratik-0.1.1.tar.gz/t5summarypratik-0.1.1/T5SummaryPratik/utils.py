import json
from T5SummaryPratik.pipeline import CompleteSummarizationPipeline

import json
def setx(json_data):
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
        return "" # Return empty string if no extracted_content found

# Factory function for the enhanced pipeline
def create_travel_pipeline():
    """Factory function to create travel pipeline instance"""
    return CompleteSummarizationPipeline()

def quick_travel_summarize(text, summary_type="travel_comprehensive", length="large"):
    """Quick travel summarization without evaluation"""
    pipeline = create_travel_pipeline()
    result = pipeline.travel_summarize_and_evaluate(text, summary_type=summary_type, length=length)
    return result['summary']
ls=[]
def get(file_path):
    # Replace this line:
    # pipeline = create_pipeline()

    # With this:
    pipeline = create_travel_pipeline()

    sample_text = setx(file_path)
    reference = sample_text

    # Replace travel_summarize_and_evaluate calls:
    travel_styles = ["travel_comprehensive", "travel_itinerary", "travel_budget", "travel_activities"]
    metrices = []

    for style in travel_styles:
        result = pipeline.travel_summarize_and_evaluate(  # Changed method name
            sample_text,
            reference_summary=reference,
            summary_type=style,  # Changed parameter name
            length="comprehensive"  # Use comprehensive for travel content
        )
        ls.append(result["summary"])
        metrices.append(result['evaluation'])

    # Use enhanced comparison
    summaries_to_compare = {
        "Comprehensive": ls[0],
        "Itinerary-Focused": ls[1],
        "Budget-Focused": ls[2],
        "Activities-Focused": ls[3]
    }

    pipeline.compare_travel_summaries(summaries_to_compare, metrices, file_path)
