import json
import os

class DiseaseClassifier:
    def __init__(self, config_filename="disease_definitions.json"):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        config_path = os.path.join(base_dir, config_filename)

        self.definitions = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.definitions = json.load(f).get("groups", {})
            except Exception as e:
                print(f"Error loading disease definitions: {e}")
        else:
            print(f"Warning: Config file not found at {config_path}")


    def get_groups(self):
        """Returns list of available groups and their descriptions."""
        return {k: v['description'] for k, v in self.definitions.items()}


    def _expand_range(self, start_code, end_code):
        """Expands J00-J06 -> [J00, J01, ... J06]"""
        prefix = start_code[0]
        if end_code[0] != prefix: return [start_code, end_code]
        try:
            s, e = int(start_code[1:]), int(end_code[1:])
            return [f"{prefix}{i:02d}" for i in range(s, e + 1)]
        except: return [start_code, end_code]


    def get_target_codes(self, query):
        """
        Input: 'ORVI' (Group Name) OR 'J00' (Root Code)
        Output: List of Root codes (e.g. ['J00', 'J01'...])
        """
        if query in self.definitions:
            codes = set()
            for rule in self.definitions[query]['rules']:
                if "-" in rule:
                    s, e = rule.split("-")
                    prefix = s[0]
                    try:
                        start_num, end_num = int(s[1:]), int(e[1:])
                        codes.update([f"{prefix}{i:02d}" for i in range(start_num, end_num + 1)])
                    except:
                        # Fallback for typos
                        codes.add(s); codes.add(e)
                else:
                    codes.add(rule.strip())
            return list(codes)

        return [query.upper().strip()]


    def search_groups(self, keyword: str):
        """
        Searches group names and descriptions for a keyword.
        Returns: [('Diabetes', 'Diabetes Mellitus (E10-E14)'), ...]
        """
        matches = []
        kw = keyword.lower().strip()

        for name, data in self.definitions.items():
            if kw in name.lower() or kw in data['description'].lower():
                matches.append((name, data['description']))

        return matches