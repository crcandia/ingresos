"""Export the existing dashboard bar mark as native SVG and browser PNG icons."""
from pathlib import Path
import shutil
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'interfaz/favicon.svg'
target = ROOT / 'site'
target.mkdir(exist_ok=True)
shutil.copyfile(source, target / 'favicon.svg')
for name, size in [('favicon-32.png', 32), ('apple-touch-icon.png', 180)]:
    cairosvg.svg2png(url=str(source), write_to=str(target / name), output_width=size, output_height=size)
