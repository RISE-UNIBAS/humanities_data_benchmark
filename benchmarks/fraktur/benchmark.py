import logging
import re
import os
from collections import defaultdict

import Levenshtein
from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import calculate_fuzzy_score

# Constants
DEFAULT_SECTION = "Es wird zum Verkauf angetragen"
SECTION_MATCH_THRESHOLD = 0.95


class Fraktur(Benchmark):
    """
    Benchmark for Fraktur text extraction from historical documents.
    
    This benchmark evaluates a model's ability to accurately extract and transcribe
    structured advertisements from historical documents written in Fraktur script.
    It measures both fuzzy matching scores and character error rates (CER) between
    the model's predictions and ground truth data.
    """

    def calculate_cer(self, reference_text: str, hypothesis_text: str) -> float:
        """
        Calculate Character Error Rate (CER) between a reference text and a hypothesis text.
        
        CER is calculated as the Levenshtein distance (edit distance) divided by the number
        of characters in the reference text. Lower scores indicate better performance.
        
        Args:
            reference_text (str): The ground truth text.
            hypothesis_text (str): The predicted text.
            
        Returns:
            float: Character Error Rate, a value between 0.0 (perfect match) and potentially >1.0
                  (when hypothesis has more errors than reference characters).
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
        Calculate the overall benchmark score by averaging fuzzy scores and CER across documents.
        
        This method computes average scores across all processed images,
        providing metrics that represent the benchmark's overall performance
        on Fraktur text extraction.
        
        Args:
            all_scores (list): List of dictionaries containing individual scores for each document,
                              where each dictionary has 'fuzzy' and 'cer' keys.
            
        Returns:
            dict: Dictionary with keys 'fuzzy' (higher is better) and 'cer' (lower is better)
                 containing the averaged scores rounded to 3 decimal places.
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
        Score a model response by comparing extracted advertisements to ground truth.
        
        This method processes the model's response, compares the extracted advertisements 
        with the ground truth data, and calculates both fuzzy similarity scores and 
        character error rates (CER) for each advertisement. Special handling is applied
        for image_4 which requires default section assignment.
        
        Args:
            image_name (str): Name of the image being processed (e.g., "image_1", "image_4").
            response (dict): The model's full JSON response containing extracted advertisements.
            ground_truth (dict): The ground truth data for comparison, containing expected advertisements.
            
        Returns:
            dict: Dictionary with:
                - 'fuzzy': Average fuzzy similarity score (higher is better, max 1.0)
                - 'cer': Average character error rate (lower is better, min 0.0)
        """

        data = self.prepare_scoring_data(response)
        results = self.compare_ads(response=data,
                                   ground_truth=ground_truth,
                                   image_name=image_name)

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
        Extract the leading number prefix (e.g., '1.', '16.') from advertisement text.
        
        This method identifies the numbered list format commonly used in historical
        classified advertisements by extracting the leading ordinal number. It matches
        patterns like "16. Bey Hrn. Rudolf..." and extracts the number 16.
        
        Args:
            text (str): The advertisement text to analyze.
            
        Returns:
            int or None: The extracted number as an integer if found (e.g., 16), 
                        None if no number prefix is found.
        """

        match = re.match(r"^\s*(\d+)\.", text)

        return int(match.group(1)) if match else None

    def group_by_section_and_number(self,
                                    ad_list: list,
                                    image_name: str = None) -> dict:
        """
        Group advertisements by their section titles and leading number prefixes.
        
        This method organizes advertisements into a nested dictionary structure,
        first by section title (e.g., "Es werden zum Verkauff offerirt") and then
        by their numerical prefix (e.g., "1.", "2.", etc.). This organization
        facilitates matching between model responses and ground truth data.
        
        For image_4, uses a default section title if tags_section is empty or None.
        
        Args:
            ad_list (list): List of advertisement dictionaries to be grouped.
            image_name (str, optional): Name of the current image being processed.
            
        Returns:
            dict: A nested dictionary with structure {section_title: {number: advertisement_dict}}
                 where section_title is the advertisement section heading,
                 number is the integer prefix of the advertisement,
                 and advertisement_dict is the full advertisement object.
        """
        grouped = defaultdict(dict)

        # Handle empty or invalid ad_list
        if not ad_list or not isinstance(ad_list, list):
            return grouped

        for ad in ad_list:
            if not isinstance(ad, dict):
                continue  # skip malformed entries

            try:
                # Get section and strip whitespace
                section = ad.get("tags_section", "").strip()

                # Special handling for image_4
                if image_name == "image_4" and not section:
                    section = DEFAULT_SECTION
                    ad["tags_section"] = DEFAULT_SECTION

                # Extract number from text and add to grouped structure
                number = self.extract_number_prefix(ad.get("text", ""))
                if section and number:
                    grouped[section][number] = ad
            except (AttributeError, TypeError) as e:
                logging.warning(f"Error grouping advertisement: {e}")
                continue

        return grouped

    def compare_ads(self,
                    response: dict,
                    ground_truth: dict | list,
                    image_name: str = None):
        """
        Compare advertisements between response and ground truth.
        
        This method matches advertisements from the model's response to the ground truth data
        by section and number prefix, then calculates text similarity scores using fuzzy matching.
        It uses a 95% similarity threshold for matching section names when exact matches aren't found.
        
        Args:
            response (dict): The model's parsed response containing extracted advertisements.
            ground_truth (dict): The ground truth data containing expected advertisements.
            image_name (str, optional): Name of the current image being processed.
            
        Returns:
            list: List of dictionaries containing comparison results for each advertisement, including:
                - section: Section name from ground truth
                - number: Advertisement number
                - match_found: Boolean indicating if a matching advertisement was found
                - similarity: Fuzzy similarity score (0.0-1.0)
                - response_text: Text from model's response (or None if no match)
                - ground_truth_text: Text from ground truth
        """
        # Flatten ground_truth values (list of list of dicts) into single list
        if isinstance(ground_truth, dict):
            ground_truth_flat = [entry for ads in ground_truth.values() for entry in ads]
        else:
            ground_truth_flat = ground_truth

        # Get model response advertisements
        try:
            # For image_4, we need special handling
            if image_name == "image_4":
                logging.info(f"Using special handling for image_4")

                # Get advertisements from response
                response_ads = response.get("advertisements", [])

                # Force the section name for ads without a section
                for ad in response_ads:
                    if isinstance(ad, dict) and ("tags_section" not in ad or not ad.get("tags_section")):
                        ad["tags_section"] = DEFAULT_SECTION

                # Group the modified ads
                response_grouped = self.group_by_section_and_number(response_ads, image_name)
            else:
                # Standard handling for other images
                response_grouped = self.group_by_section_and_number(response.get("advertisements", []), image_name)
        except (KeyError, AttributeError, TypeError) as e:
            logging.warning(f"Error getting response advertisements: {e}")
            response_grouped = {}

        # Group ground truth data
        ground_truth_grouped = self.group_by_section_and_number(ground_truth_flat, image_name)
        results = []

        # Special handling for image_4 with default section
        if image_name == "image_4" and DEFAULT_SECTION in ground_truth_grouped:
            gt_ads = ground_truth_grouped[DEFAULT_SECTION]
            response_ads = response_grouped.get(DEFAULT_SECTION, {})

            # Process each advertisement in ground truth
            for number, gt_ad in gt_ads.items():
                match_found = False

                # First try direct match by number in default section
                response_ad = response_ads.get(number)
                if response_ad:
                    match_found = True
                    similarity = calculate_fuzzy_score(test_value=response_ad["text"], gold_value=gt_ad["text"])
                    results.append({
                        "section": DEFAULT_SECTION,
                        "number": number,
                        "match_found": True,
                        "similarity": round(similarity, 3),
                        "response_text": response_ad["text"],
                        "ground_truth_text": gt_ad["text"]
                    })
                else:
                    # If no direct match, try to find by number across all sections
                    for resp_section, resp_ads in response_grouped.items():
                        if number in resp_ads:
                            response_ad = resp_ads[number]
                            match_found = True
                            similarity = calculate_fuzzy_score(test_value=response_ad["text"], gold_value=gt_ad["text"])
                            results.append({
                                "section": DEFAULT_SECTION,
                                "number": number,
                                "match_found": True,
                                "similarity": round(similarity, 3),
                                "response_text": response_ad["text"],
                                "ground_truth_text": gt_ad["text"]
                            })
                            break

                    # If still no match found, mark as not found
                    if not match_found:
                        results.append({
                            "section": DEFAULT_SECTION,
                            "number": number,
                            "match_found": False,
                            "similarity": 0.0,
                            "response_text": None,
                            "ground_truth_text": gt_ad["text"]
                        })
        else:
            # Standard matching algorithm for all other images
            for section, gt_ads in ground_truth_grouped.items():
                # First try exact match by section name
                response_ads = response_grouped.get(section, {})

                # If no exact match, try fuzzy matching of section names
                if not response_ads:
                    for resp_section, resp_ads in response_grouped.items():
                        similarity = calculate_fuzzy_score(test_value=resp_section, gold_value=section)
                        if similarity >= SECTION_MATCH_THRESHOLD:
                            response_ads = resp_ads
                            break

                # Process each advertisement in this section
                for number, gt_ad in gt_ads.items():
                    response_ad = response_ads.get(number)
                    if response_ad:
                        # Match found - calculate similarity score
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
                        # No match found
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
        Create a markdown visualization of benchmark results for a specific image.
        
        This method generates a detailed markdown report that includes:
        - The original image displayed at the top
        - Overall fuzzy score and character error rate (CER) metrics
        - A link to view the raw JSON result
        - A table comparing model predictions with ground truth for each advertisement
        - Visual highlighting of differences between prediction and ground truth
        
        Args:
            image_name (str): Name of the image being processed (e.g., "image_1").
            result (dict): The model's full JSON response.
            score (dict): Dictionary with 'fuzzy' and 'cer' scores for this image.
            truth (dict): The ground truth data for comparison.
            
        Returns:
            str: Markdown-formatted string containing the complete benchmark report.
                 This report includes the image, scores, and detailed comparison table.
        """
        data = self.prepare_scoring_data(result)
        results = self.compare_ads(response=data, ground_truth=truth, image_name=image_name)

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
        Highlight differences between prediction and ground truth texts with visual styling.
        
        This method performs a character-by-character comparison of the prediction and ground
        truth texts, then wraps differing segments in HTML spans with a light red wavy underline
        for clear visual identification of discrepancies in the generated report.
        
        Args:
            prediction_text (str): The text predicted by the model.
            ground_truth_text (str): The reference ground truth text.
            
        Returns:
            tuple: A tuple containing (formatted_prediction, formatted_ground_truth), where both
                  strings have HTML formatting applied to highlight differences with the "diff" CSS class.
                  Newlines are also replaced with <br> tags for proper rendering in markdown tables.
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
