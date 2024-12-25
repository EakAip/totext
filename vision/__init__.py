import pdfplumber

from .ocr import OCR
from .recognizer import Recognizer
from .layout_recognizer import LayoutRecognizer
from .table_structure_recognizer import TableStructureRecognizer
import os

def init_in_out(args):
    from PIL import Image
    import os
    import traceback
    from api.utils.file_utils import traversal_files
    images = []
    outputs = []

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    def pdf_pages(fnm, zoomin=3):
        nonlocal outputs, images
        pdf = pdfplumber.open(fnm)
        images = [p.to_image(resolution=72 * zoomin).annotated for i, p in
                            enumerate(pdf.pages)]

        for i, page in enumerate(images):
            outputs.append(os.path.split(fnm)[-1] + f"_{i}.jpg")

    def images_and_outputs(fnm):
        nonlocal outputs, images
        if fnm.split(".")[-1].lower() == "pdf":
            pdf_pages(fnm)
            return
        try:
            images.append(Image.open(fnm))
            outputs.append(os.path.split(fnm)[-1])
        except Exception as e:
            traceback.print_exc()

    if os.path.isdir(args.inputs):
        for fnm in traversal_files(args.inputs):
            images_and_outputs(fnm)
    else:
        images_and_outputs(args.inputs)

    for i in range(len(outputs)): outputs[i] = os.path.join(args.output_dir, outputs[i])

    return images, outputs

def init_in_out2(args):    # 让它生成图片的路径而不是直接加载图片。这样可以控制何时加载图片，从而更好地管理内存使用。
    outputs = []
    image_paths = []

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    def process_pdf(fnm):
        with pdfplumber.open(fnm) as pdf:
            num_pages = len(pdf.pages)
            for i in range(num_pages):
                page = pdf.pages[i]
                img = page.to_image()
                img_path = os.path.join(args.output_dir, f"{os.path.basename(fnm).split('.')[0]}_page_{i}.png")
                img.save(img_path, format='PNG')
                image_paths.append(img_path)
                outputs.append(img_path)

    if os.path.isdir(args.inputs):
        for fnm in os.listdir(args.inputs):
            full_path = os.path.join(args.inputs, fnm)
            if fnm.lower().endswith(".pdf"):
                process_pdf(full_path)
            else:
                output_path = os.path.join(args.output_dir, os.path.basename(full_path))
                image_paths.append(full_path)
                outputs.append(output_path)
    else:
        if args.inputs.lower().endswith(".pdf"):
            process_pdf(args.inputs)
        else:
            output_path = os.path.join(args.output_dir, os.path.basename(args.inputs))
            image_paths.append(args.inputs)
            outputs.append(output_path)

    return image_paths, outputs