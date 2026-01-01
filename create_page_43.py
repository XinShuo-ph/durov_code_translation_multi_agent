import json

page_content = {
  "page": 43,
  "chapter": 3,
  "chapter_title": "Глава 3",
  "sentences": [
    {
      "id": 1,
      "ru": "...предложили купить базу данных, от которой я, разумеется, отказался.",
      "en": "...offered to buy the database, which I, of course, refused.",
      "zh": "……提议购买数据库，我当然拒绝了。",
      "ja": "……データベースの購入を持ちかけられましたが、もちろん私は断りました。"
    },
    {
      "id": 2,
      "ru": "Но я отказался, а кто-то согласится.",
      "en": "But I refused, and someone else might agree.",
      "zh": "但我拒绝了，而别人可能会同意。",
      "ja": "しかし私は断りましたが、誰かが同意するかもしれません。"
    },
    {
      "id": 3,
      "ru": "Почему предложили мне – я один из создателей проекта ВКонтакте.ру.",
      "en": "Why they offered it to me – I am one of the creators of the VKontakte.ru project.",
      "zh": "为什么向我提议——我是VKontakte.ru项目的创始人之一。",
      "ja": "なぜ私に持ちかけられたのか――私はVKontakte.ruプロジェクトの創設者の一人だからです。"
    },
    {
      "id": 4,
      "ru": "Этот сайт, как и moifakultet, является клоном американского сайта facebook.com, однако мы создаем наш, российский сайт со своей спецификой и рядом функций.",
      "en": "This site, like moifakultet, is a clone of the American site facebook.com; however, we are creating our own, Russian site with its own specifics and a range of functions.",
      "zh": "这个网站，就像moifakultet一样，是美国网站facebook.com的克隆版，但我们正在创建一个具有自己特色和一系列功能的、我们自己的俄罗斯网站。",
      "ja": "このサイトは、moifakultetと同様にアメリカのサイトfacebook.comのクローンですが、私たちは独自の仕様と一連の機能を備えた、私たち自身のロシアのサイトを作成しています。"
    },
    {
      "id": 5,
      "ru": "Если вас заинтересовал moifakultet, но вам не нравятся баги, слабая функциональность, корявость в альтернативных браузерах и т. д., я советую использовать ВКонтакте.ру.",
      "en": "If you were interested in moifakultet, but you don't like bugs, weak functionality, clumsiness in alternative browsers, etc., I advise using VKontakte.ru.",
      "zh": "如果您对moifakultet感兴趣，但不喜欢它的漏洞、功能薄弱、在非主流浏览器中显示糟糕等问题，我建议您使用VKontakte.ru。",
      "ja": "もしmoifakultetに興味を持たれたものの、バグや機能の弱さ、代替ブラウザでの表示の崩れなどが気に入らない場合は、VKontakte.ruを使用することをお勧めします。"
    },
    {
      "id": 6,
      "ru": "Друзья, если вы посмотрите сайт и согласитесь, что vkontakte.ru – проект более серьезный и профессиональный, прошу пригласить туда друзей и предупредить их о том, о чем я рассказал.",
      "en": "Friends, if you look at the site and agree that vkontakte.ru is a more serious and professional project, I ask you to invite friends there and warn them about what I have told.",
      "zh": "朋友们，如果您浏览了网站并认同vkontakte.ru是一个更严肃、更专业的项目，请邀请朋友加入，并把这里发生的事情告诉他们。",
      "ja": "友人の皆さん、もしサイトを見て、vkontakte.ruがより真剣でプロフェッショナルなプロジェクトであることに同意していただけるなら、そこに友人を招待し、私が話したことについて彼らに警告してください。"
    },
    {
      "id": 7,
      "ru": "Для всех нас очень важна ваша поддержка – без нее проект и все наши старания бессмысленны.",
      "en": "For all of us, your support is very important – without it, the project and all our efforts are meaningless.",
      "zh": "你们的支持对我们大家都很重要——没有它，这个项目和我们要付出的一切努力都毫无意义。",
      "ja": "私たち全員にとって、皆さんのサポートは非常に重要です。それがなければ、プロジェクトも私たちのすべての努力も無意味です。"
    },
    {
      "id": 8,
      "ru": "Пожалуйста, напишите, что вы думаете об этом.",
      "en": "Please write what you think about this.",
      "zh": "请写下您的看法。",
      "ja": "これについてどう思うか書いてください。"
    },
    {
      "id": 9,
      "ru": "Автор: durov 4.12.2006, 7:44",
      "en": "Author: durov 4.12.2006, 7:44",
      "zh": "作者：durov 2006年12月4日，7:44",
      "ja": "投稿者：durov 2006年12月4日 7:44"
    },
    {
      "id": 10,
      "ru": "UPDATE!",
      "en": "UPDATE!",
      "zh": "更新！",
      "ja": "UPDATE!"
    },
    {
      "id": 11,
      "ru": "Только что мне рассказали, что администратор сайта moifakultet.ru теперь обвиняет нас в том, что мы его якобы злостно взломали.",
      "en": "I was just told that the administrator of the moifakultet.ru site is now accusing us of allegedly maliciously hacking him.",
      "zh": "刚才有人告诉我，moifakultet.ru网站的管理员现在指责我们，声称我们恶意入侵了他们。",
      "ja": "たった今聞いたのですが、moifakultet.ruサイトの管理者が、私たちが彼らを悪意を持ってハッキングしたとして非難しているそうです。"
    },
    {
      "id": 12,
      "ru": "Приехали, называется…",
      "en": "Here we go, as they say...",
      "zh": "这叫什么事儿啊……",
      "ja": "やれやれ、と言ったところですね……"
    },
    {
      "id": 13,
      "ru": "Мы сотрудничаем с серьезной командой по информационной безопасности, которая с нами работала некоторое время, – они не занимаются нелегалом.",
      "en": "We cooperate with a serious information security team that has worked with us for some time – they do not engage in illegal activities.",
      "zh": "我们与一个严肃的信息安全团队合作，他们已经与我们共事了一段时间——他们不从事非法活动。",
      "ja": "私たちは、以前から協力関係にある真面目な情報セキュリティチームと連携しており、彼らは違法行為には関与していません。"
    },
    {
      "id": 14,
      "ru": "Как оказалось, moifakultet взломали хакеры, которые как-то узнали о работе над параллельными проектами и решили «через них» подзаработать.",
      "en": "As it turned out, moifakultet was hacked by hackers who somehow found out about the work on parallel projects and decided to earn some extra money 'through them'.",
      "zh": "事实证明，moifakultet是被黑客入侵的，这些黑客不知怎么知道了我们在做类似的并行项目，决定“通过这些”赚点外快。",
      "ja": "判明したところによると、moifakultetをハッキングしたのは、並行して進められているプロジェクトについてどこかで聞きつけたハッカーたちで、彼らは「それらを通じて」小遣い稼ぎをしようとしたようです。"
    },
    {
      "id": 15,
      "ru": "Продать дыры одного сайта владельцу другого и наоборот.",
      "en": "To sell the holes of one site to the owner of another and vice versa.",
      "zh": "把一个网站的漏洞卖给另一个网站的所有者，反之亦然。",
      "ja": "あるサイトの脆弱性を別のサイトの所有者に売り、その逆もまた然り、というわけです。"
    },
    {
      "id": 16,
      "ru": "Они связались через нашу команду со мной и предложили купить БД незадачливого конкурента.",
      "en": "They contacted me through our team and offered to buy the DB of the unlucky competitor.",
      "zh": "他们通过我们的团队联系我，提议购买那个倒霉竞争对手的数据库。",
      "ja": "彼らは私たちのチームを通じて私に連絡を取り、不運な競合相手のDB（データベース）を買わないかと持ちかけました。"
    },
    {
      "id": 17,
      "ru": "Не получилось – нам это просто не надо.",
      "en": "It didn't work out – we simply don't need it.",
      "zh": "没谈成——我们根本不需要它。",
      "ja": "うまくいきませんでした――私たちには単にそれが必要ないからです。"
    },
    {
      "id": 18,
      "ru": "Не уверен, что та сторона была бы настолько же великодушна, но я хакеров послал.",
      "en": "I'm not sure that the other side would be as magnanimous, but I told the hackers to get lost.",
      "zh": "我不确定对方是否会同样宽宏大量，但我把黑客打发走了。",
      "ja": "向こう側が同じくらい寛大であったかどうかはわかりませんが、私はハッカーたちを追い払いました。"
    },
    {
      "id": 19,
      "ru": "А теперь в благодарность распространяются байки про то, что «они нас взломали».",
      "en": "And now, in gratitude, tall tales are being spread that 'they hacked us'.",
      "zh": "现在作为“回报”，关于“他们黑了我们”的谣言正在四处传播。",
      "ja": "それなのに今、感謝されるどころか、「彼らが私たちをハッキングした」という作り話が広められています。"
    },
    {
      "id": 20,
      "ru": "Автор: Данила 4.12.2006, 12:58",
      "en": "Author: Danila 4.12.2006, 12:58",
      "zh": "作者：Danila 2006年12月4日，12:58",
      "ja": "投稿者：ダニラ 2006年12月4日 12:58"
    },
    {
      "id": 21,
      "ru": "Новый проект Павла и Николая Дуровых стартует с криминальной хакерской атаки и плагиата!",
      "en": "The new project of Pavel and Nikolai Durov starts with a criminal hacker attack and plagiarism!",
      "zh": "帕维尔和尼古拉·杜罗夫的新项目以犯罪黑客攻击和剽窃作为开端！",
      "ja": "パーヴェルとニコライ・ドゥーロフの新しいプロジェクトは、犯罪的なハッカー攻撃と盗作から始まっている！"
    },
    {
      "id": 22,
      "ru": "КРИМИНАЛ. Наш сайт (MoiFakultet.ru) 01.12.06 подвергся криминальной хакерской атаке со стороны команды Павла Дурова.",
      "en": "CRIME. Our site (MoiFakultet.ru) was subjected to a criminal hacker attack by Pavel Durov's team on 01.12.06.",
      "zh": "犯罪行为。我们的网站（MoiFakultet.ru）于06年12月1日遭受了来自帕维尔·杜罗夫团队的犯罪黑客攻击。",
      "ja": "犯罪。当サイト（MoiFakultet.ru）は、06年12月1日、パーヴェル・ドゥーロフのチームによる犯罪的なハッカー攻撃を受けた。"
    },
    {
      "id": 23,
      "ru": "Документальное свидетельство (заказ на взлом сайта) смотрите в Яндекс-блогах:",
      "en": "See the documentary evidence (order for site hacking) in Yandex-blogs:",
      "zh": "请在Yandex博客中查看书面证据（入侵网站的订单）：",
      "ja": "証拠文書（サイトハッキングの依頼）はYandexブログを参照のこと："
    },
    {
      "id": 24,
      "ru": "http://blogs.yandex.ru/search.xml?how=tm&rd=2&text=moifakultet.ru",
      "en": "http://blogs.yandex.ru/search.xml?how=tm&rd=2&text=moifakultet.ru",
      "zh": "http://blogs.yandex.ru/search.xml?how=tm&rd=2&text=moifakultet.ru",
      "ja": "http://blogs.yandex.ru/search.xml?how=tm&rd=2&text=moifakultet.ru"
    },
    {
      "id": 25,
      "ru": "[сейчас ничего криминального по этой ссылке найти невозможно. – Н. К.].",
      "en": "[It is impossible to find anything criminal at this link now. – N. K.]",
      "zh": "[现在在这个链接下找不到任何犯罪证据。——N. K.]",
      "ja": "[現在、このリンク先には犯罪的なものは何も見つからない。――N. K.]"
    },
    {
      "id": 26,
      "ru": "Вот цитата текста объявления Павла или его подручного: «Большая просьба проверить два сайта на уязвимость: _vkontakte.ru и moifakultet.ru",
      "en": "Here is a quote from the text of the announcement by Pavel or his henchman: 'Big request to check two sites for vulnerability: _vkontakte.ru and moifakultet.ru",
      "zh": "这是帕维尔或其手下发布的公告原文引用：“恳请检查两个网站的漏洞：_vkontakte.ru 和 moifakultet.ru",
      "ja": "以下は、パーヴェルまたはその手下が投稿した告知文の引用である：「2つのサイトの脆弱性をチェックしてくれるよう強く頼む：_vkontakte.ru と moifakultet.ru"
    },
    {
      "id": 27,
      "ru": "Если найдете во втором сайте серьезные дырки, с меня $. Заранее спасибо».",
      "en": "If you find serious holes in the second site, the $ is on me. Thanks in advance.'",
      "zh": "如果在第二个网站中发现严重漏洞，我给钱。先谢了。”",
      "ja": "2つ目のサイトに深刻な穴を見つけたら、金は払う。よろしく頼む」。"
    },
    {
      "id": 28,
      "ru": "После этого, 01.12.06, наш сайт был взломан и прекратил работать на 1 сутки…",
      "en": "After this, on 01.12.06, our site was hacked and stopped working for 1 day...",
      "zh": "此后，在06年12月1日，我们的网站被黑客入侵并停止运行了一天……",
      "ja": "この後、06年12月1日、当サイトはハッキングされ、1日間停止した……"
    },
    {
      "id": 29,
      "ru": "Возможно, часть мейлов был похищена и будет в дальнейшем использована для увеличения аудитории сайта вконтакте.ру.",
      "en": "Possibly, part of the emails was stolen and will be used in the future to increase the audience of the site vkontakte.ru.",
      "zh": "部分邮件地址可能被窃取，将来会被用于增加vkontakte.ru网站的受众。",
      "ja": "おそらくメールの一部が盗まれ、今後vkontakte.ruサイトのオーディエンスを増やすために使われるだろう。"
    },
    {
      "id": 30,
      "ru": "ПЛАГИАТ. До хакерской атаки Павел с братом отличились тем, что оперативно скопировали наш сайт.",
      "en": "PLAGIARISM. Before the hacker attack, Pavel and his brother distinguished themselves by promptly copying our site.",
      "zh": "剽窃。在黑客攻击之前，帕维尔和他的兄弟就因迅速复制我们的网站而“声名大噪”。",
      "ja": "盗作。ハッカー攻撃の前、パーヴェルと兄は、当サイトを迅速にコピーしたことで名を馳せた。"
    },
    {
      "id": 31,
      "ru": "Убедиться в этом также просто: достаточно посмотреть на дату регистрации нашего сайта:",
      "en": "It is also simple to verify this: it is enough to look at the registration date of our site:",
      "zh": "验证这一点也很简单：只要看看我们网站的注册日期：",
      "ja": "これを確認するのも簡単だ。当サイトの登録日を見れば十分だ："
    },
    {
      "id": 32,
      "ru": "(domain: MOIFAKULTET.RU, created: 2006.08.14) и на дату регистрации",
      "en": "(domain: MOIFAKULTET.RU, created: 2006.08.14) and at the registration date",
      "zh": "(domain: MOIFAKULTET.RU, created: 2006.08.14) 以及注册日期",
      "ja": "(domain: MOIFAKULTET.RU, created: 2006.08.14) そして登録日"
    }
  ],
  "translator_notes": [
    "This page contains historical forum posts from 2006 documenting the conflict between VKontakte and MoiFakultet.ru.",
    "Durov openly admits VK is a clone of Facebook but positions it as a superior Russian version.",
    "The text captures the 'wild west' era of the early Russian internet (RuNet), with accusations of hacking and plagiarism.",
    "Danila is likely the administrator of MoiFakultet.ru.",
    "N. K. in brackets refers to the author Nikolai Kononov adding a contemporary note."
  ],
  "total_sentences": 32,
  "page_type": "narrative"
}

with open("translations/page_043.json", "w", encoding="utf-8") as f:
    json.dump(page_content, f, indent=2, ensure_ascii=False)
