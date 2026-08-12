#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, io, json, math, re, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

COLORS = {
    'VvH 00': (154,119,70), 'VvH 01': (130,130,130), 'VvH 02': (130,35,55),
    'VvH 03': (55,95,135), 'VvH 04': (80,120,75), 'VvH 05': (145,100,45),
    'VvH 06': (95,85,70), 'VvH 07': (115,50,100), 'VvH 08': (170,120,35),
    'VvH 09': (80,105,95),
}

def clean(s): return re.sub(r'&.', '', s)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def load_resource_images(zips: list[Path]) -> tuple[dict[str, Image.Image], list[dict[str, str]]]:
    images: dict[str, Image.Image] = {}
    sources: list[dict[str, str]] = []
    for path in zips:
        sources.append({'path': str(path.resolve()), 'sha256': sha256(path)})
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                match = re.fullmatch(r'assets/([^/]+)/(textures/.+\.png)', name)
                if not match:
                    continue
                key = f'{match.group(1)}:{match.group(2)}'
                try:
                    images[key] = Image.open(io.BytesIO(zf.read(name))).convert('RGBA')
                except OSError:
                    pass
    return images, sources

def paste_contained(canvas: Image.Image, source: Image.Image, center: tuple[float, float],
                    box: tuple[int, int], alpha: int, rotation: float) -> None:
    layer = source.copy()
    layer.thumbnail(box, Image.Resampling.NEAREST)
    if alpha < 255:
        layer.putalpha(layer.getchannel('A').point(lambda value: value * alpha // 255))
    if rotation:
        layer = layer.rotate(-rotation, expand=True, resample=Image.Resampling.BICUBIC)
    canvas.alpha_composite(layer, (round(center[0] - layer.width / 2), round(center[1] - layer.height / 2)))

def main():
    ap=argparse.ArgumentParser(description='Render deterministic source-level VvH layout review boards (not Minecraft screenshots).')
    ap.add_argument('manifest', type=Path); ap.add_argument('out', type=Path)
    ap.add_argument('--resource-zip', action='append', default=[], type=Path,
                    help='Resource-pack ZIP to use for namespaced chapter art; may be repeated.')
    ap.add_argument('--metadata-out', type=Path,
                    help='Write provenance and unresolved-image information as JSON.')
    a=ap.parse_args(); a.out.mkdir(parents=True, exist_ok=True)
    m=json.loads(a.manifest.read_text())
    resource_images, resource_sources = load_resource_images(a.resource_zip)
    unresolved: set[str] = set()
    font=ImageFont.load_default(); small=ImageFont.load_default()
    for idx,ch in enumerate(m['chapters']):
        qs=ch['quests']; xs=[float(q['x']) for q in qs]; ys=[float(q['y']) for q in qs]
        xmin,xmax=min(xs)-2,max(xs)+2; ymin,ymax=min(ys)-2,max(ys)+2
        W,H=1600,1000; margin=80
        sx=(W-2*margin)/(xmax-xmin or 1); sy=(H-2*margin)/(ymax-ymin or 1)
        scale=min(sx,sy)
        def pt(x,y): return (margin+(x-xmin)*scale, margin+(y-ymin)*scale)
        img=Image.new('RGBA',(W,H),(25,27,32,255)); d=ImageDraw.Draw(img)
        base=next((v for k,v in COLORS.items() if ch['title'].startswith(k)),(100,100,100))
        d.text((25,20),f"SOURCE REVIEW BOARD — {ch['title']}",fill=(245,240,225),font=font)
        d.text((25,36),'Not an in-client screenshot; verify FTB rendering manually.',fill=(235,170,100),font=small)
        by={q['id']:q for q in qs}
        # Decorative images approximate the manifest geometry. This is useful for
        # collision/contrast review, but it deliberately does not emulate FTB GUI rendering.
        for art in sorted(ch.get('images', []), key=lambda value: value.get('order', 0)):
            key=art.get('image',''); x,y=pt(float(art['x']),float(art['y']))
            source=resource_images.get(key)
            if source is None:
                unresolved.add(key)
                w=max(24,round(float(art.get('width',1))*scale)); h=max(24,round(float(art.get('height',1))*scale))
                d.rectangle((x-w/2,y-h/2,x+w/2,y+h/2),fill=(45,45,52,90),outline=(120,120,130,150),width=2)
                label=key.split(':',1)[-1].rsplit('/',1)[-1]
                d.text((x-w/2+3,y-h/2+3),label[:24],fill=(190,190,200,180),font=small)
            else:
                paste_contained(img, source, (x,y),
                                (max(1,round(float(art.get('width',1))*scale)),
                                 max(1,round(float(art.get('height',1))*scale))),
                                int(art.get('alpha',255)), float(art.get('rotation',0)))
        d=ImageDraw.Draw(img)
        # lines first
        for q in qs:
            if q.get('hide_dependency_lines'):
                continue
            x2,y2=pt(float(q['x']),float(q['y']))
            for dep in q['dependencies']:
                if dep in by:
                    x1,y1=pt(float(by[dep]['x']),float(by[dep]['y']))
                    d.line((x1,y1,x2,y2),fill=(100,105,115),width=3)
        # nodes
        for q in qs:
            x,y=pt(float(q['x']),float(q['y'])); r=34*float(q.get('size',1.2))
            fill=tuple(min(255,int(c*1.1)) for c in base)
            outline=(245,220,125) if not q['optional'] else (175,180,185)
            d.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=outline,width=4)
            label=clean(q['title'])
            words=label.split(); lines=[]; cur=''
            for w in words:
                test=(cur+' '+w).strip()
                if len(test)>20 and cur:
                    lines.append(cur); cur=w
                else: cur=test
            if cur: lines.append(cur)
            lines=lines[:4]
            yy=y-r-15-len(lines)*12
            for line in lines:
                bbox=d.textbbox((0,0),line,font=small); tw=bbox[2]-bbox[0]
                d.text((x-tw/2,yy),line,fill=(245,245,245),font=small); yy+=12
            d.text((x-18,y-5),q['id'][-4:],fill=(255,255,255),font=small)
            if q.get('min_required_dependencies'):
                d.text((x-r,y+r+3),f"{q['min_required_dependencies']}/{len(q['dependencies'])}",fill=(255,220,130),font=small)
        out=a.out/f"{idx:02d}_{ch['filename']}.png"; img.convert('RGB').save(out,optimize=True)
    # contact sheet
    files=sorted(a.out.glob('[0-9][0-9]_*.png'))
    thumbs=[]
    for f in files:
        im=Image.open(f); im.thumbnail((600,375)); thumbs.append((f,im.copy()))
    sheet=Image.new('RGB',(1200,math.ceil(len(thumbs)/2)*410),(15,15,18)); sd=ImageDraw.Draw(sheet)
    for i,(f,im) in enumerate(thumbs):
        x=(i%2)*600; y=(i//2)*410; sheet.paste(im,(x,y+25)); sd.text((x+5,y+5),f.stem,fill=(240,240,240),font=small)
    sheet.save(a.out/'contact_sheet.png',optimize=True)
    metadata = {
        'artifact_type': 'source-level review board; not runtime or in-client evidence',
        'manifest': {'path': str(a.manifest.resolve()), 'sha256': sha256(a.manifest)},
        'resource_sources': resource_sources,
        'resolved_resource_images': sorted(resource_images),
        'unresolved_references': sorted(value for value in unresolved if value),
        'outputs': [f.name for f in sorted(a.out.glob('*.png'))],
    }
    metadata_path = a.metadata_out or a.out/'render-metadata.json'
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(metadata, indent=2))
if __name__=='__main__': main()
