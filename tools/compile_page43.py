#!/usr/bin/env python3
"""Create page 43 demo translation."""

import sys
sys.path.insert(0, '/workspace/tools')
from compile_pages import compile_demo_page

# Page 43 sample sentences - VK vs moifakultet controversy
sample_sentences = [
    {
        "id": 1,
        "ru": "Мне предложили купить базу данных, от которой я, разумеется, отказался. Но я отказался, а кто-то согласится.",
        "en": "I was offered to buy the database, which I naturally refused. But I refused, and someone else might agree.",
        "zh": "有人提出卖给我一个数据库，我当然拒绝了。但我拒绝了，不代表别人也会拒绝。",
        "ja": "データベースを購入するよう提案されたが、当然断った。しかし、私は断ったが、誰かは同意するかもしれない。"
    },
    {
        "id": 2,
        "ru": "Этот сайт, как и moifakultet, является клоном американского сайта facebook.com, однако мы создаем наш, российский сайт со своей спецификой и рядом функций.",
        "en": "This site, like moifakultet, is a clone of the American site facebook.com, but we are creating our own Russian site with its own specifics and features.",
        "zh": "这个网站和moifakultet一样，都是美国网站facebook.com的克隆版，但我们正在创建我们自己的俄罗斯网站，有自己的特色和功能。",
        "ja": "このサイトはmoifakultetと同様、アメリカのサイトfacebook.comのクローンだが、私たちは独自の特徴と機能を持つロシアのサイトを作っている。"
    },
    {
        "id": 3,
        "ru": "Друзья, если вы посмотрите сайт и согласитесь, что vkontakte.ru – проект более серьезный и профессиональный, прошу пригласить туда друзей.",
        "en": "Friends, if you look at the site and agree that vkontakte.ru is a more serious and professional project, please invite your friends there.",
        "zh": "朋友们，如果你们看了网站并同意vkontakte.ru是一个更认真、更专业的项目，请邀请你们的朋友加入。",
        "ja": "友人の皆さん、サイトを見てvkontakte.ruがより真剣でプロフェッショナルなプロジェクトだと思ったら、友人を招待してください。"
    },
    {
        "id": 4,
        "ru": "Только что мне рассказали, что администратор сайта moifakultet.ru теперь обвиняет нас в том, что мы его якобы злостно взломали.",
        "en": "I was just told that the administrator of moifakultet.ru is now accusing us of allegedly maliciously hacking them.",
        "zh": "刚才有人告诉我，moifakultet.ru的管理员现在指控我们恶意入侵了他们的网站。",
        "ja": "moifakultet.ruの管理者が、私たちが悪意を持ってハッキングしたと非難していると今知らされた。"
    },
]

if __name__ == "__main__":
    result = compile_demo_page(43, sample_sentences)
    print(f"Created: {result}")
