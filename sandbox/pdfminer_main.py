from pdfminer.high_level import extract_pages
from pdfminer.layout import LTPage, LTTextBox, LTTextContainer, LTChar, LTTextLine
from dataclasses import dataclass
from scipy.cluster.hierarchy import linkage, fcluster
import requests
import os
from time import sleep


@dataclass
class Group:
    """画面上でまとまっている文字列"""

    page: int
    bbox: tuple
    text: str
    """bboxの中で最も多い文字の大きさ"""
    char_size: float


@dataclass
class Paragraph:
    """段落を構成するグループの集合"""

    groups: list[Group]


def extract_groups(page: LTPage) -> list[Group]:
    """pageオブジェクトからからGroupを抽出する"""

    def main_char_size(textbox: LTTextBox) -> float:
        """textbox内の文字の大きさの最頻値を取得する"""

        char_sizes: list[float] = []
        for line in textbox:
            if not isinstance(line, LTTextLine):
                continue
            for char in line:
                if not isinstance(char, LTChar):
                    continue
                char_sizes.append(char.size)

        return max(set(char_sizes), key=char_sizes.count)

    result: list[Group] = []
    for textbox in page:
        # TextBoxのみ抽出
        if not isinstance(textbox, LTTextBox):
            continue

        print(textbox.get_text(), end="\n\n\n")

        result.append(
            Group(
                page=page.pageid,
                bbox=textbox.bbox,
                text=textbox.get_text().replace("\n", ""),
                char_size=main_char_size(textbox),
            )
        )
    return result


def groups2paragraphs(groups: list[Group]) -> list[Paragraph]:
    result: list[Paragraph] = [Paragraph([])]

    # ピリオドで終わると新しく段落を作る
    for group in groups:
        result[-1].groups.append(group)
        if group.text.endswith("."):
            result.append(Paragraph([]))

    return result


def translate_paragraphs(paragraphs: list[Paragraph]) -> list[Paragraph]:
    def translate_paragraph(
        paragraph: Paragraph, API_KEY=os.environ.get("DEEPL_API_KEY")
    ) -> Paragraph:
        result = Paragraph([])
        
        for group in paragraph.groups:
            params = {
                "auth_key": API_KEY,
                "text": group.text,
                "source_lang": "EN",
                "target_lang": "JA",
            }
    
            request = requests.post(
                "https://api-free.deepl.com/v2/translate", params=params
            )
            result.groups.append(
                Group(
                    page=group.page,
                    bbox=group.bbox,
                    text=request.json()["translations"][0]["text"],
                    char_size=group.char_size,
                )
            )
            sleep(1)

        return result

    return [translate_paragraph(paragraph) for paragraph in paragraphs]



def main(path):
    groups: list[Group] = []
    for page_layout in extract_pages(path):
        groups.extend(extract_groups(page_layout))

    paragraphs = groups2paragraphs(groups)
    translated_paragraphs = translate_paragraphs(paragraphs)

    for paragraph in translated_paragraphs:
        for group in paragraph.groups:
            print(group.text, end="\n\n\n")

main("output.pdf")
