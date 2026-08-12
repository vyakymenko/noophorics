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
import time
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
    """Hash only the canonical passages the translations actually restate.

    v1 hashed every visible word on the canonical page. Any edit anywhere --
    a new card, a corrected footer -- marked all eleven translations stale,
    and rebuilding re-stamped the fingerprint without changing a translated
    word. A staleness check whose remedy is a no-op is worse than none: it
    trains you to clear the warning rather than read it.

    The four passages below are marked ``data-i18n-src`` in the canonical page,
    so the coupling is visible at both ends. If a marker disappears this raises
    rather than quietly hashing less -- silently narrowing what is watched is
    exactly the failure mode being repaired.
    """
    with open(CANON, "r", encoding="utf-8") as fh:
        html = fh.read()
    import re

    parts = []
    for key in ("lede", "move", "phi", "status"):
        m = re.search(
            r'<([a-z0-9]+)[^>]*data-i18n-src="%s"[^>]*>(.*?)</\1>' % key,
            html, re.S)
        if not m:
            raise SystemExit(
                "canonical page has no data-i18n-src=\"%s\" element. The "
                "translations restate it, so it must stay marked; re-mark it "
                "or drop the string from the translation set." % key)
        text = " ".join(re.sub(r"<[^>]+>", " ", m.group(2)).split())
        parts.append("%s\x1f%s" % (key, text))
    return hashlib.sha256("\x1e".join(parts).encode("utf-8")).hexdigest()[:12]


# lang -> (endonym, dir, strings)
T: Dict[str, Dict[str, str]] = {
    "es": {"name": "Español", "dir": "ltr",
        "title": "Noophorics — medir la transferencia de comprensión",
        "lede": "Dos mentes reciben el mismo problema. Una se lo explica a la otra. Ambas coinciden en que la explicación llegó. Nadie mide lo que se perdió.",
        "move": "La comprensión se mide por convergencia de conducta hacia una referencia declarada: B comprendió lo que A comprende en la medida en que las decisiones de B se acercan a esa referencia, siempre respecto de una medida de sondeo declarada.",
        "phi": "Acuerdo fantasma (Φ): ambas partes creen que la comprensión se transfirió; los sondeos dicen lo contrario. La patología central del campo.",
        "status": "Versión 0.5. Un resultado preregistrado ya está establecido. Catorce de nuestras propias afirmaciones han sido retiradas y cuatro experimentos son nulos.",
        "skip": "Ir al contenido", "canon": "El texto canónico está en inglés. Esta página es un resumen."},
    "zh": {"name": "中文", "dir": "ltr",
        "title": "Noophorics — 度量理解的传递",
        "lede": "两个心智面对同一个问题。其中一个向另一个解释。双方都认为解释传达到了。没有人度量失去了什么。",
        "move": "理解由行为趋同来度量，且趋向于一个明确声明的参照：就某个明确声明的探针测度而言，B 的决策在多大程度上靠近该参照，就在多大程度上理解了 A 所理解的。",
        "phi": "幻影一致（Φ）：双方都相信理解已经传递，探针却显示并非如此。本领域的核心病理。",
        "status": "版本 0.5。一项预注册结果现已确立。我们自己的十四项主张已被撤回，四项实验作废。",
        "skip": "跳到正文", "canon": "规范文本为英文。本页为摘要。"},
    "hi": {"name": "हिन्दी", "dir": "ltr",
        "title": "Noophorics — समझ के हस्तांतरण का मापन",
        "lede": "दो मनों को एक ही समस्या दी जाती है। एक दूसरे को समझाता है। दोनों मानते हैं कि व्याख्या पहुँच गई। जो खोया, उसे कोई नहीं मापता।",
        "move": "समझ को एक घोषित संदर्भ की ओर व्यवहारगत अभिसरण से मापा जाता है: एक घोषित प्रोब माप के सापेक्ष, B के निर्णय उस संदर्भ के जितने निकट आते हैं, उतनी ही समझ पहुँची।",
        "phi": "छद्म सहमति (Φ): दोनों पक्ष मानते हैं कि समझ पहुँची; प्रोब कहते हैं नहीं पहुँची। इस क्षेत्र की केंद्रीय विकृति।",
        "status": "संस्करण 0.5। एक पूर्व-पंजीकृत परिणाम अब स्थापित है, हमारे अपने चौदह दावे वापस लिए जा चुके हैं, और चार प्रयोग रद्द हैं।",
        "skip": "सामग्री पर जाएँ", "canon": "प्रामाणिक पाठ अंग्रेज़ी में है। यह पृष्ठ एक सारांश है।"},
    "ar": {"name": "العربية", "dir": "rtl",
        "title": "Noophorics — قياس نقل الفهم",
        "lede": "يُعطى عقلان المسألة ذاتها. يشرح أحدهما للآخر. ويتفق كلاهما على أن الشرح قد وصل. ولا أحد يقيس ما ضاع.",
        "move": "يُقاس الفهم بالتقارب السلوكي نحو مرجع معلَن: بقدر ما تقترب قرارات B من ذلك المرجع، بالنسبة إلى مقياس فحص معلن، يكون الفهم قد وصل.",
        "phi": "التوافق الوهمي (Φ): يعتقد الطرفان أن الفهم قد انتقل، بينما تقول الفحوص خلاف ذلك. وهو الاعتلال المركزي لهذا الحقل.",
        "status": "الإصدار 0.5. نتيجة واحدة مُسجَّلة مسبقًا صارت مُثبتة، وقد سُحبت أربع عشرة من دعاوانا، وأُبطلت أربع تجارب.",
        "skip": "تخطَّ إلى المحتوى", "canon": "النص المرجعي بالإنجليزية. هذه الصفحة ملخّص."},
    "pt": {"name": "Português", "dir": "ltr",
        "title": "Noophorics — medir a transferência de compreensão",
        "lede": "Duas mentes recebem o mesmo problema. Uma explica à outra. Ambas concordam que a explicação chegou. Ninguém mede o que se perdeu.",
        "move": "A compreensão é medida por convergência de comportamento em direção a uma referência declarada: B compreendeu na medida em que as decisões de B se aproximam dessa referência, sempre relativamente a uma medida de sondagem declarada.",
        "phi": "Concordância fantasma (Φ): ambas as partes acreditam que a compreensão foi transferida; as sondagens dizem o contrário. A patologia central do campo.",
        "status": "Versão 0.5. Um resultado pré-registado está agora estabelecido, catorze das nossas próprias afirmações foram retiradas e quatro experiências são nulas.",
        "skip": "Ir para o conteúdo", "canon": "O texto canónico está em inglês. Esta página é um resumo."},
    "ru": {"name": "Русский", "dir": "ltr",
        "title": "Ноофорика — измерение передачи понимания",
        "lede": "Двум умам дают одну задачу. Один объясняет её другому. Оба согласны, что объяснение дошло. Никто не измеряет, что потерялось.",
        "move": "Понимание измеряется поведенческим сближением с объявленным эталоном: B понял в той мере, в какой решения B приближаются к этому эталону, — всегда относительно объявленной пробной меры.",
        "phi": "Фантомное согласие (Φ): обе стороны уверены, что понимание передалось; пробы говорят обратное. Центральная патология поля.",
        "status": "Версия 0.5. Установлен один пред-зарегистрированный результат, четырнадцать наших собственных утверждений отозваны, четыре эксперимента признаны недействительными.",
        "skip": "Перейти к содержанию", "canon": "Канонический текст — английский. Эта страница — краткое изложение."},
    "ja": {"name": "日本語", "dir": "ltr",
        "title": "Noophorics — 理解の伝達を測る",
        "lede": "二つの知性に同じ問題が与えられる。一方が他方に説明する。双方とも説明は伝わったと考える。何が失われたかは誰も測らない。",
        "move": "理解は、明示された参照へ向かう行動の収束によって測られる。明示されたプローブ測度のもとで、B の判断がその参照にどれだけ近づくかが、理解の度合いである。",
        "phi": "幻の合意（Φ）：双方が理解は伝わったと信じているが、プローブはそうでないと示す。この分野の中心的な病理。",
        "status": "バージョン 0.5。事前登録された結果が一件、確立された。我々自身の主張のうち十四件は撤回され、四つの実験は無効となった。",
        "skip": "本文へ", "canon": "正典は英語です。本ページは要約です。"},
    "de": {"name": "Deutsch", "dir": "ltr",
        "title": "Noophorics — die Übertragung von Verstehen messen",
        "lede": "Zwei Köpfe erhalten dasselbe Problem. Der eine erklärt es dem anderen. Beide sind sich einig, dass die Erklärung angekommen ist. Niemand misst, was verloren ging.",
        "move": "Verstehen wird an Verhaltenskonvergenz zu einer angegebenen Referenz gemessen: B hat in dem Maße verstanden, in dem sich Bs Entscheidungen dieser Referenz annähern — stets relativ zu einem angegebenen Prüfmaß.",
        "phi": "Phantomübereinstimmung (Φ): Beide Seiten glauben, das Verstehen sei übertragen worden; die Prüfungen sagen etwas anderes. Die zentrale Pathologie des Feldes.",
        "status": "Version 0.5. Ein präregistriertes Ergebnis ist nun gesichert, vierzehn unserer eigenen Behauptungen sind zurückgezogen, und vier Experimente sind ungültig.",
        "skip": "Zum Inhalt springen", "canon": "Der maßgebliche Text ist englisch. Diese Seite ist eine Zusammenfassung."},
    "fr": {"name": "Français", "dir": "ltr",
        "title": "Noophorics — mesurer le transfert de la compréhension",
        "lede": "Deux esprits reçoivent le même problème. L'un l'explique à l'autre. Tous deux conviennent que l'explication est passée. Personne ne mesure ce qui s'est perdu.",
        "move": "La compréhension se mesure par convergence comportementale vers une référence déclarée : B a compris dans la mesure où les décisions de B se rapprochent de cette référence, toujours relativement à une mesure de sondage déclarée.",
        "phi": "Accord fantôme (Φ) : les deux parties croient que la compréhension a été transmise ; les sondages disent le contraire. La pathologie centrale du domaine.",
        "status": "Version 0.5. Un résultat préenregistré est désormais établi, quatorze de nos propres affirmations sont retirées et quatre expériences sont nulles.",
        "skip": "Aller au contenu", "canon": "Le texte canonique est en anglais. Cette page est un résumé."},
    "ko": {"name": "한국어", "dir": "ltr",
        "title": "Noophorics — 이해의 전달을 측정하기",
        "lede": "두 지성에게 같은 문제가 주어진다. 하나가 다른 하나에게 설명한다. 둘 다 설명이 전달되었다고 여긴다. 무엇이 사라졌는지는 아무도 측정하지 않는다.",
        "move": "이해는 명시된 기준을 향한 행동의 수렴으로 측정된다. 명시된 프로브 측도에 대하여, B의 결정이 그 기준에 얼마나 가까워지는가가 곧 이해의 정도다.",
        "phi": "유령 합의(Φ): 양측 모두 이해가 전달되었다고 믿지만, 프로브는 그렇지 않다고 말한다. 이 분야의 중심 병리.",
        "status": "버전 0.5. 사전 등록된 결과 한 건이 이제 확립되었고, 우리 자신의 주장 열네 건은 철회되었으며, 실험 네 건은 무효다.",
        "skip": "본문으로 건너뛰기", "canon": "정본은 영어입니다. 이 페이지는 요약입니다."},
    "it": {"name": "Italiano", "dir": "ltr",
        "title": "Noophorics — misurare il trasferimento della comprensione",
        "lede": "A due menti viene dato lo stesso problema. Una lo spiega all'altra. Entrambe concordano che la spiegazione sia arrivata. Nessuno misura ciò che è andato perduto.",
        "move": "La comprensione si misura come convergenza comportamentale verso un riferimento dichiarato: B ha compreso ciò che A comprende nella misura in cui le decisioni di B si avvicinano a quel riferimento, sempre rispetto a una misura di sonda dichiarata.",
        "phi": "Accordo fantasma (Φ): entrambe le parti credono che la comprensione sia passata; le sonde dicono il contrario. La patologia centrale del campo.",
        "status": "Versione 0.5. Un risultato preregistrato è ora stabilito, quattordici delle nostre stesse affermazioni sono state ritirate e quattro esperimenti sono nulli.",
        "skip": "Vai al contenuto", "canon": "Il testo canonico è in inglese. Questa pagina è un riassunto."},
    "pl": {"name": "Polski", "dir": "ltr",
        "title": "Noophorics — pomiar transferu rozumienia",
        "lede": "Dwa umysły dostają ten sam problem. Jeden tłumaczy go drugiemu. Oba zgadzają się, że wyjaśnienie dotarło. Nikt nie mierzy tego, co zginęło po drodze.",
        "move": "Rozumienie mierzy się zbieżnością zachowań wobec zadeklarowanego odniesienia: B zrozumiał to, co rozumie A, w tym stopniu, w jakim decyzje B zbliżają się do tego odniesienia — zawsze względem zadeklarowanej miary sond.",
        "phi": "Zgoda pozorna (Φ): obie strony wierzą, że rozumienie zostało przekazane; sondy mówią co innego. Centralna patologia tej dziedziny.",
        "status": "Wersja 0.5. Jeden wynik zarejestrowany z wyprzedzeniem jest już ustalony, czternaście naszych własnych twierdzeń wycofano, a cztery eksperymenty są nieważne.",
        "skip": "Przejdź do treści", "canon": "Tekst kanoniczny jest po angielsku. Ta strona to streszczenie."},
    "tr": {"name": "Türkçe", "dir": "ltr",
        "title": "Noophorics — anlayışın aktarımını ölçmek",
        "lede": "İki zihne aynı problem verilir. Biri diğerine anlatır. İkisi de açıklamanın ulaştığında hemfikirdir. Kaybolanı kimse ölçmez.",
        "move": "Anlayış, beyan edilmiş bir referansa doğru davranışsal yakınsamayla ölçülür: B'nin kararları o referansa ne kadar yaklaşıyorsa, beyan edilmiş bir sonda ölçüsüne göre, A'nın anladığını o kadar anlamıştır.",
        "phi": "Hayalet mutabakat (Φ): iki taraf da anlayışın aktarıldığına inanır; sondalar aksini söyler. Alanın merkezî patolojisi.",
        "status": "Sürüm 0.5. Önceden kaydedilmiş bir sonuç artık yerleşmiş durumda, kendi iddialarımızdan on dört tanesi geri çekildi ve dört deney geçersiz.",
        "skip": "İçeriğe geç", "canon": "Kanonik metin İngilizcedir. Bu sayfa bir özettir."},
    "id": {"name": "Bahasa Indonesia", "dir": "ltr",
        "title": "Noophorics — mengukur perpindahan pemahaman",
        "lede": "Dua pikiran diberi persoalan yang sama. Yang satu menjelaskannya kepada yang lain. Keduanya sepakat penjelasan itu sampai. Tidak ada yang mengukur apa yang hilang.",
        "move": "Pemahaman diukur lewat konvergensi perilaku menuju rujukan yang dinyatakan: B memahami apa yang dipahami A sejauh keputusan B mendekati rujukan itu, selalu relatif terhadap ukuran probe yang dinyatakan.",
        "phi": "Kesepakatan semu (Φ): kedua pihak percaya pemahaman telah berpindah; probe berkata sebaliknya. Patologi inti bidang ini.",
        "status": "Versi 0.5. Satu hasil yang dipradaftarkan kini tegak, empat belas klaim kami sendiri ditarik, dan empat eksperimen batal.",
        "skip": "Lewati ke konten", "canon": "Teks kanonik dalam bahasa Inggris. Halaman ini ringkasan."},
    "vi": {"name": "Tiếng Việt", "dir": "ltr",
        "title": "Noophorics — đo lường sự truyền đạt hiểu biết",
        "lede": "Hai trí óc nhận cùng một bài toán. Một bên giải thích cho bên kia. Cả hai đều đồng ý rằng lời giải thích đã đến nơi. Không ai đo phần đã mất.",
        "move": "Hiểu biết được đo bằng sự hội tụ hành vi hướng tới một tham chiếu đã tuyên bố: B hiểu điều A hiểu tới mức các quyết định của B tiến gần tham chiếu ấy, luôn xét theo một độ đo thăm dò đã tuyên bố.",
        "phi": "Đồng thuận ảo (Φ): cả hai bên tin rằng hiểu biết đã được truyền; các phép thăm dò nói ngược lại. Bệnh lý trung tâm của lĩnh vực này.",
        "status": "Phiên bản 0.5. Một kết quả đăng ký trước nay đã được xác lập, mười bốn tuyên bố của chính chúng tôi đã bị rút lại, và bốn thí nghiệm vô hiệu.",
        "skip": "Tới nội dung", "canon": "Văn bản chuẩn bằng tiếng Anh. Trang này là bản tóm tắt."},
    "fa": {"name": "فارسی", "dir": "rtl",
        "title": "Noophorics — سنجش انتقال فهم",
        "lede": "دو ذهن مسئله‌ای یکسان می‌گیرند. یکی برای دیگری توضیح می‌دهد. هر دو می‌پذیرند که توضیح رسیده است. هیچ‌کس آنچه را از دست رفته نمی‌سنجد.",
        "move": "فهم با هم‌گرایی رفتاری به سوی یک مرجعِ اعلام‌شده سنجیده می‌شود: B به همان اندازه آنچه را A می‌فهمد فهمیده است که تصمیم‌هایش به آن مرجع نزدیک شود، همواره نسبت به یک سنجهٔ کاوشِ اعلام‌شده.",
        "phi": "توافق موهوم (Φ): هر دو طرف باور دارند فهم منتقل شده است؛ کاوش‌ها خلاف آن را می‌گویند. آسیب‌شناسی مرکزی این حوزه.",
        "status": "نسخهٔ ۰٫۵. یک نتیجهٔ از پیش ثبت‌شده اکنون تثبیت شده است، چهارده ادعای خودمان پس گرفته شده و چهار آزمایش باطل است.",
        "skip": "پرش به محتوا", "canon": "متن مرجع به انگلیسی است. این صفحه یک خلاصه است."},
    "bn": {"name": "বাংলা", "dir": "ltr",
        "title": "Noophorics — বোঝাপড়ার সঞ্চালন মাপা",
        "lede": "দুটি মনকে একই সমস্যা দেওয়া হয়। একজন অন্যজনকে ব্যাখ্যা করে। দুজনেই মানে যে ব্যাখ্যাটি পৌঁছেছে। কী হারিয়ে গেল, তা কেউ মাপে না।",
        "move": "বোঝাপড়া মাপা হয় একটি ঘোষিত রেফারেন্সের দিকে আচরণগত অভিসারী হয়ে: ঘোষিত একটি প্রোব-পরিমাপের সাপেক্ষে B-র সিদ্ধান্ত সেই রেফারেন্সের যত কাছে যায়, A যা বোঝে তা B ততটাই বুঝেছে।",
        "phi": "ছায়া-ঐকমত্য (Φ): দুই পক্ষই বিশ্বাস করে বোঝাপড়া সঞ্চালিত হয়েছে; প্রোব বলে হয়নি। এই ক্ষেত্রের কেন্দ্রীয় ব্যাধি।",
        "status": "সংস্করণ ০.৫। পূর্ব-নিবন্ধিত একটি ফলাফল এখন প্রতিষ্ঠিত, আমাদের নিজেদের চোদ্দটি দাবি প্রত্যাহার করা হয়েছে, এবং চারটি পরীক্ষা বাতিল।",
        "skip": "বিষয়বস্তুতে যান", "canon": "মূল পাঠ্য ইংরেজিতে। এই পাতা একটি সারসংক্ষেপ।"},
    "nl": {"name": "Nederlands", "dir": "ltr",
        "title": "Noophorics — de overdracht van begrip meten",
        "lede": "Twee geesten krijgen hetzelfde probleem. De een legt het de ander uit. Beiden vinden dat de uitleg is aangekomen. Niemand meet wat verloren ging.",
        "move": "Begrip wordt gemeten als gedragsconvergentie naar een verklaarde referentie: B begreep wat A begrijpt voor zover B's beslissingen die referentie naderen, steeds ten opzichte van een verklaarde probemaat.",
        "phi": "Spookovereenstemming (Φ): beide partijen geloven dat begrip is overgedragen; de probes zeggen van niet. De centrale pathologie van dit vakgebied.",
        "status": "Versie 0.5. Eén vooraf geregistreerd resultaat staat nu vast, veertien van onze eigen beweringen zijn ingetrokken en vier experimenten zijn ongeldig.",
        "skip": "Naar de inhoud", "canon": "De canonieke tekst is Engels. Deze pagina is een samenvatting."},
    "uk": {"name": "Українська", "dir": "ltr",
        "title": "Ноофорика — вимірювання передачі розуміння",
        "lede": "Двом розумам дають одну задачу. Один пояснює її другому. Обидва згодні, що пояснення дійшло. Ніхто не вимірює, що загубилося.",
        "move": "Розуміння вимірюється поведінковим зближенням з оголошеним еталоном: B зрозумів тією мірою, якою рішення B наближаються до цього еталона, — завжди відносно оголошеної пробної міри.",
        "phi": "Фантомна згода (Φ): обидві сторони переконані, що розуміння передалося; проби кажуть протилежне. Центральна патологія поля.",
        "status": "Версія 0.5. Встановлено один попередньо зареєстрований результат, чотирнадцять наших власних тверджень відкликано, чотири експерименти визнано недійсними.",
        "skip": "Перейти до змісту", "canon": "Канонічний текст — англійський. Ця сторінка є стислим викладом."},
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
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{status}">
<meta name="twitter:image" content="https://noophorics.org/og.png">
<meta property="og:title" content="{title}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://noophorics.org/{lang}/">
<meta property="og:image" content="https://noophorics.org/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Noophorics — a dark card reading NOOPHORICS above the line “Understanding is measured by behavioural convergence toward a declared reference”, footed with Φ phantom agreement and the version.">
<meta property="og:description" content="{status}">
<script type="application/ld+json">{ld}</script>
<style>
:root{{
  color-scheme:light dark;
  --plate:#e7e8e3;
  --field:#ddded8;
  --ink:#12161a;
  --graphite:#5c6369;
  --rule:#c5c7c0;
  --rule-soft:#d5d6d0;
  --phantom:#a3291d;
  --phantom-wash:rgba(163,41,29,.11);
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Charter,
    "Bitstream Charter","Book Antiqua","Noto Serif",Georgia,serif;
  --mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,"DejaVu Sans Mono",
    "Liberation Mono",Consolas,monospace;
  --measure:40rem;
  --rail:9rem;
  --gutter:3rem;
}}
@media (prefers-color-scheme:dark){{
  :root{{
    --plate:#0f1317;
    --field:#161b20;
    --ink:#d7d9d4;
    --graphite:#8c9299;
    --rule:#262c32;
    --rule-soft:#1d2329;
    --phantom:#e0705f;
    --phantom-wash:rgba(224,112,95,.14);
  }}
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{
  min-width:18rem;
  margin:0;
  background:var(--plate);
  color:var(--ink);
  font-family:var(--serif);
  font-size:clamp(1rem,.96rem + .2vw,1.0625rem);
  line-height:1.62;
  -webkit-text-size-adjust:100%;
}}
p,h1{{margin:0;text-wrap:pretty}}
a{{
  color:inherit;
  text-decoration-color:var(--phantom);
  text-decoration-thickness:from-font;
  text-underline-offset:.2em;
}}
a:hover{{color:var(--phantom)}}
:focus-visible{{outline:2px solid var(--phantom);outline-offset:3px}}
.shell{{
  width:min(100%,calc(var(--rail) + var(--gutter) + var(--measure) + 3rem));
  margin-inline:auto;
  padding-inline:clamp(1.125rem,4vw,1.5rem);
}}
.skip{{
  position:absolute;
  inset-block-start:.5rem;
  inset-inline-start:-200vw;
  z-index:10;
  padding:.75rem 1rem;
  background:var(--phantom);
  color:var(--plate);
  font:600 .75rem/1 var(--mono);
  letter-spacing:.08em;
  text-decoration:none;
  text-transform:uppercase;
}}
.skip:focus{{inset-inline-start:.5rem}}
.masthead{{
  border-bottom:1px solid var(--rule);
  font:500 .6875rem/1.2 var(--mono);
  letter-spacing:.13em;
  text-transform:uppercase;
}}
.masthead .shell{{
  min-height:3.25rem;
  display:grid;
  grid-template-columns:auto 1fr auto;
  gap:.75rem 1.5rem;
  align-items:center;
}}
.mark,.programme-nav{{text-decoration:none}}
.mark{{color:var(--ink);letter-spacing:.16em}}
.edition{{color:var(--graphite);text-align:center}}
.programme-nav{{color:var(--graphite)}}
.programme-nav span{{color:var(--phantom)}}
.programme-nav:hover span{{color:inherit}}
.page{{
  display:grid;
  grid-template-columns:minmax(0,var(--rail)) minmax(0,var(--measure));
  gap:0 var(--gutter);
  padding-block:clamp(3.25rem,8vw,6.5rem) clamp(3.5rem,8vw,6rem);
}}
.rail{{
  grid-column:1;
  grid-row:1;
  padding-block-start:.55rem;
  color:var(--graphite);
  font:400 .625rem/1.65 var(--mono);
  letter-spacing:.14em;
  text-align:end;
  text-transform:uppercase;
}}
.rail strong{{
  display:block;
  color:var(--ink);
  font-weight:400;
}}
.rail .rail-phi{{
  display:block;
  margin-block-start:1.15rem;
  color:var(--phantom);
  font-size:2.5rem;
  line-height:1;
  letter-spacing:0;
}}
.content{{grid-column:2;min-width:0;overflow-wrap:anywhere}}
.stale{{
  margin-block-end:2rem;
  padding:.85rem 1rem;
  border:1px solid var(--phantom);
  background:var(--phantom-wash);
  color:var(--ink);
  font-size:.9375rem;
}}
.stale:empty{{display:none}}
.eyebrow{{
  margin-block-end:1.25rem;
  color:var(--graphite);
  font:400 .6875rem/1.5 var(--mono);
  letter-spacing:.16em;
  text-transform:uppercase;
}}
h1{{
  font-size:clamp(3rem,9vw,5.25rem);
  font-weight:400;
  line-height:.98;
  letter-spacing:.015em;
  text-transform:uppercase;
}}
.etym{{
  margin-block-start:1rem;
  color:var(--graphite);
  font:400 .8125rem/1.5 var(--mono);
  letter-spacing:.02em;
}}
.lede{{
  max-width:35rem;
  margin-block-start:clamp(2.25rem,6vw,3.25rem);
  font-size:clamp(1.2rem,2.8vw,1.45rem);
  line-height:1.43;
}}
.definition{{
  margin-block-start:clamp(2.25rem,6vw,3rem);
  padding-block-start:1.6rem;
  border-block-start:1px solid var(--rule);
  font-size:clamp(1.08rem,2.3vw,1.22rem);
  line-height:1.55;
}}
.phi{{
  display:grid;
  grid-template-columns:clamp(5.25rem,14vw,7rem) 1fr;
  margin-block:clamp(2.5rem,7vw,4rem);
  border-block:1px solid var(--phantom);
  background:var(--field);
}}
.phi-mark{{
  min-height:8.5rem;
  display:grid;
  place-items:center;
  border-inline-end:1px solid var(--phantom);
  background:var(--phantom-wash);
  color:var(--phantom);
  font:400 clamp(3.5rem,10vw,5.25rem)/1 var(--mono);
}}
.phi-copy{{
  align-self:center;
  padding:clamp(1.2rem,4vw,1.65rem);
  font-size:clamp(1.02rem,2.2vw,1.15rem);
  line-height:1.52;
}}
.status{{
  padding-block:1.25rem;
  border-block:1px solid var(--rule);
  color:var(--graphite);
  font-size:.9375rem;
}}
.canonical{{
  margin-block-start:2.25rem;
  padding:1.25rem;
  border:1px solid var(--rule);
  background:var(--field);
}}
.canonical p{{color:var(--graphite);font-size:.9375rem}}
.canonical-link{{
  min-height:2.75rem;
  margin-block-start:1rem;
  padding:.75rem 1rem;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:1.5rem;
  background:var(--ink);
  color:var(--plate);
  font:500 .75rem/1.3 var(--mono);
  letter-spacing:.1em;
  text-decoration:none;
  text-transform:uppercase;
}}
.canonical-link:hover{{background:var(--phantom);color:var(--plate)}}
.canonical-link .arrow{{font-size:1rem}}
.foot{{
  padding-block:0 2.5rem;
  border-top:1px solid var(--rule);
}}
.foot .shell{{
  display:grid;
  grid-template-columns:minmax(0,var(--rail)) minmax(0,var(--measure));
  gap:0 var(--gutter);
}}
.foot-inner{{grid-column:2;min-width:0;padding-block-start:1.5rem}}
.foot-meta{{
  display:flex;
  justify-content:space-between;
  gap:1rem;
  color:var(--graphite);
  font:400 .6875rem/1.5 var(--mono);
  letter-spacing:.1em;
  text-transform:uppercase;
}}
.foot-meta a{{min-height:2.75rem;display:inline-flex;align-items:center}}
.langs{{margin-block-start:1rem}}
.langs ul{{
  display:flex;
  flex-wrap:wrap;
  gap:.25rem .5rem;
  margin:0;
  padding:0;
  list-style:none;
}}
.langs a{{
  min-height:2.75rem;
  display:inline-flex;
  align-items:center;
  padding-inline:.6rem;
  border:1px solid transparent;
  color:var(--graphite);
  font-size:.875rem;
  white-space:nowrap;
}}
.langs a:hover{{border-color:var(--rule);color:var(--phantom)}}
.langs a[aria-current="page"]{{
  border-color:var(--phantom);
  color:var(--ink);
  text-decoration:none;
}}
@media (max-width:50rem){{
  .page{{grid-template-columns:minmax(0,1fr)}}
  .rail{{display:none}}
  .content{{grid-column:1}}
  .foot .shell{{grid-template-columns:minmax(0,1fr)}}
  .foot-inner{{grid-column:1}}
}}
@media (max-width:34rem){{
  .masthead .shell{{grid-template-columns:1fr auto}}
  .edition{{display:none}}
  .programme-nav{{text-align:end}}
  h1{{font-size:clamp(2.4rem,14vw,3rem)}}
  .phi{{grid-template-columns:4.5rem 1fr}}
  .phi-mark{{min-height:7.5rem;font-size:3.25rem}}
  .phi-copy{{padding:1rem}}
  .foot-meta{{align-items:flex-start;flex-direction:column;gap:0}}
}}
@media (prefers-reduced-motion:reduce){{
  html{{scroll-behavior:auto}}
}}
@media (forced-colors:active){{
  .phi,.canonical-link,.langs a[aria-current="page"]{{border:1px solid CanvasText}}
  .phi-mark{{border-inline-end:1px solid CanvasText}}
}}
@media print{{
  .skip,.masthead,.foot{{display:none}}
  .page{{display:block;max-width:var(--measure);padding-block:2rem}}
  .canonical-link{{border:1px solid var(--ink)}}
}}
</style>
</head>
<body>
<a class="skip" href="#content">{skip}</a>
<header class="masthead">
  <div class="shell">
    <a class="mark" href="/" dir="ltr">Noophorics</a>
    <span class="edition"><bdi>{name}</bdi> / v0.4</span>
    <a class="programme-nav" href="/" dir="ltr">Canonical programme <span aria-hidden="true">→</span></a>
  </div>
</header>
<main class="page shell" id="content" tabindex="-1">
  <aside class="rail" aria-hidden="true" dir="ltr">
    Condensed summary
    <strong>{lang} / v0.4</strong>
    <span class="rail-phi">Φ</span>
  </aside>
  <article class="content" aria-labelledby="page-title">
    <p class="stale" role="status">{stale}</p>
    <p class="eyebrow" dir="ltr">{lang} / condensed summary / v0.4</p>
    <h1 id="page-title" dir="ltr">Noophorics</h1>
    <p class="etym" dir="ltr">νόος + φορά</p>
    <p class="lede">{lede}</p>
    <p class="definition">{move}</p>
    <aside class="phi" aria-label="Φ">
      <div class="phi-mark" aria-hidden="true">Φ</div>
      <p class="phi-copy">{phi}</p>
    </aside>
    <p class="status">{status}</p>
    <section class="canonical" aria-label="Canonical programme">
      <p>{canon}</p>
      <a class="canonical-link" href="/" dir="ltr">
        <span>English (canonical)</span>
        <span class="arrow" aria-hidden="true">↗</span>
      </a>
    </section>
  </article>
</main>
<footer class="foot">
  <div class="shell">
    <div class="foot-inner">
      <div class="foot-meta">
        <span><bdi>Noophorics</bdi> / <bdi>{name}</bdi></span>
        <a href="https://github.com/vyakymenko/noophorics" dir="ltr">GitHub <span aria-hidden="true">↗</span></a>
      </div>
      <nav class="langs" aria-label="Language">
        <ul>{langnav}</ul>
      </nav>
    </div>
  </div>
</footer>
</body>
</html>
"""


def rewrite_canonical_language_lists() -> None:
    """The canonical page's hreflang block and language menu, from `T`.

    Both were hand-maintained, and adding eight languages left both listing
    eleven -- the new pages existed, were in the sitemap, and were invisible to
    a search engine and to a reader looking for their own language. This is the
    sitemap lesson again: two writers of one list is a race the later writer
    always wins, and here the later writer was nobody, so the list simply
    stopped being true.

    Only the marked regions are touched, so the four watched passages -- and
    therefore `source_fingerprint()` -- are untouched by construction.
    """
    import re

    with open(CANON, "r", encoding="utf-8") as fh:
        html = fh.read()

    alts = "\n".join(
        '<link rel="alternate" hreflang="%s" href="https://noophorics.org/%s/">'
        % (l, l) for l in sorted(T))
    alts += ('\n<link rel="alternate" hreflang="x-default" '
             'href="https://noophorics.org/">')
    links = "\n".join(
        '              <a href="/%s/" hreflang="%s">%s</a>' % (l, l, T[l]["name"])
        for l in sorted(T))

    new, n1 = re.subn(
        r"<!-- i18n:alternates -->.*?<!-- /i18n:alternates -->",
        "<!-- i18n:alternates -->\n%s\n<!-- /i18n:alternates -->" % alts,
        html, flags=re.S)
    new, n2 = re.subn(
        r"<!-- i18n:menu -->.*?<!-- /i18n:menu -->",
        "<!-- i18n:menu -->\n%s\n              <!-- /i18n:menu -->" % links,
        new, flags=re.S)
    if not (n1 and n2):
        raise SystemExit(
            "canonical page is missing the i18n markers (alternates=%d menu=%d). "
            "Without them these lists go back to being hand-maintained, which "
            "is how they came to list eleven of nineteen languages." % (n1, n2))
    if new != html:
        with open(CANON, "w", encoding="utf-8") as fh:
            fh.write(new)
        print("  canonical page: %d hreflang + %d menu links" % (len(T) + 1, len(T)))


def build(check_only: bool = False) -> int:
    fingerprint = source_fingerprint()
    if not check_only:
        rewrite_canonical_language_lists()
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

    hreflang = "\n".join(
        '<link rel="alternate" hreflang="%s" href="https://noophorics.org/%s/">' % (l, l)
        for l in sorted(T)
    )

    for lang, s in sorted(T.items()):
        langnav = (
            '<li><a href="/" lang="en" dir="ltr" hreflang="en">English</a></li>'
            + "".join(
                '<li><a href="/%s/" lang="%s" dir="%s" hreflang="%s"%s>%s</a></li>'
                % (
                    code,
                    code,
                    T[code]["dir"],
                    code,
                    ' aria-current="page"' if code == lang else "",
                    T[code]["name"],
                )
                for code in sorted(T)
            )
        )
        out_dir = os.path.join(DOCS, lang)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
            # Schema.org for a translated summary. It has to say two things a
            # bare WebPage cannot: which language it is in, and that it is a
            # translation of the canonical English article rather than a
            # separate work. Without translationOfWork nineteen pages carrying
            # the same claims in different words look like nineteen documents
            # making them independently.
            ld = json.dumps({
                "@context": "https://schema.org",
                "@type": "WebPage",
                "@id": "https://noophorics.org/%s/#page" % lang,
                "url": "https://noophorics.org/%s/" % lang,
                "name": s["title"],
                "description": s["status"],
                "inLanguage": lang,
                "isPartOf": {"@id": "https://noophorics.org/#website"},
                "translationOfWork": {"@id": "https://noophorics.org/#programme"},
                "license": "https://creativecommons.org/licenses/by/4.0/",
                "publisher": {"@type": "Organization", "name": "Noophorics",
                              "url": "https://noophorics.org/"},
                "isAccessibleForFree": True,
            }, ensure_ascii=False, separators=(",", ":"))
            fh.write(PAGE.format(
                lang=lang, dir=s["dir"], name=s["name"], title=s["title"], lede=s["lede"],
                move=s["move"], phi=s["phi"], status=s["status"], canon=s["canon"],
                hreflang=hreflang, langnav=langnav, stale="", ld=ld,
                skip=s.get("skip", "Skip to content"),
            ))
        manifest[lang] = {"source_fingerprint": fingerprint, "name": s["name"]}

    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False, sort_keys=True)

    # Sitemap covering EVERY route that exists on disk, not only the languages.
    #
    # This function is the single writer. It used to emit languages only, while
    # the journal routes were added by hand elsewhere -- so every translation
    # build silently deleted twelve URLs, and the deletion was invisible because
    # the sitemap was checked right after it was hand-written and never after
    # the build. Two writers of one file is a race the later writer always wins.
    #
    # lastmod comes from the file's own mtime rather than a literal, because a
    # hard-coded date is a claim about freshness that nothing checks.
    import datetime

    def _mtime(rel: str) -> str:
        path = os.path.join(DOCS, rel)
        ts = os.path.getmtime(path) if os.path.exists(path) else time.time()
        return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")

    routes = [("", "index.html")]
    routes += [(l + "/", os.path.join(l, "index.html")) for l in sorted(T)]
    if os.path.exists(os.path.join(DOCS, "wiki", "index.html")):
        routes.append(("wiki/", os.path.join("wiki", "index.html")))
    journal = os.path.join(DOCS, "journal")
    if os.path.isdir(journal):
        routes.append(("journal/", os.path.join("journal", "index.html")))
        routes += [("journal/%s/" % d, os.path.join("journal", d, "index.html"))
                   for d in sorted(os.listdir(journal))
                   if os.path.isdir(os.path.join(journal, d))]
    with open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for route, src in routes:
            fh.write("  <url><loc>https://noophorics.org/%s</loc>"
                     "<lastmod>%s</lastmod></url>\n" % (route, _mtime(src)))
        fh.write("</urlset>\n")
    print("  sitemap: %d routes" % len(routes))

    print("built %d translations against source %s" % (len(T), fingerprint))
    return 0


if __name__ == "__main__":
    raise SystemExit(build(check_only="--check" in sys.argv))
