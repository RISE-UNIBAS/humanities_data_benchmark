from scripts.benchmark_base import Benchmark
from scripts.scoring_helper import calculate_fuzzy_score
import re
from collections import defaultdict


class Fraktur(Benchmark):

    def score_benchmark(self, all_scores: list) -> dict:
        """
        Calculate the overall benchmark score by averaging the fuzzy scores of all evaluated documents.
        
        This method computes an average fuzzy matching score across all processed images,
        providing a single metric that represents the benchmark's overall performance.
        
        Args:
            all_scores (list): List of dictionaries containing individual fuzzy scores for each document.
            
        Returns:
            dict: Dictionary with a single key 'fuzzy' containing the averaged fuzzy score.
        """

        total_score = 0
        for score in all_scores:
            total_score += score['fuzzy']

        return {"fuzzy": total_score / len(all_scores)}

    def score_request_answer(self,
                             image_name: str,
                             response: dict,
                             ground_truth: dict) -> dict:
        """
        Score an individual response by comparing extracted advertisements to ground truth.
        
        This method processes the model's response, compares the extracted advertisements 
        with the ground truth data, and calculates a fuzzy similarity score for each advertisement.
        The final score is an average of all individual advertisement similarity scores.
        
        Args:
            image_name (str): Name of the image being processed.
            response (dict): The model's full response containing extracted advertisements.
            ground_truth (dict): The ground truth data for comparison, containing expected advertisements.
            
        Returns:
            dict: Dictionary with a 'fuzzy' key containing the rounded average similarity score.
        """

        data = self.prepare_scoring_data(response)
        results = self.compare_ads(response=data,
                                   ground_truth=ground_truth)

        # avg fuzzy score over all ads on a page
        avg_score = sum([result["similarity"] for result in results]) / len(results)

        return {"fuzzy": round(avg_score, 2)}

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
            section = ad.get("tags_section", "").strip()
            number = self.extract_number_prefix(ad.get("text", ""))
            if section and number:
                grouped[section][number] = ad
        return grouped

    def compare_ads(self,
                    response: dict,
                    ground_truth: dict):
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
        ground_truth_flat = [entry for ads in ground_truth.values() for entry in ads]

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
        advertisements with the ground truth, including similarity scores for each item.
        
        Args:
            image_name (str): Name of the image being processed.
            result (dict): The model's full response.
            score (dict): The calculated scores for this response.
            truth (dict): The ground truth data for comparison.
            
        Returns:
            str: Markdown-formatted string containing the comparison report.
        """
        data = self.prepare_scoring_data(result)
        results = self.compare_ads(response=data, ground_truth=truth)
        
        # Add result header and overall score at the top
        render = f"**Result for image: {image_name}**\n\n"
        render += f"**Average fuzzy score:** {score['fuzzy']:.3f}\n\n"
        
        # Create markdown table with 4 columns
        render += "| Section | Prediction | Ground Truth | Score |\n"
        render += "|---------|------------|--------------|-------|\n"
        
        for item in results:
            section = item["section"]
            prediction = item["response_text"] or "N/A"
            ground_truth = item["ground_truth_text"]
            similarity = f"{item['similarity']:.3f}"
            
            # Format multi-line text for markdown table
            prediction = prediction.replace("\n", "<br>")
            ground_truth = ground_truth.replace("\n", "<br>")
            
            render += f"| {section} | {prediction} | {ground_truth} | {similarity} |\n"
        
        return render
