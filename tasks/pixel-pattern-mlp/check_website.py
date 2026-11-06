"""Check the local or deployed MLP page with Playwright."""
import argparse
import json
from urllib.parse import urljoin
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base-url',help='Deployed site root, including the repository path')
parser.add_argument('--report-dir',type=Path,help='Directory for verification JSON and screenshot')
args=parser.parse_args()
report_dir=args.report_dir or root/'tasks/pixel-pattern-mlp'
report_dir.mkdir(parents=True,exist_ok=True)
if args.base_url:
    if not args.base_url.startswith(('https://','http://')):
        parser.error('--base-url must use HTTP or HTTPS')
    base=args.base_url.rstrip('/')+'/'
    sample_url=urljoin(base,'samples/pixel-pattern-mlp/')
    gallery_url=urljoin(base,'samples/')
else:
    sample_url=(root/'_site/samples/pixel-pattern-mlp/index.html').as_uri()
    gallery_url=(root/'_site/samples/index.html').as_uri()
report={'page_url':sample_url}
final_time=json.loads((root/'tasks/pixel-pattern-mlp/stages.json').read_text())['complete-network']
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    for name,width,height in [('desktop',1280,1000),('mobile',390,844)]:
        page=browser.new_page(viewport={'width':width,'height':height},color_scheme='light')
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(sample_url)
        page.wait_for_function('document.querySelector("video").readyState >= 1')
        assert 'four pixel intensities' in page.get_by_role('main').inner_text()
        video=page.locator('video')
        initial=video.bounding_box()
        page.eval_on_selector('video','v => { v.muted=true; return v.play(); }')
        page.wait_for_function('document.querySelector("video").currentTime > 0.25',timeout=12000)
        assert page.eval_on_selector('video','v => v.currentTime')>0
        playing=video.bounding_box()
        assert initial['width']==playing['width'] and initial['height']==playing['height']
        assert page.eval_on_selector('video','v => !v.error')
        assert page.eval_on_selector('video','v => v.videoWidth===1920 && v.videoHeight===1080')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.eval_on_selector('video','v => v.controlsList.contains("nodownload")')
        assert page.locator('a[download]').count()==0
        assert not errors,errors
        report[name]=dict(initial=initial,playing=playing,errors=errors,
                          page_background=page.evaluate('getComputedStyle(document.body).backgroundColor'),
                          font=page.evaluate('getComputedStyle(document.body).fontFamily'))
        page.eval_on_selector('video','(v,time) => {v.pause();v.currentTime=time;}',final_time)
        page.wait_for_function('(t) => {const v=document.querySelector("video");return !v.seeking && v.readyState>=2 && Math.abs(v.currentTime-t)<0.1;}',arg=final_time,timeout=12000)
        page.wait_for_timeout(100)
        if name=='desktop':
            page.screenshot(path=str(report_dir/'review-website.png'),full_page=True)
        page.close()
    gallery=browser.new_page()
    gallery.goto(gallery_url)
    link=gallery.locator('.sd-card a[href="pixel-pattern-mlp/"]')
    assert link.count()>0,'MLP gallery card missing'
    report['gallery_card_present']=True
    browser.close()
(report_dir/'website-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
