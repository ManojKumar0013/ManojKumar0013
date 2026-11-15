"""Small action buttons in the shared arcade palette."""
from ..kit import esc, t


def button(label: str, theme: dict) -> str:
    width = max(90, 30 + len(label) * 10)
    arrow = f'<path d="M{width - 18} 14h6v6m0-6-6 6" fill="none" stroke="{theme["amber"]}" stroke-width="1.5"/>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="32" viewBox="0 0 {width} 32" role="img">
<title>{esc(label)}</title>
<style>.arrow{{animation:appear .45s ease-out}}@keyframes appear{{from{{opacity:.65}}}}@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>
<desc>Open {esc(label)}</desc>
<rect x=".5" y=".5" width="{width - 1}" height="31" rx="7" fill="{theme['bg']}" stroke="{theme['line']}"/>
<rect x="10" y="13" width="7" height="7" rx="1" fill="{theme['amber']}"/>
{t(23,22,label,"",12,weight=700,extra=f' fill="{theme["fg"]}" font-family="monospace"')}
<g class="arrow">{arrow}</g>
</svg>
"""
