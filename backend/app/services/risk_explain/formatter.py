def format_explanation(explanation):
    return {
        "summary": explanation["overall_reasoning"],
        "details": explanation["by_layer"]
    }
