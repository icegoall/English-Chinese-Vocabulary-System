"""
Vocabulary library for middle-school English vocabulary system.
Contains 45 built-in vocabulary entries suitable for Chinese middle-school students.
Each entry includes: English word, Chinese meaning, part of speech,
example sentence, Chinese example translation, and optional confusable-word group.
"""

# Confusable-word groups: words that look similar and are easily confused.
# Each group is a list of words that students commonly mix up.
CONFUSABLE_GROUPS = {
    "accept_except": ["accept", "except"],
    "affect_effect": ["affect", "effect"],
    "quite_quiet": ["quite", "quiet"],
    "through_though": ["through", "though"],
    "their_there": ["their", "there"],
    "piece_peace": ["piece", "peace"],
    "advice_advise": ["advice", "advise"],
    "principal_principle": ["principal", "principle"],
    "desert_dessert": ["desert", "dessert"],
}

# The main vocabulary list. Each entry is a dict with keys:
#   word        — English word (str)
#   meaning     — Chinese meaning (str)
#   pos         — Part of speech (str), e.g. "v.", "n.", "adj."
#   example     — English example sentence (str)
#   example_cn  — Chinese translation of the example (str)
#   confusable  — List of all words in the same confusable group (list[str]),
#                 or an empty list if the word has no known confusable partners.
VOCABULARY = [
    # --- Common verbs ---
    {
        "word": "abandon", "meaning": "放弃；抛弃", "pos": "v.",
        "example": "He had to abandon his plan due to lack of money.",
        "example_cn": "由于缺钱，他不得不放弃他的计划。",
        "confusable": [],
    },
    {
        "word": "benefit", "meaning": "益处；利益", "pos": "n./v.",
        "example": "Regular exercise benefits your health.",
        "example_cn": "经常锻炼有益于你的健康。",
        "confusable": [],
    },
    {
        "word": "capable", "meaning": "有能力的", "pos": "adj.",
        "example": "She is capable of solving this problem.",
        "example_cn": "她有能力解决这个问题。",
        "confusable": [],
    },
    {
        "word": "determine", "meaning": "决定；确定", "pos": "v.",
        "example": "Hard work determines your success.",
        "example_cn": "努力决定了你的成功。",
        "confusable": [],
    },
    {
        "word": "eager", "meaning": "渴望的", "pos": "adj.",
        "example": "The students are eager to learn English.",
        "example_cn": "学生们渴望学习英语。",
        "confusable": [],
    },
    {
        "word": "factor", "meaning": "因素", "pos": "n.",
        "example": "Weather is an important factor in farming.",
        "example_cn": "天气是农业中一个重要的因素。",
        "confusable": [],
    },
    {
        "word": "gain", "meaning": "获得；增加", "pos": "v./n.",
        "example": "You can gain knowledge by reading books.",
        "example_cn": "你可以通过读书获得知识。",
        "confusable": [],
    },
    {
        "word": "handle", "meaning": "处理；把手", "pos": "v./n.",
        "example": "Can you handle this situation?",
        "example_cn": "你能处理这种情况吗？",
        "confusable": [],
    },
    {
        "word": "improve", "meaning": "改善；提高", "pos": "v.",
        "example": "I want to improve my English speaking skills.",
        "example_cn": "我想提高我的英语口语能力。",
        "confusable": [],
    },
    {
        "word": "justify", "meaning": "证明…是正当的", "pos": "v.",
        "example": "How can you justify your behavior?",
        "example_cn": "你怎样证明你的行为是正当的？",
        "confusable": [],
    },
    {
        "word": "knowledge", "meaning": "知识；学问", "pos": "n.",
        "example": "Knowledge is power.",
        "example_cn": "知识就是力量。",
        "confusable": [],
    },
    {
        "word": "maintain", "meaning": "维持；保养", "pos": "v.",
        "example": "We must maintain peace in the world.",
        "example_cn": "我们必须维持世界和平。",
        "confusable": [],
    },
    {
        "word": "necessary", "meaning": "必要的", "pos": "adj.",
        "example": "Water is necessary for life.",
        "example_cn": "水是生命所必需的。",
        "confusable": [],
    },
    {
        "word": "obtain", "meaning": "获得；得到", "pos": "v.",
        "example": "You can obtain a license at the office.",
        "example_cn": "你可以在办公室获得许可证。",
        "confusable": [],
    },
    {
        "word": "prevent", "meaning": "阻止；预防", "pos": "v.",
        "example": "Washing hands can prevent disease.",
        "example_cn": "洗手可以预防疾病。",
        "confusable": [],
    },
    {
        "word": "require", "meaning": "要求；需要", "pos": "v.",
        "example": "This task requires patience.",
        "example_cn": "这项任务需要耐心。",
        "confusable": [],
    },
    {
        "word": "solve", "meaning": "解决", "pos": "v.",
        "example": "Let's solve this math problem together.",
        "example_cn": "让我们一起解决这道数学题。",
        "confusable": [],
    },
    {
        "word": "achieve", "meaning": "实现；达到", "pos": "v.",
        "example": "She achieved her goal through hard work.",
        "example_cn": "她通过努力实现了自己的目标。",
        "confusable": [],
    },
    {
        "word": "develop", "meaning": "发展；开发", "pos": "v.",
        "example": "Reading helps develop your mind.",
        "example_cn": "阅读有助于发展你的思维。",
        "confusable": [],
    },
    # --- Nouns ---
    {
        "word": "quality", "meaning": "质量；品质", "pos": "n.",
        "example": "We care about the quality of our products.",
        "example_cn": "我们关心产品的质量。",
        "confusable": [],
    },
    {
        "word": "challenge", "meaning": "挑战", "pos": "n./v.",
        "example": "Learning a new language is a challenge.",
        "example_cn": "学习一门新语言是一个挑战。",
        "confusable": [],
    },
    {
        "word": "environment", "meaning": "环境", "pos": "n.",
        "example": "We should protect the environment.",
        "example_cn": "我们应该保护环境。",
        "confusable": [],
    },
    {
        "word": "future", "meaning": "未来", "pos": "n.",
        "example": "Study hard for your future.",
        "example_cn": "为了你的未来努力学习。",
        "confusable": [],
    },
    {
        "word": "generation", "meaning": "一代人", "pos": "n.",
        "example": "The younger generation loves technology.",
        "example_cn": "年轻一代热爱科技。",
        "confusable": [],
    },
    {
        "word": "balance", "meaning": "平衡", "pos": "n./v.",
        "example": "Try to keep a balance between work and rest.",
        "example_cn": "尽量保持工作和休息的平衡。",
        "confusable": [],
    },
    # --- Adjectives ---
    {
        "word": "typical", "meaning": "典型的", "pos": "adj.",
        "example": "This is a typical English breakfast.",
        "example_cn": "这是一顿典型的英式早餐。",
        "confusable": [],
    },
    {
        "word": "ancient", "meaning": "古代的", "pos": "adj.",
        "example": "The Great Wall is an ancient building.",
        "example_cn": "长城是一座古老的建筑。",
        "confusable": [],
    },
    {
        "word": "modern", "meaning": "现代的", "pos": "adj.",
        "example": "I prefer modern art.",
        "example_cn": "我更喜欢现代艺术。",
        "confusable": [],
    },
    {
        "word": "serious", "meaning": "严肃的；严重的", "pos": "adj.",
        "example": "This is a serious problem.",
        "example_cn": "这是一个严重的问题。",
        "confusable": [],
    },
    {
        "word": "various", "meaning": "各种各样的", "pos": "adj.",
        "example": "There are various ways to solve this.",
        "example_cn": "有各种各样的方法可以解决这个。",
        "confusable": [],
    },
    # --- Confusable word group: accept / except ---
    {
        "word": "accept", "meaning": "接受", "pos": "v.",
        "example": "I accept your invitation.",
        "example_cn": "我接受你的邀请。",
        "confusable": CONFUSABLE_GROUPS["accept_except"],
    },
    {
        "word": "except", "meaning": "除…之外", "pos": "prep.",
        "example": "Everyone went except Tom.",
        "example_cn": "除了汤姆，大家都去了。",
        "confusable": CONFUSABLE_GROUPS["accept_except"],
    },
    # --- Confusable word group: affect / effect ---
    {
        "word": "affect", "meaning": "影响", "pos": "v.",
        "example": "The weather affects our mood.",
        "example_cn": "天气影响我们的心情。",
        "confusable": CONFUSABLE_GROUPS["affect_effect"],
    },
    {
        "word": "effect", "meaning": "效果；影响", "pos": "n.",
        "example": "The medicine had a good effect.",
        "example_cn": "这种药效果很好。",
        "confusable": CONFUSABLE_GROUPS["affect_effect"],
    },
    # --- Confusable word group: quite / quiet ---
    {
        "word": "quite", "meaning": "相当；十分", "pos": "adv.",
        "example": "The test was quite difficult.",
        "example_cn": "考试相当难。",
        "confusable": CONFUSABLE_GROUPS["quite_quiet"],
    },
    {
        "word": "quiet", "meaning": "安静的", "pos": "adj.",
        "example": "Please keep quiet in the library.",
        "example_cn": "请在图书馆保持安静。",
        "confusable": CONFUSABLE_GROUPS["quite_quiet"],
    },
    # --- Confusable word group: through / though ---
    {
        "word": "through", "meaning": "穿过；通过", "pos": "prep.",
        "example": "We walked through the forest.",
        "example_cn": "我们穿过了森林。",
        "confusable": CONFUSABLE_GROUPS["through_though"],
    },
    {
        "word": "though", "meaning": "虽然", "pos": "conj.",
        "example": "Though it was late, he kept working.",
        "example_cn": "虽然很晚了，他还在工作。",
        "confusable": CONFUSABLE_GROUPS["through_though"],
    },
    # --- Confusable word group: their / there ---
    {
        "word": "their", "meaning": "他们的", "pos": "pron.",
        "example": "This is their classroom.",
        "example_cn": "这是他们的教室。",
        "confusable": CONFUSABLE_GROUPS["their_there"],
    },
    {
        "word": "there", "meaning": "那里", "pos": "adv.",
        "example": "The book is over there.",
        "example_cn": "书在那边。",
        "confusable": CONFUSABLE_GROUPS["their_there"],
    },
    # --- Confusable word group: piece / peace ---
    {
        "word": "piece", "meaning": "块；片", "pos": "n.",
        "example": "Can I have a piece of cake?",
        "example_cn": "我可以要一块蛋糕吗？",
        "confusable": CONFUSABLE_GROUPS["piece_peace"],
    },
    {
        "word": "peace", "meaning": "和平", "pos": "n.",
        "example": "Everyone hopes for peace.",
        "example_cn": "每个人都希望和平。",
        "confusable": CONFUSABLE_GROUPS["piece_peace"],
    },
    # --- Confusable word group: advice / advise ---
    {
        "word": "advice", "meaning": "建议（名词）", "pos": "n.",
        "example": "Thank you for your advice.",
        "example_cn": "谢谢你的建议。",
        "confusable": CONFUSABLE_GROUPS["advice_advise"],
    },
    {
        "word": "advise", "meaning": "劝告（动词）", "pos": "v.",
        "example": "I advise you to study hard.",
        "example_cn": "我劝你努力学习。",
        "confusable": CONFUSABLE_GROUPS["advice_advise"],
    },
    # --- Confusable word group: principal / principle ---
    {
        "word": "principal", "meaning": "校长；主要的", "pos": "n./adj.",
        "example": "The principal spoke to the students.",
        "example_cn": "校长对学生们讲话。",
        "confusable": CONFUSABLE_GROUPS["principal_principle"],
    },
    {
        "word": "principle", "meaning": "原则；原理", "pos": "n.",
        "example": "Honesty is an important principle.",
        "example_cn": "诚实是一个重要的原则。",
        "confusable": CONFUSABLE_GROUPS["principal_principle"],
    },
    # --- Confusable word group: desert / dessert ---
    {
        "word": "desert", "meaning": "沙漠", "pos": "n.",
        "example": "The camel lives in the desert.",
        "example_cn": "骆驼生活在沙漠中。",
        "confusable": CONFUSABLE_GROUPS["desert_dessert"],
    },
    {
        "word": "dessert", "meaning": "甜点", "pos": "n.",
        "example": "I want some dessert after dinner.",
        "example_cn": "晚饭后我想吃点甜点。",
        "confusable": CONFUSABLE_GROUPS["desert_dessert"],
    },
]


def get_all_words():
    """Return a copy of the full vocabulary list."""
    return [dict(w) for w in VOCABULARY]


def get_word_by_index(index):
    """Return the word at the given index, or None if out of range."""
    if 0 <= index < len(VOCABULARY):
        return dict(VOCABULARY[index])
    return None


def search_words(keyword):
    """
    Search vocabulary by English word or Chinese meaning.
    Returns a list of matching word dicts.
    """
    if not keyword:
        return get_all_words()
    kw = keyword.strip().lower()
    results = []
    for entry in VOCABULARY:
        if kw in entry["word"].lower() or kw in entry["meaning"]:
            results.append(dict(entry))
    return results


def get_word_by_word(word_text):
    """Look up a word entry by its English word (case-insensitive)."""
    target = word_text.strip().lower()
    for entry in VOCABULARY:
        if entry["word"].lower() == target:
            return dict(entry)
    return None


def get_confusable_words(word_text):
    """Return the list of confusable partner words for the given word."""
    entry = get_word_by_word(word_text)
    if entry and entry["confusable"]:
        # Return all words in the group except the word itself
        return [w for w in entry["confusable"] if w.lower() != word_text.strip().lower()]
    return []
