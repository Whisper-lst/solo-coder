from typing import Dict, List, Optional
import re


LANGUAGE_CODES = {
    "en": {"name": "English", "stop_words": ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "shall", "can", "need", "dare", "ought", "used", "this", "that", "these", "those", "it", "its", "as", "if", "when", "than", "because", "while", "although", "though", "since", "until", "unless", "so", "such", "too", "very", "more", "most", "less", "least", "few", "fewer", "fewest", "many", "more", "most", "much", "more", "most", "some", "any", "no", "none", "all", "both", "each", "every", "either", "neither", "other", "another", "such", "what", "which", "who", "whom", "whose", "where", "when", "why", "how"]},
    "zh": {"name": "中文", "stop_words": ["的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "她", "他", "它", "们", "这个", "那个", "什么", "怎么", "为什么", "哪", "哪里", "谁", "多少", "几", "啊", "吧", "呢", "吗", "呀", "哇", "哈", "啦", "哦", "嗯", "唉", "嘛", "呗", "罢了", "而已", "等等", "之类", "等等", "等等"]},
    "ja": {"name": "日本語", "stop_words": ["は", "が", "を", "に", "へ", "で", "と", "や", "から", "まで", "の", "より", "ほど", "だけ", "しか", "さえ", "こそ", "でも", "ばかり", "など", "やら", "なり", "か", "の", "よ", "ね", "さ", "ぜ", "ぞ", "わ", "な", "もの", "こと", "ところ", "わけ", "はず", "つもり", "ため", "せい", "おかげ", "うえ", "うち", "かわり", "ほか", "たび", "ごと", "うえで", "もとで", "なかで", "かたちで", "いっぽう", "かぎり", "ともなう", "つれて", "したがって", "ともに", "ひきかえ", "だけでなく", "のみならず", "上に", "その上", "さらに", "また", "そして", "しかも", "かつ", "および", "ならびに", "あるいは", "または", "もしくは", "ないしは", "では", "だが", "しかし", "けれども", "が", "のに", "くせに", "ても", "でも", "たとえても", "としても", "にしても", "にもかかわらず", "のに", "どころか", "ばかりか", "だけでなく", "なのに", "ものの", "ながらも", "とはいえ", "というものの", "とはいっても", "とはいえども"]},
    "fr": {"name": "Français", "stop_words": ["le", "la", "les", "de", "du", "des", "un", "une", "et", "ou", "mais", "donc", "car", "ni", "or", "que", "qui", "quoi", "où", "quand", "comment", "pourquoi", "combien", "quel", "quelle", "quels", "quelles", "ce", "cet", "cette", "ces", "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses", "notre", "nos", "votre", "vos", "leur", "leurs", "je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles", "me", "te", "le", "la", "les", "lui", "leur", "y", "en", "se", "soi", "à", "de", "en", "dans", "sur", "sous", "vers", "par", "pour", "sans", "avec", "chez", "entre", "sans", "pendant", "depuis", "jusqu'à", "avant", "après", "pendant", "durant", "tout", "toute", "tous", "toutes", "autre", "autres", "même", "mêmes", "tel", "telle", "tels", "telles", "beaucoup", "peu", "plus", "moins", "très", "trop", "assez", "si", "aussi", "non", "ne", "pas", "jamais", "toujours", "souvent", "parfois", "quelquefois", "rarement", "déjà", "encore", "bientôt", "tôt", "tard", "maintenant", "alors", "donc", "ainsi", "comme", "parce que", "puisque", "étant donné que", "vu que", "à cause de", "grâce à", "en raison de", "par suite de", "dû à"]},
    "de": {"name": "Deutsch", "stop_words": ["der", "die", "das", "die", "der", "des", "dem", "den", "ein", "eine", "einer", "einem", "einen", "eines", "und", "oder", "aber", "sondern", "denn", "weder", "noch", "entweder", "oder", "sowohl", "als", "auch", "nicht", "nur", "sondern", "auch", "da", "weil", "daher", "deshalb", "also", "folglich", "demzufolge", "dementsprechend", "dementsprechend", "dementsprechend", "wenn", "falls", "sofern", "falls", "falls", "während", "indem", "währenddem", "während", "indessen", "bis", "bevor", "nachdem", "sobald", "sowie", "sobald", "kaum", "dass", "obwohl", "obgleich", "obschon", "obzwar", "trotzdem", "dennoch", "doch", "jedoch", "hingegen", "dagegen", "zwar", "aber", "einerseits", "andererseits", "einerseits", "andererseits", "ich", "du", "er", "sie", "es", "wir", "ihr", "sie", "Sie", "mich", "dich", "ihn", "sie", "es", "uns", "euch", "sie", "Sie", "mir", "dir", "ihm", "ihr", "uns", "euch", "ihnen", "Ihnen", "mein", "meine", "meiner", "meinem", "meinen", "meines", "dein", "deine", "deiner", "deinem", "deinen", "deines", "sein", "seine", "seiner", "seinem", "seinen", "seines", "ihr", "ihre", "ihrer", "ihrem", "ihren", "ihres", "unser", "unsere", "unserer", "unserem", "unseren", "unseres", "euer", "eure", "eurer", "eurem", "euren", "eures", "ihr", "ihre", "ihrer", "ihrem", "ihren", "ihres", "Ihr", "Ihre", "Ihrer", "Ihrem", "Ihren", "Ihres", "dies", "dieses", "dieser", "diesem", "diese", "dieses", "dieser", "diesem", "diesen", "dieses", "jenes", "jener", "jenem", "jene", "jenes", "jener", "jenem", "jenen", "jenes", "solch", "solches", "solcher", "solchem", "solche", "solches", "solcher", "solchem", "solchen", "solches", "welch", "welches", "welcher", "welchem", "welche", "welches", "welcher", "welchem", "welchen", "welches", "was", "wer", "wen", "wem", "wessen", "welch", "welches", "welcher", "welchem", "welche", "welches", "welcher", "welchem", "welchen", "welches", "wo", "wohin", "woher", "wann", "wie", "warum", "weshalb", "wieso", "weswegen"]},
    "es": {"name": "Español", "stop_words": ["el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al", "a", "en", "por", "para", "con", "sin", "sobre", "bajo", "tras", "durante", "mientras", "antes", "después", "hasta", "desde", "entre", "sin", "y", "o", "pero", "mas", "sino", "que", "porque", "pues", "ya", "aunque", "mientras", "si", "cuando", "como", "porque", "pues", "ya", "aunque", "mientras", "si", "cuando", "como", "yo", "tu", "el", "ella", "usted", "nosotros", "nosotras", "vosotros", "vosotras", "ellos", "ellas", "ustedes", "me", "te", "se", "nos", "os", "le", "les", "lo", "la", "los", "las", "mi", "mis", "tu", "tus", "su", "sus", "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra", "vuestros", "vuestras", "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aquel", "aquella", "aquellos", "aquellas", "mismo", "misma", "mismos", "mismas", "otro", "otra", "otros", "otras", "alguno", "alguna", "algunos", "algunas", "ninguno", "ninguna", "ningunos", "ningunas", "mucho", "mucha", "muchos", "muchas", "poco", "poca", "pocos", "pocas", "demasiado", "demasiada", "demasiados", "demasiadas", "bastante", "bastantes", "todo", "toda", "todos", "todas", "cualquier", "cualquiera", "cualesquiera", "quien", "quienes", "que", "el", "la", "los", "las", "cual", "cuales", "cuyo", "cuya", "cuyos", "cuyas", "donde", "cuando", "como", "cuanto", "cuanta", "cuantos", "cuantas", "si", "no", "nunca", "jamás", "siempre", "todavía", "ya", "aún", "también", "tampoco", "así", "entonces", "por lo tanto", "por consiguiente", "de ahí", "en consecuencia"]}
}


def detect_language(text: str) -> str:
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', text))
    total_chars = len(text)
    
    if total_chars == 0:
        return "en"
    
    chinese_ratio = chinese_chars / total_chars
    japanese_ratio = japanese_chars / total_chars
    
    if chinese_ratio > 0.3:
        return "zh"
    if japanese_ratio > 0.2:
        return "ja"
    
    return "en"


def get_stop_words_for_language(language: str) -> List[str]:
    lang_data = LANGUAGE_CODES.get(language, LANGUAGE_CODES["en"])
    return lang_data.get("stop_words", [])


def get_language_name(language: str) -> str:
    lang_data = LANGUAGE_CODES.get(language, LANGUAGE_CODES["en"])
    return lang_data.get("name", "Unknown")


def get_supported_languages() -> Dict[str, str]:
    return {code: data["name"] for code, data in LANGUAGE_CODES.items()}
