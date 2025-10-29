import logging
from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score


class CompanyLists(Benchmark):

    def score_benchmark(self, all_scores):
        total_score = 0
        for score in all_scores:
            logging.debug(f"Fuzzy score: {score['fuzzy']}")
            total_score += score['fuzzy']

        return {"fuzzy": total_score / len(all_scores)}

    def score_request_answer(self, image_name, response, ground_truth):
        data = self.prepare_scoring_data(response)

        # Check if data is a list (array) but ground_truth has entries
        if isinstance(data, list) and "entries" in ground_truth:
            # Create entries wrapper to match ground truth structure
            data = {"entries": data}

        my_keys = get_all_keys(ground_truth)

        avg_score = 0
        total_keys = 0
        for k in my_keys:
            test_value = get_nested_value(data, k)
            gold_value = get_nested_value(ground_truth, k)

            # Skip metadata fields to focus on bibliographic entries
            if k.startswith("metadata"):
                continue

            # Normalize None and "null" to empty string for consistent comparison
            if test_value is None or test_value == "null":
                test_value = ""
            if gold_value is None or gold_value == "null":
                gold_value = ""

            score = calculate_fuzzy_score(test_value, gold_value)
            avg_score += score
            total_keys += 1

        if total_keys > 0:
            avg_score /= total_keys
        else:
            avg_score = 0

        return {"fuzzy": avg_score}

    def create_request_render(self, image_name, result, score, truth):
        """
        Create a markdown visualization of benchmark results for a company list page.

        This method generates a detailed markdown report that includes:
        - Overall fuzzy score metrics
        - A link to view the raw JSON result
        - The original page image displayed
        - A table showing individual field comparisons with scores

        Args:
            image_name (str): Name of the image being processed.
            result (dict): The model's full JSON response.
            score (dict): Dictionary with fuzzy score for this image.
            truth (dict): The ground truth data for comparison.

        Returns:
            str: Markdown-formatted string containing the complete benchmark report.
        """
        data = self.prepare_scoring_data(result)

        # Check if data is a list (array) but truth has entries
        if isinstance(data, list) and "entries" in truth:
            # Create entries wrapper to match ground truth structure
            data = {"entries": data}

        my_keys = get_all_keys(truth)
        avg_score = 0
        total_keys = 0

        # Collect field scores for table
        field_data = []

        for k in my_keys:
            # Skip metadata fields to focus on bibliographic entries
            if k.startswith("metadata"):
                continue

            test_value = get_nested_value(data, k)
            gold_value = get_nested_value(truth, k)

            # Normalize None and "null" to empty string for consistent comparison
            if test_value is None or test_value == "null":
                test_value = ""
            if gold_value is None or gold_value == "null":
                gold_value = ""

            item_score = calculate_fuzzy_score(test_value, gold_value)
            avg_score += item_score
            total_keys += 1

            field_data.append({
                'key': k,
                'test_value': test_value,
                'gold_value': gold_value,
                'score': item_score
            })

        if total_keys > 0:
            avg_score /= total_keys
        else:
            avg_score = 0

        # Build the render
        render = f"### Result for {image_name}\n"
        render += f"**Average Fuzzy Score:** {avg_score:.3f} (higher is better)<br>\n"
        render += f"**Total Fields:** {total_keys}<br>\n"

        # Add link to raw result JSON file with model name
        request_name = f"request_{self.id}_{image_name}"
        render += f"[View raw result from {self.model}](https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/results/{self.date}/{self.id}/{request_name}.json)\n\n"

        # Add the image - using GitHub raw URL format for proper display
        render += f"<img src=\"https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/benchmarks/{self.name}/images/{image_name}.jpg?raw=true\" alt=\"{image_name}\" width=\"600px\">\n\n"

        # Create markdown table with field-level comparisons
        render += "| Field | Model Response | Ground Truth | Fuzzy Score | Match |\n"
        render += "|-------|----------------|--------------|-------------|-------|\n"

        # Match threshold for visual indicator
        match_threshold = 0.92

        for field in field_data:
            # Get values (already normalized, None converted to "")
            response_value = field['test_value']
            ground_truth_value = field['gold_value']

            # Display empty strings as "(empty)" for clarity
            if response_value == "":
                response_value = "(empty)"
            if ground_truth_value == "":
                ground_truth_value = "(empty)"

            # Escape markdown special characters and handle line breaks
            response_str = str(response_value).replace('|', '\\|').replace('\n', '<br>')
            ground_truth_str = str(ground_truth_value).replace('|', '\\|').replace('\n', '<br>')

            # Determine match status
            match_status = "✅" if field['score'] >= match_threshold else "❌"

            render += f"| {field['key']} | {response_str} | {ground_truth_str} | {field['score']:.3f} | {match_status} |\n"

        return render