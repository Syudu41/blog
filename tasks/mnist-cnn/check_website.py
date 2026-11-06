"""Check the built CNN page with Playwright in the website environment."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[2]
report={}
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    for name,width,height in [('desktop',1280,1000),('mobile',390,844)]:
        page=browser.new_page(viewport={'width':width,'height':height},color_scheme='light')
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((root/'_site/samples/mnist-cnn/index.html').as_uri())
        page.wait_for_function('document.querySelector("video").readyState >= 1')
        video=page.locator('video')
        initial=video.bounding_box()
        page.eval_on_selector('video','v => { v.muted=true; return v.play(); }')
        page.wait_for_timeout(800)
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
        page.eval_on_selector('video','v => {v.pause();v.currentTime=38;}')
        page.wait_for_timeout(300)
        if name=='desktop':
            page.screenshot(path=str(root/'tasks/mnist-cnn/review-website.png'),full_page=True)
        page.close()
    gallery=browser.new_page()
    gallery.goto((root/'_site/samples/index.html').as_uri())
    link=gallery.locator('.sd-card a[href="mnist-cnn/"]')
    assert link.count()>0,'CNN gallery card missing'
    report['gallery_card_present']=True
    browser.close()
(root/'tasks/mnist-cnn/website-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
