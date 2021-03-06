﻿import re
from typing import Callable, Dict, List  # noqa: F401

FormatText = Callable[[str], str]

ascii: str = (''' !"#$%&'()*+,-./'''
              '0123456789'
              ':;<=>?@'
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
              r'[\]^_`'
              'abcdefghijklmnopqrstuvwxyz'
              '{|}~')
upper: str = (''' !"#$%&'()*+,-./'''
              '0123456789'
              ':;<=>?@'
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
              r'[\]^_`'
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
              '{|}~')
lower: str = (''' !"#$%&'()*+,-./'''
              '0123456789'
              ':;<=>?@'
              'abcdefghijklmnopqrstuvwxyz'
              r'[\]^_`'
              'abcdefghijklmnopqrstuvwxyz'
              '{|}~')
full: str = ('''　！＂＃＄％＆＇（）＊＋，ー．／'''
             '０１２３４５６７８９'
             '：；〈＝〉？＠'
             'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
             '［＼］＾＿｀'
             'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
             '｛｜｝～')
parenthesized: str = (''' !"#$%&'()*+,-./'''
                      '0⑴⑵⑶⑷⑸⑹⑺⑻⑼'
                      ':;<=>?@'
                      '⒜⒝⒞⒟⒠⒡⒢⒣⒤⒥⒦⒧⒨⒩⒪⒫⒬⒭⒮⒯⒰⒱⒲⒳⒴⒵'
                      r'[\]^_`'
                      '⒜⒝⒞⒟⒠⒡⒢⒣⒤⒥⒦⒧⒨⒩⒪⒫⒬⒭⒮⒯⒰⒱⒲⒳⒴⒵'
                      '{|}~')
circled: str = (''' !"#$%&'()*+,-./'''
                '⓪①②③④⑤⑥⑦⑧⑨'
                ':;<=>?@'
                'ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ'
                '[\\]^_`'
                'ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ'
                '{|}~')
smallcaps: str = (''' !"#$%&'()*+,-./'''
                  '0123456789'
                  ':;<=>?@'
                  'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴩQʀsᴛᴜᴠᴡxYᴢ'
                  r'[\]^_`'
                  'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴩqʀsᴛᴜᴠᴡxyᴢ'
                  '{|}~')
upsidedown: str = (''' ¡"#$%⅋,()*+‘-./'''
                   '0123456789'
                   ':;<=>¿@'
                   'ɐqɔpǝɟƃɥıɾʞןɯuodbɹsʇnʌʍxʎz'
                   r'[\]^_`'
                   'ɐqɔpǝɟƃɥıɾʞןɯuodbɹsʇnʌʍxʎz'
                   '{|}~')
serifBold: str = (''' !"#$%&'()*+,-./'''
                  '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
                  ':;<=>?@'
                  '𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙'
                  r'[\]^_`'
                  '𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳'
                  '{|}~')
serifItalic: str = (''' !"#$%&'()*+,-./'''
                    '0123456789'
                    ':;<=>?@'
                    '𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍'
                    r'[\]^_`'
                    '𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧'
                    '{|}~')
serifBoldItalic: str = (''' !"#$%&'()*+,-./'''
                        '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
                        ':;<=>?@'
                        '𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁'
                        r'[\]^_`'
                        '𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛'
                        '{|}~')
sanSerif: str = (''' !"#$%&'()*+,-./'''
                 '𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫'
                 ':;<=>?@'
                 '𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹'
                 r'[\]^_`'
                 '𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓'
                 '{|}~')
sanSerifBold: str = (''' !"#$%&'()*+,-./'''
                     '𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵'
                     ':;<=>?@'
                     '𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭'
                     r'[\]^_`'
                     '𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇'
                     '{|}~')
sanSerifItalic: str = (''' !"#$%&'()*+,-./'''
                       '𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫'
                       ':;<=>?@'
                       '𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡'
                       r'[\]^_`'
                       '𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻'
                       '{|}~')
sanSerifBoldItalic: str = (''' !"#$%&'()*+,-./'''
                           '𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵'
                           ':;<=>?@'
                           '𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕'
                           r'[\]^_`'
                           '𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯'
                           '{|}~')
script: str = (''' !"#$%&'()*+,-./'''
               '0123456789'
               ':;<=>?@'
               '𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵'
               r'[\]^_`'
               '𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏'
               '{|}~')
scriptBold: str = (''' !"#$%&'()*+,-./'''
                   '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
                   ':;<=>?@'
                   '𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩'
                   r'[\]^_`'
                   '𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃'
                   '{|}~')
fraktur: str = (''' !"#$%&'()*+,-./'''
                '0123456789'
                ':;<=>?@'
                '𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ'
                r'[\]^_`'
                '𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷'
                '{|}~')
frakturBold: str = (''' !"#$%&'()*+,-./'''
                    '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
                    ':;<=>?@'
                    '𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅'
                    r'[\]^_`'
                    '𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟'
                    '{|}~')
monospace: str = (''' !"#$%&'()*+,-./'''
                  '𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿'
                  ':;<=>?@'
                  '𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉'
                  r'[\]^_`'
                  '𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣'
                  '{|}~')
doubleStruck: str = (''' !"#$%&'()*+,-./'''
                     '𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡'
                     ':;<=>?@'
                     '𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ'
                     r'[\]^_`'
                     '𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫'
                     '{|}~')


def _createAsciiTo(name: str,
                   toTable: str) -> FormatText:
    table = str.maketrans(ascii, toTable)

    def asciiTo(text: str) -> str:
        return text.translate(table)
    asciiTo.__name__ = name
    return asciiTo


to_upper: FormatText = _createAsciiTo('to_upper', upper)
to_lower: FormatText = _createAsciiTo('to_lower', lower)
to_full_width: FormatText = _createAsciiTo('to_full_width', full)
to_parenthesized: FormatText = _createAsciiTo(
    'to_parenthesized', parenthesized)
to_circled: FormatText = _createAsciiTo('to_circled', circled)
to_small_caps: FormatText = _createAsciiTo('to_small_caps', smallcaps)
_to_upside_down_reversed: FormatText = _createAsciiTo(
    'to_upside_down', upsidedown)


def to_upside_down(text: str) -> str:
    return _to_upside_down_reversed(text)[::-1]


to_serif_bold: FormatText = _createAsciiTo('to_serif_bold', serifBold)
to_serif_italic: FormatText = _createAsciiTo('to_serif_italic', serifItalic)
to_serif_bold_italic: FormatText = _createAsciiTo(
    'to_serif_bold_italic', serifBoldItalic)
to_sanserif: FormatText = _createAsciiTo('to_sanserif', sanSerif)
to_sanserif_bold: FormatText = _createAsciiTo('to_sanserif_bold', sanSerifBold)
to_sanserif_italic: FormatText = _createAsciiTo(
    'to_sanserif_italic', sanSerifItalic)
to_sanserif_bold_italic: FormatText = _createAsciiTo(
    'to_sanserif_bold_italic', sanSerifBoldItalic)
to_script: FormatText = _createAsciiTo('to_script', script)
to_script_bold: FormatText = _createAsciiTo('to_script_bold', scriptBold)
to_fraktur: FormatText = _createAsciiTo('to_fraktur', fraktur)
to_fraktur_bold: FormatText = _createAsciiTo('to_fraktur_bold', frakturBold)
to_monospace: FormatText = _createAsciiTo('to_monospace', monospace)
to_double_struck: FormatText = _createAsciiTo('to_double_struck', doubleStruck)


def to_ascii(text: str) -> str:
    fromTable: List[str]
    fromTable = [full, parenthesized, circled, smallcaps, upsidedown,
                 serifBold, serifItalic, serifBoldItalic, sanSerif,
                 sanSerifBold, sanSerifItalic, sanSerifBoldItalic, script,
                 scriptBold, fraktur, frakturBold, monospace, doubleStruck,
                 ascii]
    toTable: Dict[int, int] = {}
    for table in fromTable:
        toTable.update(str.maketrans(table, ascii))
    return text.translate(toTable)


def format(string: str,
           format_: str) -> str:
    format_ = format_.lower()
    strTable: Dict[str, FormatText] = {
        'ascii': to_ascii,
        'upper': to_upper,
        'lower': to_lower,
        'full': to_full_width,
        'parenthesized': to_parenthesized,
        'circled': to_circled,
        'smallcaps': to_small_caps,
        'upsidedown': to_upside_down,
        'sanserif': to_sanserif,
        'script': to_script,
        'cursive': to_script,
        'fraktur': to_fraktur,
        'monospace': to_monospace,
        'doublestruck': to_double_struck,
        }
    reTable: Dict[str, FormatText] = {
        r'serif-?bold': to_serif_bold,
        r'serif-?italic': to_serif_italic,
        r'serif-?(bold-?italic|italic-?bold)': to_serif_bold_italic,
        r'(sanserif-?)?bold': to_sanserif_bold,
        r'(sanserif-?)?italic': to_sanserif_italic,
        r'(sanserif-?)?(bold-?italic|italic-?bold)': to_sanserif_bold_italic,
        r'(script|cursive)-?bold': to_script_bold,
        r'fraktur-?bold': to_fraktur_bold,
        }
    if format_ in strTable:
        return strTable[format_](string)
    pattern: str
    for pattern in reTable:
        if re.fullmatch(pattern, format_):
            return reTable[pattern](string)
    return string
