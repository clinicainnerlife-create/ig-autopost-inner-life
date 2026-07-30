"""
Gera o PNG de um post a partir do template SVG + conteúdo do calendário.
Usa Jinja2 pra preencher o template e wkhtmltoimage pra rasterizar
(evita problemas de acentuação: forçamos UTF-8 explicitamente).

A saída final é convertida pra JPEG porque a API de publicação do
Instagram não aceita PNG (nem imagens com canal de transparência).
"""
import subprocess
import tempfile
from pathlib import Path

from jinja2 import Template
from PIL import Image

TEMPLATE_PATH = Path(__file__).parent / "templates" / "post_template.svg.j2"


def render_svg(post: dict) -> str:
    template = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return template.render(
        eyebrow=post["eyebrow"],
        headline_lines=post["headline_lines"],
        subtext=post["subtext"],
    )


def _rasterize(svg_content: str, output_path: Path) -> Path:
    """Converte um conteúdo SVG (string) em JPEG, forçando UTF-8 e
    achatando qualquer transparência num fundo branco."""
    with tempfile.NamedTemporaryFile(
        suffix=".html", mode="w", encoding="utf-8", delete=False
    ) as f:
        f.write(
            "<!DOCTYPE html><html><head><meta charset='UTF-8'>"
            "<style>body{margin:0;padding:0;width:1080px;height:1080px;}</style>"
            f"</head><body>{svg_content}</body></html>"
        )
        html_path = f.name

    png_path = output_path.with_suffix(".png")
    subprocess.run(
        [
            "wkhtmltoimage",
            "--encoding", "utf-8",
            "--width", "1080",
            "--height", "1080",
            "--disable-smart-width",
            html_path,
            str(png_path),
        ],
        check=True,
        capture_output=True,
    )

    with Image.open(png_path) as im:
        rgb = Image.new("RGB", im.size, (255, 255, 255))
        rgb.paste(im, mask=im.split()[3] if im.mode == "RGBA" else None)
        rgb.save(output_path, "JPEG", quality=92)

    png_path.unlink(missing_ok=True)
    return output_path


def svg_to_jpeg(svg_content: str, output_path: Path) -> Path:
    return _rasterize(svg_content, output_path)


def svg_file_to_jpeg(svg_path: Path, output_path: Path) -> Path:
    """Converte um arquivo .svg já pronto (ex: slide de carrossel
    desenhado à mão) direto pra JPEG, sem passar pelo template Jinja."""
    return _rasterize(svg_path.read_text(encoding="utf-8"), output_path)


def generate(post: dict, output_dir: Path) -> Path:
    svg_content = render_svg(post)
    output_path = output_dir / f"post_{post['id']}.jpg"
    return svg_to_jpeg(svg_content, output_path)


def generate_carousel(post: dict, output_dir: Path, assets_root: Path) -> list[Path]:
    """Gera todas as imagens de um post do tipo carrossel, na ordem
    listada em post['slides'] (caminhos relativos de arquivos .svg)."""
    paths = []
    for i, slide_svg_relpath in enumerate(post["slides"], start=1):
        svg_path = assets_root / slide_svg_relpath
        output_path = output_dir / f"post_{post['id']}_slide_{i}.jpg"
        paths.append(svg_file_to_jpeg(svg_path, output_path))
    return paths
