import logging
from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import get_all_keys, get_nested_value, calculate_fuzzy_score


class CompanyLists(Benchmark):

    def score_benchmark(self, all_scores):
        """
        Calculate macro and micro F1 scores across all test instances.

        Micro F1: Aggregate TP/FP/FN across all instances, then calculate F1
        Macro F1: Calculate F1 for each instance, then average the F1 scores
        """
        if not all_scores:
            return {"f1_micro": 0.0, "f1_macro": 0.0}

        # For micro F1: sum all TP, FP, FN across instances
        total_tp = 0
        total_fp = 0
        total_fn = 0

        # For macro F1: collect individual F1 scores
        f1_scores = []

        for score_data in all_scores:
            if isinstance(score_data, dict) and 'f1_score' in score_data:
                # Add to totals for micro F1
                total_tp += score_data.get('true_positives', 0)
                total_fp += score_data.get('false_positives', 0)
                total_fn += score_data.get('false_negatives', 0)

                # Collect individual F1 for macro F1
                f1_scores.append(score_data['f1_score'])

        # Calculate micro F1
        micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1_micro = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0

        # Calculate macro F1 (average of individual F1 scores)
        f1_macro = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

        score = {
            "f1_micro": f1_micro,
            "f1_macro": f1_macro,
            "micro_precision": micro_precision,
            "micro_recall": micro_recall,
            "total_instances": len(f1_scores),
            "total_tp": total_tp,
            "total_fp": total_fp,
            "total_fn": total_fn
        }

        logging.info(f"f1_micro: {f1_micro}, f1_macro: {f1_macro}")

        return score

    def score_request_answer(self, image_name, response, ground_truth):
        """
        Score the response against ground truth using F1 score based on field-level comparison.
        Each field is treated as a separate entity for TP/FP/FN calculation.
        """
        data = self.prepare_scoring_data(response)

        # Check if data is a list (array) but ground_truth has entries
        if isinstance(data, list) and "entries" in ground_truth:
            # Create entries wrapper to match ground truth structure
            data = {"entries": data}

        logging.info(image_name)
        logging.debug(f"response: {data}")
        logging.debug(f"ground_truth: {ground_truth}")

        # Get all terminal fields from both response and ground truth
        response_keys = get_all_keys(data)
        gt_keys = get_all_keys(ground_truth)

        # Calculate TP, FP, FN for each field
        tp = 0  # True positives - fields that match between response and ground truth
        fp = 0  # False positives - fields in response but not matching in ground truth
        fn = 0  # False negatives - fields in ground truth but not matching in response

        # Track field-level scores for debugging
        field_scores = {}

        # Get all unique keys from both datasets
        all_keys = set(response_keys + gt_keys)

        # Filter out metadata fields
        filtered_keys_temp = []
        for key in all_keys:
            if key.startswith("metadata"):
                continue
            filtered_keys_temp.append(key)

        # Filter out parent keys when child keys exist
        filtered_keys = []
        for key in filtered_keys_temp:
            # Check if this key has any children in the key set
            has_children = any(other_key.startswith(key + '.') for other_key in filtered_keys_temp if other_key != key)
            if not has_children:
                filtered_keys.append(key)

        for key in filtered_keys:
            response_value = get_nested_value(data, key)
            gt_value = get_nested_value(ground_truth, key)

            # Normalize None and "null" to empty string for consistent comparison
            if response_value is None or response_value == "null":
                response_value = ""
            if gt_value is None or gt_value == "null":
                gt_value = ""

            # Calculate fuzzy match score for this field
            field_score = calculate_fuzzy_score(response_value, gt_value)
            field_scores[key] = {
                'response': response_value,
                'ground_truth': gt_value,
                'score': field_score
            }

            # Threshold for considering a match (can be adjusted)
            match_threshold = 0.92

            if response_value != "" and gt_value != "":
                if field_score >= match_threshold:
                    tp += 1
                else:
                    # Both have values but don't match well enough
                    fp += 1
                    fn += 1
            elif response_value != "" and gt_value == "":
                fp += 1  # Response has value but ground truth doesn't
            elif response_value == "" and gt_value != "":
                fn += 1  # Ground truth has value but response doesn't
            # If both are empty, it's neither TP, FP, nor FN

        # Calculate precision, recall, and F1
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        score = {
            'f1_score': round(f1, 2),
            'precision': precision,
            'recall': recall,
            'true_positives': tp,
            'false_positives': fp,
            'false_negatives': fn,
            'field_scores': field_scores,
            'total_fields': len(all_keys)
        }

        logging.info(score['f1_score'])
        for line in score['field_scores'].values():
            logging.debug(line)

        return score

    def create_request_render(self, image_name, result, score, truth):
        """
        Create a markdown visualization of benchmark results for a company list page.

        This method generates a detailed markdown report that includes:
        - Overall F1 score, precision, and recall metrics
        - A link to view the raw JSON result
        - The original page image displayed
        - A table showing individual field comparisons with scores

        Args:
            image_name (str): Name of the image being processed.
            result (dict): The model's full JSON response.
            score (dict): Dictionary with F1, precision, recall and field scores for this image.
            truth (dict): The ground truth data for comparison.

        Returns:
            str: Markdown-formatted string containing the complete benchmark report.
        """

        # Add result header and overall scores at the top
        render = f"### Result for {image_name}\n"
        render += f"**F1 Score:** {score['f1_score']:.2f} (higher is better)<br>"
        render += f"**Precision:** {score['precision']:.3f}<br>"
        render += f"**Recall:** {score['recall']:.3f}<br>"
        render += f"**True Positives:** {score['true_positives']}<br>"
        render += f"**False Positives:** {score['false_positives']}<br>"
        render += f"**False Negatives:** {score['false_negatives']}<br>"

        # Calculate filtered field count for display
        field_scores = score.get('field_scores', {})
        filtered_field_count = sum(1 for key in field_scores.keys()
                                 if not key.startswith('metadata'))
        render += f"**Total Fields:** {filtered_field_count}<br>"

        # Add link to raw result JSON file with model name
        request_name = f"request_{self.id}_{image_name}"
        render += f"[View raw result from {self.model}](https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/results/{self.date}/{self.id}/{request_name}.json)\n\n"

        # Add the image - using GitHub raw URL format for proper display
        render += f"<img src=\"https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/benchmarks/{self.name}/images/{image_name}.jpg?raw=true\" alt=\"{image_name}\" width=\"600px\">\n\n"

        # Create markdown table with field-level comparisons
        render += "| Field | Model Response | Ground Truth | Fuzzy Score | Match |\n"
        render += "|-------|----------------|--------------|-------------|-------|\n"

        # Sort fields by key name for consistent ordering
        field_scores = score.get('field_scores', {})

        # Filter out metadata fields from rendering
        filtered_field_scores = {}
        for field_key, field_data in field_scores.items():
            if field_key.startswith('metadata'):
                continue
            filtered_field_scores[field_key] = field_data

        sorted_fields = sorted(filtered_field_scores.items())

        for field_key, field_data in sorted_fields:
            response_value = field_data.get('response', '')
            ground_truth_value = field_data.get('ground_truth', '')
            field_score = field_data.get('score', 0.0)

            # Display empty strings as "(empty)" for clarity
            if response_value == "":
                response_value = "(empty)"
            if ground_truth_value == "":
                ground_truth_value = "(empty)"

            # Escape markdown special characters and handle line breaks
            response_str = str(response_value).replace('|', '\\|').replace('\n', '<br>')
            ground_truth_str = str(ground_truth_value).replace('|', '\\|').replace('\n', '<br>')

            # Determine match status
            match_threshold = 0.92
            match_status = "✅" if field_score >= match_threshold else "❌"

            render += f"| {field_key} | {response_str} | {ground_truth_str} | {field_score:.3f} | {match_status} |\n"

        return render