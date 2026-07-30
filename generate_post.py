"""
Gera o PNG de um post a partir do template SVG + conteúdo do calendário.
Usa Jinja2 pra preencher o template e wkhtmltoimage pra rasterizar
(evita problemas de acentuação: forçamos UTF-8 explicitamente).
"""
import subprocess
import tempfile
from pathlib import Path
from jinja2 import Template

TEMPLATE_PATH = Path(__file__).parent / "templates" / "post_template.svg.j2"


def render_svg(post: dict) -> str:
    template = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return template.render(
        eyebrow=post["eyebrow"],
        headline_lines=post["headline_lines"],
        subtext=post["subtext"],
    )


def svg_to_png(svg_content: str, output_path: Path) -> Path:
    with tempfile.NamedTemporaryFile(
        suffix=".html", mode="w", encoding="utf-8", delete=False
    ) as f:
        f.write(
            "<!DOCTYPE html><html><head><meta charset='UTF-8'>"
            "<style>body{margin:0;padding:0;width:1080px;height:1080px;}</style>"
            f"</head><body>{svg_content}</body></html>"
        )
        html_path = f.name

    subprocess.run(
        [
            "wkhtmltoimage",
            "--encoding", "utf-8",
            "--width", "1080",
            "--height", "1080",
            "--disable-smart-width",
            html_path,
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )
    return output_path


def generate(post: dict, output_dir: Path) -> Path:
    svg_content = render_svg(post)
    output_path = output_dir / f"post_{post['id']}.png"
    return svg_to_png(svg_content, output_path)
