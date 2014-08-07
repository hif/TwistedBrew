import HTMLParser
import yaml

BREW_NAME_NODE = "F_R_NAME"
BREW_BREWER_NODE = "F_R_BREWER"
BREW_STYLE_NODE = "F_R_STYLE"
BREW_STYLE_NAME_NODE = "F_S_NAME"
BREW_STYLE_CATEGORY_NODE = "F_S_CATEGORY"
BREW_STYLE_DESCRIPTION_NODE = "F_S_DESCRIPTION"
BREW_STYLE_PROFILE_NODE = "F_S_PROFILE"
BREW_STYLE_INGREDIENTS_NODE = "F_S_INGREDIENTS"
BREW_STYLE_WEB_NODE = "F_S_WEB_LINK"

__brew_html_parser__ = HTMLParser.HTMLParser()


class Brew():
    def __init__(self, data):
        self.name = recipename(data)
        self.brewer = lookupinfo(data, BREW_BREWER_NODE)
        self.style = lookupstyleinfo(data, BREW_STYLE_NAME_NODE)
        self.category = lookupstyleinfo(data, BREW_STYLE_CATEGORY_NODE)
        self.description = lookupstyleinfo(data, BREW_STYLE_DESCRIPTION_NODE)
        self.profile = lookupstyleinfo(data, BREW_STYLE_PROFILE_NODE)
        self.ingredients = lookupstyleinfo(data, BREW_STYLE_INGREDIENTS_NODE)
        self.weblink = lookupstyleinfo(data, BREW_STYLE_WEB_NODE)

    def __str__(self):
        return yaml.dump(self)


def lookupinfo(data, key):
    if data.data.__contains__(key):
        return __brew_html_parser__.unescape(data.data[key])
    return None


def recipename(data):
    return lookupinfo(data, BREW_NAME_NODE)


def lookupstyleinfo(data, key):
    if not data.children.__contains__(BREW_STYLE_NODE):
        return None
    style = data.children[BREW_STYLE_NODE]
    if style.data.__contains__(key):
        return __brew_html_parser__.unescape(style.data[key])
    return None