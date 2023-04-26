from argparse import ArgumentParser
from dataclasses import dataclass
from itertools import zip_longest
import json
import fitz

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

    @property
    def text(self):
        return "".join([line.text for line in self.lines])

def extract_blocks(path) -> list[Group]:
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

    def remove_text_until_period(group: Group) -> tuple[str, Group]:
        result: str = ""
        for line in group.lines:
            if "." in line.text:
                result += line.text.split(".")[0] + "."
                line.text = line.text[len(line.text.split(".")[0] + "."):]
                return result, group
            else:
                result += line.text
                del line

        raise ValueError("ピリオドが見つかりませんでした")

    result: list[Group] = groups

    # TODO: group2が反映されない
    for group1, group2 in zip(result, result[1:]):

        if group1.text.endswith("."):
            continue

        if abs(group1.lines[-1].font_size - group2.lines[0].font_size) > 0.5:
            continue

        # group1がピリオドで終わっていない場合
        # 次のgroupのピリオドまでを結合することで意味が通る文章の分け方になる
        text, group2 = remove_text_until_period(group2)
        group1.lines[-1].text += text

    return result


def redact_blocks(path, blocks):
    pass


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "input_pdf", type=str, default="example.pdf", help="input pdf file"
    )
    parser.add_argument(
        "output_pdf", type=str, default="output.pdf", help="output pdf file"
    )

    args = parser.parse_args()

    groups = extract_blocks(args.input_pdf)
    for group in groups:
        for line in group.lines:
            print(line.font_size, line.text)
        print('--------------------------')

    groups = resplit_block_by_period(groups)
    for group in groups:
        print(group.text, end="\n\n\n")


if __name__ == "__main__":
    main()
