#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

COLORS = {
    'VvH 00': (154,119,70), 'VvH 01': (130,130,130), 'VvH 02': (130,35,55),
    'VvH 03': (55,95,135), 'VvH 04': (80,120,75), 'VvH 05': (145,100,45),
    'VvH 06': (95,85,70), 'VvH 07': (115,50,100), 'VvH 08': (170,120,35),
    'VvH 09': (80,105,95),
}

def clean(s): return re.sub(r'&.', '', s)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('manifest', type=Path); ap.add_argument('out', type=Path)
    a=ap.parse_args(); a.out.mkdir(parents=True, exist_ok=True)
    m=json.loads(a.manifest.read_text())
    font=ImageFont.load_default(); small=ImageFont.load_default()
    for idx,ch in enumerate(m['chapters']):
        qs=ch['quests']; xs=[float(q['x']) for q in qs]; ys=[float(q['y']) for q in qs]
        xmin,xmax=min(xs)-2,max(xs)+2; ymin,ymax=min(ys)-2,max(ys)+2
        W,H=1600,1000; margin=80
        sx=(W-2*margin)/(xmax-xmin or 1); sy=(H-2*margin)/(ymax-ymin or 1)
        scale=min(sx,sy)
        def pt(x,y): return (margin+(x-xmin)*scale, margin+(y-ymin)*scale)
        img=Image.new('RGB',(W,H),(25,27,32)); d=ImageDraw.Draw(img)
        base=next((v for k,v in COLORS.items() if ch['title'].startswith(k)),(100,100,100))
        d.text((25,20),ch['title'],fill=(245,240,225),font=font)
        by={q['id']:q for q in qs}
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
        out=a.out/f"{idx:02d}_{ch['filename']}.png"; img.save(out,optimize=True)
    # contact sheet
    files=sorted(a.out.glob('[0-9][0-9]_*.png'))
    thumbs=[]
    for f in files:
        im=Image.open(f); im.thumbnail((600,375)); thumbs.append((f,im.copy()))
    sheet=Image.new('RGB',(1200,math.ceil(len(thumbs)/2)*410),(15,15,18)); sd=ImageDraw.Draw(sheet)
    for i,(f,im) in enumerate(thumbs):
        x=(i%2)*600; y=(i//2)*410; sheet.paste(im,(x,y+25)); sd.text((x+5,y+5),f.stem,fill=(240,240,240),font=small)
    sheet.save(a.out/'contact_sheet.png',optimize=True)
if __name__=='__main__': main()
