from pdfminer.high_level import extract_pages
from pdfminer.layout import LTPage, LTTextContainer, LTChar
from dataclasses import dataclass
from scipy.cluster.hierarchy import linkage, fcluster


@dataclass
class Line:
    """pdfから取り出した1行の文字列"""

    page: int
    bbox: tuple
    text: str
    char_size: float


@dataclass
class Group:
    """画面上でまとまっている行の集合"""

    page: int
    bbox: tuple
    lines: list[Line]
    """bboxの中で最も多い文字の大きさ"""
    char_size: float


@dataclass
class Paragraph:
    """段落を構成する行の集合"""

    bbox: tuple
    lines: list[Line]
    """bboxの中で最も多い文字の大きさ"""
    char_size: float


def extract_lines(page: LTPage) -> list[Line]:
    """pageオブジェクトからからLineを抽出する"""
    result: list[Line] = []
    for element in page:
        # 文字列のみ抽出
        if not isinstance(element, LTTextContainer):
            continue

        print(element)
        for char in element:
            print(char)

        char_sizes = [char.size for char in element]
        # 最も頻度が多い文字の大きさを取得
        char_size = max(set(char_sizes), key=char_sizes.count)

        result.append(
            Line(
                page=page.pageid,
                bbox=element.bbox,
                text=element.get_text(),
                char_size=char_size,
            )
        )
    return result


def extract_groups(
    lines: list[Line],
    x_threshold_distance: float = 10,
    y_threshold_distance: float = 10,
) -> list[Group]:
    result: list[Group] = []

    # x軸方向に近い行をグループ化する
    x = [[line.bbox[0], line.bbox[2]] for line in lines]
    x_linkage = linkage(x, method="ward", metric="euclidean")
    x_clusters = fcluster(x_linkage, x_threshold_distance, criterion="ward")
    print(x_clusters)
    return []

    # lineをグループ化する
    for i in range(max(x_clusters)):
        group_lines = [line for line, cluster in zip(lines, x_clusters) if cluster == i]
        if len(group_lines) == 0:
            continue
        group_bbox = (
            min([line.bbox[0] for line in group_lines]),
            min([line.bbox[1] for line in group_lines]),
            max([line.bbox[2] for line in group_lines]),
            max([line.bbox[3] for line in group_lines]),
        )
        group_char_sizes = [line.char_size for line in group_lines]
        group_char_size = max(set(group_char_sizes), key=group_char_sizes.count)
        result.append(
            Group(
                page=group_lines[0].page,
                bbox=group_bbox,
                lines=group_lines,
                char_size=group_char_size,
            )
        )



    return result


def main(path):
    for page_layout in extract_pages(path):
        lines =extract_lines(page_layout)
        groups = extract_groups(lines)
        break

    return
    with open(path, "rb") as f:
        parser = PDFParser(f)
        document = PDFDocument(parser)
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed
        # https://pdfminersix.readthedocs.io/en/latest/api/composable.html#
        laparams = LAParams(
            all_texts=True,
        )
        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            results = []
            print("objs-------------------------")
            get_objs(layout, results)
            for r in results:
                print(r)


main("test3.pdf")
