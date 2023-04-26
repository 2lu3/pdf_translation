from argparse import ArgumentParser
from dataclasses import dataclass
from itertools import zip_longest
import json
from typing import Optional
import fitz
import os
import requests

# page.add_redact_annot(
#            block[:4],
#            text="hello world.helo world.helo world.helo world.helo world.helo world.....",
#        )
#
# page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
#
# doc.save("output.pdf")


@dataclass
class Line:
    text: str
    font_size: float


@dataclass
class Group:
    """画面上と文字サイズで分割された文字列"""

    page_number: int
    bbox: tuple[float, float, float, float]
    lines: list[Line]
    # _text default is None
    _text: Optional[str] = None

    @property
    def text(self):
        if self._text is None:
            return "".join([line.text for line in self.lines])
        else:
            return self._text

    @text.setter
    def text(self, value):
        self._text = value


def extract_groups(path) -> list[Group]:
    def font_size(line):
        """lineの中で最も頻度の高いフォントサイズを返す"""
        font_sizes: list[float] = []
        for span in line["spans"]:
            font_sizes.extend([span["size"]] * len(span["text"]))

        # ちょっとだけ大きさが違うフォントサイズは同じフォントサイズとみなす
        sorted_font_sizzes = sorted(font_sizes)
        for font_size1, font_size2 in zip(sorted_font_sizzes, sorted_font_sizzes[1:]):
            if font_size1 == font_size2:
                continue

            if font_size2 - font_size1 < 0.5:
                font_size1_num = font_sizes.count(font_size1)
                font_sizes = [
                    font_size for font_size in font_sizes if font_size != font_size1
                ] + [font_size2] * font_size1_num

        return max(set(font_sizes), key=font_sizes.count)

    def text(line):
        """lineの中のtextを返す"""
        raw_text = "".join([span["text"] for span in line["spans"]])
        return "".join(raw_text.replace("\n", ""))

    result: list[Group] = []
    doc = fitz.open(path)

    for page in doc:
        textpage = page.get_textpage()

        json_dict = json.loads(textpage.extractJSON())

        for block in json_dict["blocks"]:
            lines: list[Line] = []
            for line in block["lines"]:
                lines.append(
                    Line(
                        text=text(line),
                        font_size=font_size(line),
                    )
                )

            result.append(
                Group(
                    page_number=page.number,
                    bbox=block["bbox"],
                    lines=lines,
                )
            )

    return result


def resplit_block_by_period(groups: list[Group]) -> list[Group]:
    """ピリオドで終わっていない文章を次の文章のピリオドまで結合する"""

    result: list[Group] = groups

    # TODO: group2が反映されない
    for group1, group2 in zip(result, result[1:]):
        if group1.text.endswith("."):
            continue

        if abs(group1.lines[-1].font_size - group2.lines[0].font_size) > 0.5:
            continue

        # group1がピリオドで終わっていない場合
        # 次のgroupのピリオドまでを結合することで意味が通る文章の分け方になる
        for line in group2.lines:
            if "." in line.text:
                new_text = line.text.split(".")[0] + "."
                group1.lines[-1].text += new_text
                line.text = line.text[len(new_text) :]
                break
            else:
                group1.lines[-1].text += line.text
                group2.lines.remove(line)

    return result


def translate(groups: list[Group]) -> list[Group]:
    for group in groups:
        params = {
            "auth_key": os.environ.get("DEEPL_API_KEY"),
            "text": group.text,
            "source_lang": "EN",
            "target_lang": "JA",
        }

        request = requests.post(
            "https://api-free.deepl.com/v2/translate", params=params
        )

        group.text = request.json()["translations"][0]["text"]

    return groups


def output_pdf(input_path: str, output_path: str, groups: list[Group]):
    font = fitz.Font("cjk")
    print(font.name)
    doc = fitz.open(input_path)

    for page in doc:
        print(page.mediabox)
        page.insert_font(fontname="F0", fontbuffer=font.buffer)

        x_center = (page.mediabox[0] + page.mediabox[2]) / 2
        y_bottom = page.mediabox[1]
        page.insert_text([x_center - 50,y_bottom + 50, x_center+10, y_bottom+20], "a", fontname="F0", render_mode=3)
        print(page.get_fonts())
        for group in groups:
            if group.page_number != page.number:
                continue

            page.add_redact_annot(
                group.bbox,
                text=group.text,
                #fontname="F0",
            )

        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    doc.save(output_path)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "input_pdf", type=str, default="example.pdf", help="input pdf file"
    )
    parser.add_argument(
        "output_pdf", type=str, default="output.pdf", help="output pdf file"
    )

    args = parser.parse_args()

    groups = extract_groups(args.input_pdf)
    groups = resplit_block_by_period(groups)

    groups = translate(groups)

    output_pdf(args.input_pdf, args.output_pdf, groups)


if __name__ == "__main__":
    main()
