import logging

from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import calculate_fuzzy_score
import re
import os
from collections import defaultdict
import Levenshtein


class Fraktur(Benchmark):

    def calculate_cer(self, reference_text: str, hypothesis_text: str) -> float:
        """
        Calculate Character Error Rate (CER) between a reference text and a hypothesis text.
        
        CER is calculated as the Levenshtein distance (edit distance) divided by the number
        of characters in the reference text. Lower scores indicate better performance.
        
        Args:
            reference_text (str): The ground truth text
            hypothesis_text (str): The predicted text
            
        Returns:
            float: Character Error Rate, a value between 0.0 (perfect match) and potentially >1.0
                  (when hypothesis has more errors than reference characters)
        """
        if not reference_text:
            return 1.0  # Maximum error if reference is empty
            
        if not hypothesis_text:
            return 1.0  # Maximum error if hypothesis is empty
        
        # Normalize strings - lowercase and remove extra whitespace
        ref_normalized = ' '.join(reference_text.lower().split())
        hyp_normalized = ' '.join(hypothesis_text.lower().split())
        
        # If strings are identical after normalization
        if ref_normalized == hyp_normalized:
            return 0.0
            
        # Calculate Levenshtein distance (minimum number of single-character edits)
        edit_distance = Levenshtein.distance(ref_normalized, hyp_normalized)
        
        # Divide by the length of the reference text
        return min(1.0, edit_distance / max(1, len(ref_normalized)))

    def score_benchmark(self, all_scores: list) -> dict:
        """
        Calculate the overall benchmark score by averaging the fuzzy scores and CER of all evaluated documents.
        
        This method computes average scores across all processed images,
        providing metrics that represent the benchmark's overall performance.
        
        Args:
            all_scores (list): List of dictionaries containing individual scores for each document.
            
        Returns:
            dict: Dictionary with keys 'fuzzy' and 'cer' containing the averaged scores.
        """

        total_fuzzy = 0
        total_cer = 0
        
        for score in all_scores:
            total_fuzzy += score['fuzzy']
            total_cer += score['cer']

        # Ensure we don't divide by zero
        if len(all_scores) > 0:
            avg_fuzzy = total_fuzzy / len(all_scores)
            avg_cer = total_cer / len(all_scores)
        else:
            avg_fuzzy = 0.0
            avg_cer = 1.0

        return {
            "fuzzy": round(avg_fuzzy, 3),
            "cer": round(avg_cer, 3)
        }

    def score_request_answer(self,
                             image_name: str,
                             response: dict,
                             ground_truth: dict) -> dict:
        """
        Score an individual response by comparing extracted advertisements to ground truth.
        
        This method processes the model's response, compares the extracted advertisements 
        with the ground truth data, and calculates both fuzzy similarity scores and 
        character error rates (CER) for each advertisement.
        The final scores are averages of all individual scores.
        
        Args:
            image_name (str): Name of the image being processed.
            response (dict): The model's full response containing extracted advertisements.
            ground_truth (dict): The ground truth data for comparison, containing expected advertisements.
            
        Returns:
            dict: Dictionary with 'fuzzy' and 'cer' keys containing the rounded average scores.
                 Note that for CER, lower scores are better (0.0 is perfect).
        """

        data = self.prepare_scoring_data(response)
        results = self.compare_ads(response=data,
                                   ground_truth=ground_truth)

        # Calculate scores
        total_fuzzy = 0
        total_cer = 0
        
        for result in results:
            total_fuzzy += result["similarity"]
            
            # Calculate CER if we have both texts
            if result["match_found"]:
                # Use the text from the ground truth and the response for CER calculation
                gt_text = result["ground_truth_text"]
                resp_text = result["response_text"]
                
                # Calculate and store the CER
                cer = self.calculate_cer(gt_text, resp_text)
                result["cer"] = round(cer, 3)
                total_cer += cer
            else:
                # Missing advertisement is maximum error
                result["cer"] = 1.0
                total_cer += 1.0
        
        # Ensure we don't divide by zero
        if len(results) > 0:
            avg_fuzzy = total_fuzzy / len(results)
            avg_cer = total_cer / len(results)
        else:
            avg_fuzzy = 0.0
            avg_cer = 1.0

        return {
            "fuzzy": round(avg_fuzzy, 2),
            "cer": round(avg_cer, 3)  # Use 3 decimal places for CER for more precision
        }

    def extract_number_prefix(self,
                              text: str) -> int | None:
        """
        Extract the leading number prefix (e.g., '1.') from advertisement text.
        
        This method identifies the numbered list format commonly used in historical
        classified advertisements by extracting the leading ordinal number.
        
        Args:
            text (str): The advertisement text to analyze.
            
        Returns:
            int or None: The extracted number as an integer if found, None otherwise.
        """

        match = re.match(r"^\s*(\d+)\.", text)

        return int(match.group(1)) if match else None

    def group_by_section_and_number(self,
                                    ad_list: list) -> dict:
        """
        Group advertisements by their section titles and leading number prefixes.
        
        This method organizes advertisements into a nested dictionary structure,
        first by section title (e.g., "Es werden zum Verkauff offerirt") and then
        by their numerical prefix (e.g., "1.", "2.", etc.). This organization
        facilitates matching between model responses and ground truth data.
        
        Args:
            ad_list (list): List of advertisement dictionaries to be grouped.
            
        Returns:
            dict: A nested dictionary with structure {section_title: {number: advertisement_dict}}
                 where section_title is the advertisement section heading,
                 number is the integer prefix of the advertisement,
                 and advertisement_dict is the full advertisement object.
        """

        grouped = defaultdict(dict)
        for ad in ad_list:
            if not isinstance(ad, dict):
                continue  # skip malformed entries
            try:
                section = ad.get("tags_section", "").strip()
                number = self.extract_number_prefix(ad.get("text", ""))
                if section and number:
                    grouped[section][number] = ad
            except AttributeError:
                return {}
        return grouped

    def compare_ads(self,
                    response: dict,
                    ground_truth: dict | list):
        """
        Compare advertisements between response and ground truth.
        
        This method matches advertisements from the model's response to the ground truth data
        by section and number prefix, then calculates text similarity scores using fuzzy matching.
        It uses a 95% similarity threshold for matching section names when exact matches aren't found.
        
        Args:
            response (dict): The model's parsed response containing extracted advertisements.
            ground_truth (dict): The ground truth data containing expected advertisements.
            
        Returns:
            list: List of dictionaries containing comparison results for each advertisement, including:
                - section: Section name from ground truth
                - number: Advertisement number
                - match_found: Boolean indicating if a matching advertisement was found
                - similarity: Fuzzy similarity score (0.0-1.0)
                - response_text: Text from model's response (or None if no match)
                - ground_truth_text: Text from ground truth
        """

        # Fuzzy matching threshold (95%)
        SECTION_MATCH_THRESHOLD = 0.95

        # Flatten ground_truth values (list of list of dicts) into single list
        if type(ground_truth) is dict:
            ground_truth_flat = [entry for ads in ground_truth.values() for entry in ads]
        else:
            ground_truth_flat = ground_truth

        # Group response and ground_truth data
        try:
            response_grouped = self.group_by_section_and_number(response["advertisements"])
        except KeyError:
            response_grouped = {}

        ground_truth_grouped = self.group_by_section_and_number(ground_truth_flat)

        # Compare ads per section
        results = []
        for section, gt_ads in ground_truth_grouped.items():
            # First try exact match
            response_ads = response_grouped.get(section, {})
            
            # If no exact match, try fuzzy matching
            if not response_ads:
                for resp_section, resp_ads in response_grouped.items():
                    similarity = calculate_fuzzy_score(test_value=resp_section, gold_value=section)
                    if similarity >= SECTION_MATCH_THRESHOLD:
                        response_ads = resp_ads
                        break

            for number, gt_ad in gt_ads.items():
                response_ad = response_ads.get(number)
                if response_ad:
                    similarity = calculate_fuzzy_score(test_value=response_ad["text"], gold_value=gt_ad["text"])
                    results.append({
                        "section": section,
                        "number": number,
                        "match_found": True,
                        "similarity": round(similarity, 3),
                        "response_text": response_ad["text"],
                        "ground_truth_text": gt_ad["text"]
                    })
                else:
                    results.append({
                        "section": section,
                        "number": number,
                        "match_found": False,
                        "similarity": 0.0,
                        "response_text": None,
                        "ground_truth_text": gt_ad["text"]
                    })
        return results

    def create_request_render(self,
                              image_name: str,
                              result: dict,
                              score: dict,
                              truth: dict) -> str:
        """
        Create a markdown render of the request results for visualization.
        
        This method generates a detailed markdown report comparing the model's extracted
        advertisements with the ground truth, including similarity scores and character
        error rates (CER) for each item. The differences between prediction and ground truth
        are highlighted with light red underlines.
        
        Args:
            image_name (str): Name of the image being processed.
            result (dict): The model's full response.
            score (dict): The calculated scores for this response.
            truth (dict): The ground truth data for comparison.
            
        Returns:
            str: Markdown-formatted string containing the comparison report with highlighted differences.
        """
        data = self.prepare_scoring_data(result)
        results = self.compare_ads(response=data, ground_truth=truth)
        
        # Ensure CER scores are calculated for all results
        for item in results:
            if "cer" not in item and item["match_found"]:
                # Use normalized text for consistency with score_request_answer
                gt_text = item["ground_truth_text"]
                resp_text = item["response_text"]
                item["cer"] = round(self.calculate_cer(gt_text, resp_text), 3)
            elif "cer" not in item:
                item["cer"] = 1.0
        
        # Add result header and overall scores at the top
        render = f"### Result for {image_name}\n"
        render += f"**Average fuzzy score:** {score['fuzzy']:.3f} (higher is better)<br>"
        render += f"**Average character error rate (CER):** {score['cer']:.3f} (lower is better)<br>"
        
        # Add link to raw result JSON file with model name
        request_name = f"request_{self.id}_{image_name}"
        render += f"[View raw result from {self.model}](https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/results/{self.date}/{self.id}/{request_name}.json)\n\n"

        # Add the image before the table - using relative path from renders to images directory
        image_ext = None
        for ext in ['.jpg', '.jpeg', '.png']:
            if os.path.exists(os.path.join(self.benchmark_dir, "images", f"{image_name}{ext}")):
                image_ext = ext
                break

        if image_ext:
            # Use GitHub raw URL format to ensure images display correctly on GitHub Pages
            render += f"<img src=\"https://github.com/RISE-UNIBAS/humanities_data_benchmark/blob/main/benchmarks/{self.name}/images/{image_name}{image_ext}?raw=true\" alt=\"{image_name}\" width=\"800px\">\n\n"

        # Add CSS style for highlighting differences
        render += "<style>\n"
        render += ".diff { text-decoration: underline; text-decoration-color: #ffcccc; text-decoration-style: wavy; }\n"
        render += "</style>\n\n"
        
        # Create markdown table with 5 columns
        render += "| Section | Prediction | Ground Truth | Fuzzy Score | CER |\n"
        render += "|---------|------------|--------------|-------------|-----|\n"
        
        for item in results:
            section = item["section"]
            prediction_text = item["response_text"]
            ground_truth_text = item["ground_truth_text"]
            similarity = f"{item['similarity']:.3f}"
            cer = f"{item['cer']:.3f}"
            
            # Handle case where prediction is missing
            if prediction_text is None:
                prediction = "N/A"
                ground_truth = ground_truth_text.replace("\n", "<br>")
            else:
                # Highlight differences between prediction and ground truth
                prediction, ground_truth = self._highlight_differences(prediction_text, ground_truth_text)
            
            render += f"| {section} | {prediction} | {ground_truth} | {similarity} | {cer} |\n"
        
        return render
        
    def _highlight_differences(self, prediction_text: str, ground_truth_text: str) -> tuple:
        """
        Highlight differences between prediction and ground truth texts.
        
        This method compares the two texts character by character and wraps
        differing segments in HTML spans with a light red underline style.
        
        Args:
            prediction_text (str): The text predicted by the model
            ground_truth_text (str): The ground truth text
            
        Returns:
            tuple: (formatted_prediction, formatted_ground_truth) with differences highlighted
        """
        from difflib import SequenceMatcher
        
        # Compare sequences
        matcher = SequenceMatcher(None, prediction_text, ground_truth_text)
        
        # Build formatted strings with highlighted differences
        pred_formatted = ""
        truth_formatted = ""
        
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == 'equal':
                # Identical text
                pred_part = prediction_text[i1:i2]
                truth_part = ground_truth_text[j1:j2]
                pred_formatted += pred_part
                truth_formatted += truth_part
            elif op == 'replace':
                # Different text
                pred_part = prediction_text[i1:i2]
                truth_part = ground_truth_text[j1:j2]
                pred_formatted += f'<span class="diff">{pred_part}</span>'
                truth_formatted += f'<span class="diff">{truth_part}</span>'
            elif op == 'delete':
                # Text in prediction but not in ground truth
                pred_part = prediction_text[i1:i2]
                pred_formatted += f'<span class="diff">{pred_part}</span>'
            elif op == 'insert':
                # Text in ground truth but not in prediction
                truth_part = ground_truth_text[j1:j2]
                truth_formatted += f'<span class="diff">{truth_part}</span>'
        
        # Replace newlines for markdown table compatibility
        pred_formatted = pred_formatted.replace("\n", "<br>")
        truth_formatted = truth_formatted.replace("\n", "<br>")
        
        return pred_formatted, truth_formatted
