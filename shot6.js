const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p = await b.newPage({viewport:{width:1280,height:920}});
  await p.goto('file:///root/ecsite/ecosysteme.html');
  await p.waitForTimeout(900);
  await p.screenshot({path:'/root/shot-hero.png'});
  await b.close();
})();
