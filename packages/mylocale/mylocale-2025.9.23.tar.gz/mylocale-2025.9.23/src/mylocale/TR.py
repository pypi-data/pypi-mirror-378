import csv


class TR:
    def __init__(self, langcode: str, csv_file: str):
        self.langcode = langcode
        self.csv_file = csv_file
        with open(csv_file, newline="", mode="r", encoding="utf-8") as f:
            self.locale_csv = list(csv.DictReader(f, delimiter=","))
        self.csv_langcodes = self.locale_csv[0].keys() if self.locale_csv else []

    def check_rtl(self, langcode: str):
        rtl_langcodes = ["ar", "he", "fa", "ur", "ps", "ku", "dv", "yi", "sd", "kmr"]
        return langcode in rtl_langcodes and langcode in self.csv_langcodes

    def tr(self, target_key, langcode: str):
        for item in self.locale_csv:
            if item["stringname"] == target_key:
                try:
                    if not item[langcode] or item[langcode] == "":
                        return item.get("en", target_key)
                    else:
                        return item[langcode]
                except KeyError:
                    return item.get("en", target_key)
        return target_key
