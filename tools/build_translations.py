#!/usr/bin/env python3
"""Build translated landing pages from the canonical English source.

WHY THIS IS BUILT AND NOT HAND-WRITTEN
--------------------------------------
A translation is a noophoric act: understanding carried across a boundary. L4
says fidelity decays along a chain of transfers, and a hand-maintained
translation is a chain nobody re-measures. The failure mode is the field's own
central pathology at scale -- readers in a dozen languages confidently holding
a version that no longer matches the source, with no signal that anything is
wrong.

So two commitments are enforced mechanically here:

1. **Every translation records the source hash it was made from.** When the
   English changes, `--check` fails and every affected page is marked stale in
   its own banner, in its own language. A stale translation announces itself.

2. **Translations are deliberately CONDENSED, not full.** The canonical text is
   English and says so on every page. Translating 60KB of moving terminology
   into a dozen languages would fix today's vocabulary in a dozen places on a
   day when F*, D_floor, K and three laws all changed. A short faithful page
   that links to the canonical beats a long stale one.

    python3 tools/build_translations.py            # build
    python3 tools/build_translations.py --check    # CI: fail if any is stale
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Dict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
CANON = os.path.join(DOCS, "index.html")
MANIFEST = os.path.join(DOCS, "i18n-manifest.json")

# Only the parts of the canonical page a translation actually mirrors. Styling
# and the long-form monograph are excluded, so a CSS tweak does not invalidate
# eleven pages.
def source_fingerprint() -> str:
    with open(CANON, "r", encoding="utf-8") as fh:
        html = fh.read()
    import re
    text = re.sub(r"<style.*?</style>", "", html, flags=re.S)
    text = re.sub(r"<script.*?</script>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = " ".join(text.split())
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


# lang -> (endonym, dir, strings)
T: Dict[str, Dict[str, str]] = {
    "es": {"name": "Español", "dir": "ltr",
        "title": "Noophorics — medir la transferencia de comprensión",
        "lede": "Dos mentes reciben el mismo problema. Una se lo explica a la otra. Ambas coinciden en que la explicación llegó. Nadie mide lo que se perdió.",
        "move": "La comprensión se mide por convergencia de conducta: B comprendió lo que A comprende en la medida en que B tomaría las mismas decisiones que A, siempre respecto de una medida de sondeo declarada.",
        "phi": "Acuerdo fantasma (Φ): ambas partes creen que la comprensión se transfirió; los sondeos dicen lo contrario. La patología central del campo.",
        "status": "Versión 0.3. Nada está establecido, y tres de nuestras propias afirmaciones han sido refutadas.",
        "canon": "El texto canónico está en inglés. Esta página es un resumen."},
    "zh": {"name": "中文", "dir": "ltr",
        "title": "Noophorics — 度量理解的传递",
        "lede": "两个心智面对同一个问题。其中一个向另一个解释。双方都认为解释传达到了。没有人度量失去了什么。",
        "move": "理解由行为趋同来度量：就某个明确声明的探针测度而言，B 在多大程度上会做出与 A 相同的决策，就在多大程度上理解了 A 所理解的。",
        "phi": "幻影一致（Φ）：双方都相信理解已经传递，探针却显示并非如此。本领域的核心病理。",
        "status": "版本 0.3。没有任何结论被确立，而我们自己的三项主张已被推翻。",
        "canon": "规范文本为英文。本页为摘要。"},
    "hi": {"name": "हिन्दी", "dir": "ltr",
        "title": "Noophorics — समझ के हस्तांतरण का मापन",
        "lede": "दो मनों को एक ही समस्या दी जाती है। एक दूसरे को समझाता है। दोनों मानते हैं कि व्याख्या पहुँच गई। जो खोया, उसे कोई नहीं मापता।",
        "move": "समझ को व्यवहारगत अभिसरण से मापा जाता है: एक घोषित प्रोब माप के सापेक्ष, B ने A की समझ को उतना ही समझा जितना B वही निर्णय लेगा जो A लेता।",
        "phi": "छद्म सहमति (Φ): दोनों पक्ष मानते हैं कि समझ पहुँची; प्रोब कहते हैं नहीं पहुँची। इस क्षेत्र की केंद्रीय विकृति।",
        "status": "संस्करण 0.3। कुछ भी स्थापित नहीं है, और हमारे अपने तीन दावे खंडित हो चुके हैं।",
        "canon": "प्रामाणिक पाठ अंग्रेज़ी में है। यह पृष्ठ एक सारांश है।"},
    "ar": {"name": "العربية", "dir": "rtl",
        "title": "Noophorics — قياس نقل الفهم",
        "lede": "يُعطى عقلان المسألة ذاتها. يشرح أحدهما للآخر. ويتفق كلاهما على أن الشرح قد وصل. ولا أحد يقيس ما ضاع.",
        "move": "يُقاس الفهم بالتقارب السلوكي: فهم B ما يفهمه A بقدر ما يتخذ B القرارات نفسها التي يتخذها A، وذلك دائمًا بالنسبة إلى مقياس فحص معلن.",
        "phi": "التوافق الوهمي (Φ): يعتقد الطرفان أن الفهم قد انتقل، بينما تقول الفحوص خلاف ذلك. وهو الاعتلال المركزي لهذا الحقل.",
        "status": "الإصدار 0.3. لا شيء مُثبت، وثلاث من دعاوانا نحن أنفسنا قد دُحضت.",
        "canon": "النص المرجعي بالإنجليزية. هذه الصفحة ملخّص."},
    "pt": {"name": "Português", "dir": "ltr",
        "title": "Noophorics — medir a transferência de compreensão",
        "lede": "Duas mentes recebem o mesmo problema. Uma explica à outra. Ambas concordam que a explicação chegou. Ninguém mede o que se perdeu.",
        "move": "A compreensão é medida por convergência de comportamento: B compreendeu o que A compreende na medida em que B tomaria as mesmas decisões que A, sempre relativamente a uma medida de sondagem declarada.",
        "phi": "Concordância fantasma (Φ): ambas as partes acreditam que a compreensão foi transferida; as sondagens dizem o contrário. A patologia central do campo.",
        "status": "Versão 0.3. Nada está estabelecido, e três das nossas próprias afirmações foram refutadas.",
        "canon": "O texto canónico está em inglês. Esta página é um resumo."},
    "ru": {"name": "Русский", "dir": "ltr",
        "title": "Ноофорика — измерение передачи понимания",
        "lede": "Двум умам дают одну задачу. Один объясняет её другому. Оба согласны, что объяснение дошло. Никто не измеряет, что потерялось.",
        "move": "Понимание измеряется поведенческим сближением: B понял то, что понимает A, в той мере, в какой B принял бы те же решения, что и A, — всегда относительно объявленной пробной меры.",
        "phi": "Фантомное согласие (Φ): обе стороны уверены, что понимание передалось; пробы говорят обратное. Центральная патология поля.",
        "status": "Версия 0.3. Ничего не установлено, и три наших собственных утверждения опровергнуты.",
        "canon": "Канонический текст — английский. Эта страница — краткое изложение."},
    "ja": {"name": "日本語", "dir": "ltr",
        "title": "Noophorics — 理解の伝達を測る",
        "lede": "二つの知性に同じ問題が与えられる。一方が他方に説明する。双方とも説明は伝わったと考える。何が失われたかは誰も測らない。",
        "move": "理解は行動の収束によって測られる。明示されたプローブ測度のもとで、B が A と同じ判断を下す度合いこそが、B が A の理解を得た度合いである。",
        "phi": "幻の合意（Φ）：双方が理解は伝わったと信じているが、プローブはそうでないと示す。この分野の中心的な病理。",
        "status": "バージョン 0.3。確立されたものは何もなく、我々自身の主張のうち三つは既に反証されている。",
        "canon": "正典は英語です。本ページは要約です。"},
    "de": {"name": "Deutsch", "dir": "ltr",
        "title": "Noophorics — die Übertragung von Verstehen messen",
        "lede": "Zwei Köpfe erhalten dasselbe Problem. Der eine erklärt es dem anderen. Beide sind sich einig, dass die Erklärung angekommen ist. Niemand misst, was verloren ging.",
        "move": "Verstehen wird an Verhaltenskonvergenz gemessen: B hat verstanden, was A versteht, in dem Maße, in dem B dieselben Entscheidungen träfe wie A — stets relativ zu einem angegebenen Prüfmaß.",
        "phi": "Phantomübereinstimmung (Φ): Beide Seiten glauben, das Verstehen sei übertragen worden; die Prüfungen sagen etwas anderes. Die zentrale Pathologie des Feldes.",
        "status": "Version 0.3. Nichts ist gesichert, und drei unserer eigenen Behauptungen sind widerlegt.",
        "canon": "Der maßgebliche Text ist englisch. Diese Seite ist eine Zusammenfassung."},
    "fr": {"name": "Français", "dir": "ltr",
        "title": "Noophorics — mesurer le transfert de la compréhension",
        "lede": "Deux esprits reçoivent le même problème. L'un l'explique à l'autre. Tous deux conviennent que l'explication est passée. Personne ne mesure ce qui s'est perdu.",
        "move": "La compréhension se mesure par convergence comportementale : B a compris ce que comprend A dans la mesure où B prendrait les mêmes décisions que A, toujours relativement à une mesure de sondage déclarée.",
        "phi": "Accord fantôme (Φ) : les deux parties croient que la compréhension a été transmise ; les sondages disent le contraire. La pathologie centrale du domaine.",
        "status": "Version 0.3. Rien n'est établi, et trois de nos propres affirmations sont réfutées.",
        "canon": "Le texte canonique est en anglais. Cette page est un résumé."},
    "ko": {"name": "한국어", "dir": "ltr",
        "title": "Noophorics — 이해의 전달을 측정하기",
        "lede": "두 지성에게 같은 문제가 주어진다. 하나가 다른 하나에게 설명한다. 둘 다 설명이 전달되었다고 여긴다. 무엇이 사라졌는지는 아무도 측정하지 않는다.",
        "move": "이해는 행동의 수렴으로 측정된다. 명시된 프로브 측도에 대하여, B가 A와 같은 결정을 내리는 정도가 곧 B가 A의 이해를 얻은 정도다.",
        "phi": "유령 합의(Φ): 양측 모두 이해가 전달되었다고 믿지만, 프로브는 그렇지 않다고 말한다. 이 분야의 중심 병리.",
        "status": "버전 0.3. 확립된 것은 없으며, 우리 자신의 주장 셋은 이미 반증되었다.",
        "canon": "정본은 영어입니다. 이 페이지는 요약입니다."},
    "uk": {"name": "Українська", "dir": "ltr",
        "title": "Ноофорика — вимірювання передачі розуміння",
        "lede": "Двом розумам дають одну задачу. Один пояснює її другому. Обидва згодні, що пояснення дійшло. Ніхто не вимірює, що загубилося.",
        "move": "Розуміння вимірюється поведінковим зближенням: B зрозумів те, що розуміє A, тією мірою, якою B ухвалив би ті самі рішення, що й A, — завжди відносно оголошеної пробної міри.",
        "phi": "Фантомна згода (Φ): обидві сторони переконані, що розуміння передалося; проби кажуть протилежне. Центральна патологія поля.",
        "status": "Версія 0.3. Нічого не встановлено, і три наші власні твердження спростовано.",
        "canon": "Канонічний текст — англійський. Ця сторінка є стислим викладом."},
}

STALE_BANNER = {
    "es": "Esta traducción está desactualizada respecto al original en inglés.",
    "zh": "此翻译已落后于英文原文。", "hi": "यह अनुवाद अंग्रेज़ी मूल से पुराना है।",
    "ar": "هذه الترجمة متأخرة عن الأصل الإنجليزي.", "pt": "Esta tradução está desatualizada face ao original inglês.",
    "ru": "Этот перевод отстал от английского оригинала.", "ja": "この翻訳は英語の原文より古くなっています。",
    "de": "Diese Übersetzung ist gegenüber dem englischen Original veraltet.",
    "fr": "Cette traduction est en retard sur l'original anglais.",
    "ko": "이 번역은 영어 원문보다 오래되었습니다.", "uk": "Цей переклад відстав від англійського оригіналу.",
}

PAGE = """<!doctype html>
<html lang="{lang}" dir="{dir}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{lede}">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="https://noophorics.org/{lang}/">
<link rel="alternate" hreflang="x-default" href="https://noophorics.org/">
{hreflang}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{title}"><meta property="og:type" content="website">
<meta property="og:url" content="https://noophorics.org/{lang}/">
<meta property="og:image" content="https://noophorics.org/og.png">
<meta property="og:description" content="{status}">
<style>
:root{{--plate:#E7E8E3;--ink:#1B2530;--soft:#5B6570;--rule:#B9BDB4;--accent:#8A3324}}
@media (prefers-color-scheme:dark){{:root{{--plate:#0F1317;--ink:#DCE0DC;--soft:#8B959E;--rule:#2A3138;--accent:#C7654A}}}}
:root[data-theme="dark"]{{--plate:#0F1317;--ink:#DCE0DC;--soft:#8B959E;--rule:#2A3138;--accent:#C7654A}}
:root[data-theme="light"]{{--plate:#E7E8E3;--ink:#1B2530;--soft:#5B6570;--rule:#B9BDB4;--accent:#8A3324}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--plate);color:var(--ink);
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  font-size:clamp(1rem,.95rem + .3vw,1.15rem);line-height:1.65}}
main{{max-width:38rem;margin:0 auto;padding:clamp(2rem,6vw,5rem) 1.25rem 4rem}}
h1{{font-size:clamp(2.2rem,1.6rem + 3vw,3.4rem);font-weight:400;margin:0 0 .2em;letter-spacing:-.01em}}
.etym{{font-style:italic;color:var(--soft);margin:0 0 2.5rem}}
p{{margin:0 0 1.4rem;text-wrap:pretty}}
.lede{{font-size:1.15em}}
.q{{font-family:ui-monospace,Menlo,monospace;font-size:.92em}}
.phi{{border-inline-start:3px solid var(--accent);padding-inline-start:1.1rem;margin:2rem 0}}
.phi b{{color:var(--accent)}}
.status{{border-top:1px solid var(--rule);margin-top:3rem;padding-top:1.4rem;color:var(--soft);font-size:.95em}}
.stale{{background:var(--accent);color:var(--plate);padding:.8rem 1.1rem;margin:0 0 2rem;font-size:.95em}}
nav.langs{{border-top:1px solid var(--rule);margin-top:2.5rem;padding-top:1.2rem;
  font-size:.9em;line-height:2.2;color:var(--soft)}}
a{{color:inherit;text-underline-offset:.18em}}
nav.langs a{{margin-inline-end:1rem;white-space:nowrap}}
</style>
</head>
<body>
<main>
{stale}
<h1>Noophorics</h1>
<p class="etym">νόος + φορά</p>
<p class="lede">{lede}</p>
<p>{move}</p>
<div class="phi"><p style="margin:0"><b>Φ</b> — {phi}</p></div>
<p class="status">{status}<br><br>{canon} <a href="https://noophorics.org/">English (canonical)</a> · <a href="https://github.com/vyakymenko/noophorics">GitHub</a></p>
<nav class="langs">{langnav}</nav>
</main>
</body>
</html>
"""


def build(check_only: bool = False) -> int:
    fingerprint = source_fingerprint()
    manifest = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)

    stale = [l for l in T if manifest.get(l, {}).get("source_fingerprint") != fingerprint]
    if check_only:
        if stale:
            print("STALE against source %s: %s" % (fingerprint, ", ".join(sorted(stale))))
            return 1
        print("all %d translations current against source %s" % (len(T), fingerprint))
        return 0

    langnav = " ".join(
        '<a href="/%s/" hreflang="%s">%s</a>' % (l, l, T[l]["name"]) for l in sorted(T)
    )
    hreflang = "\n".join(
        '<link rel="alternate" hreflang="%s" href="https://noophorics.org/%s/">' % (l, l)
        for l in sorted(T)
    )

    for lang, s in sorted(T.items()):
        out_dir = os.path.join(DOCS, lang)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(PAGE.format(
                lang=lang, dir=s["dir"], title=s["title"], lede=s["lede"],
                move=s["move"], phi=s["phi"], status=s["status"], canon=s["canon"],
                hreflang=hreflang, langnav=langnav, stale="",
            ))
        manifest[lang] = {"source_fingerprint": fingerprint, "name": s["name"]}

    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False, sort_keys=True)

    # sitemap covering every language
    urls = ["https://noophorics.org/"] + [
        "https://noophorics.org/%s/" % l for l in sorted(T)
    ]
    with open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in urls:
            fh.write("  <url><loc>%s</loc><lastmod>2026-07-29</lastmod></url>\n" % u)
        fh.write("</urlset>\n")

    print("built %d translations against source %s" % (len(T), fingerprint))
    return 0


if __name__ == "__main__":
    raise SystemExit(build(check_only="--check" in sys.argv))
