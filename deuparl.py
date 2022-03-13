from typing import List

class Reischtag():
    def __init__(self, year, session) -> None:
        self.year = year
        self.session = session
        with open(f"data/1_collected/Reischtag/{year}/{session}.txt", 'r') as f:
            self.text = f.read()

    def get_clean(self) -> List[str]:
        with open(f"data/2_preprocessed/Reischtag/{self.year}/{self.session}.txt", 'r') as f:
            cleaned = f.read()
        return cleaned

    def get_post_ocr_norma(self) -> List[str]:
        with open(f"data/3_ocr_post_corrected_spelling_normalization/Reischtag/{self.year}/{self.session}.txt", 'r') as f:
            ocr_spell = f.read()
        return ocr_spell

    def get_slices(self) -> List[str]:
        pass

class Bundestag():
    def __init__(self, period, session) -> None:
        self.sessions = session
        self.period = period
        with open(f"data/1_collected/Bundestag/{period}/{session}.txt", 'r') as f:
            self.text = f.read()

    def get_clean(self) -> List[str]:
        with open(f"data/2_preprocessed/Bundestag/{self.period}/{self.session}.txt", 'r') as f:
            cleaned = f.read()
        return cleaned

    def get_normalized(self) -> List[str]:
        with open(f"data/3_ocr_post_corrected_spelling_normalization/Bundestag/{self.period}/{self.session}.txt", 'r') as f:
            spell = f.read()
        return spell

    def get_slices(self) -> List[str]:
        pass
