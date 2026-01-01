#!/usr/bin/env python3
"""Create page 8 translation JSON file."""

import json

page_data = {
    "page": 8,
    "chapter": "Пролог / Prologue",
    "translator_id": "e545",
    "sentences": [
        {
            "id": 1,
            "ru": "Черт возьми, я думал, что мы работаем с инновационной компанией, а вы торгуетесь, как на базаре, – чеканил тип.",
            "en": "Damn it, I thought we were working with an innovative company, but you're haggling like at a bazaar, the guy hammered out.",
            "zh": "该死的，我以为我们在和一家创新公司合作，结果你们像在菜市场讨价还价，这家伙一字一顿地说。",
            "ja": "くそ、革新的な会社と仕事をしていると思っていたのに、市場で値切るようなことをしている、と男は声を張り上げた。"
        },
        {
            "id": 2,
            "ru": "Мы создаем новое, совершенное средство коммуникации, а вы… что вы тут вообще устраиваете?!",
            "en": "We are creating a new, perfect means of communication, and you... what are you even doing here?!",
            "zh": "我们正在创造一种新的、完美的通讯工具，而你们……你们在这里搞什么鬼？！",
            "ja": "私たちは新しい、完璧なコミュニケーション手段を作っているのに、あなたたちは……ここで一体何をしているんだ？！"
        },
        {
            "id": 3,
            "ru": "Иностранец лихорадочно соображал, как себя вести: исполнитель роли attack dog сидел совсем не там, где он предполагал, и напал неожиданно.",
            "en": "The foreigner was frantically figuring out how to behave: the one playing the attack dog role was sitting in a completely different place than he had expected, and had attacked unexpectedly.",
            "zh": "外国人手忙脚乱地思考该如何应对：扮演攻击犬角色的人根本不在他预想的位置上，而且发起了出其不意的攻击。",
            "ja": "外国人は必死にどう振る舞うべきか考えていた：アタックドッグ役を演じていたのは彼が想定していた人物とは全く別の場所にいて、不意に攻撃してきた。"
        },
        {
            "id": 4,
            "ru": "Ему говорили, что плохого следователя играет стриженый очкарик, а этот, якобы гениальный программист, всегда вежлив.",
            "en": "He had been told that the bad cop was played by the short-haired guy in glasses, and that this one, the supposedly genius programmer, was always polite.",
            "zh": "有人告诉他，扮演坏警察角色的是那个戴眼镜的短发男，而这位所谓的天才程序员一向彬彬有礼。",
            "ja": "彼は、悪役刑事役は短髪の眼鏡男が演じ、この天才プログラマーと言われている男はいつも礼儀正しいと聞いていた。"
        },
        {
            "id": 5,
            "ru": "Хотя чего думать, надо успокаивать чертова неврастеника, пока не сбежал.",
            "en": "But why think about it - he needed to calm down this damn neurotic before he ran off.",
            "zh": "但想那么多干嘛，得在这个该死的神经质跑掉之前安抚他。",
            "ja": "でも考えている場合じゃない、この神経質なやつが逃げ出す前に落ち着かせなければ。"
        },
        {
            "id": 6,
            "ru": "Подождите, Павел, – экспат примиряюще развел руками. – Я прекрасно вас понимаю и ценю ваш продукт, вы работаете на переднем крае технологий…",
            "en": "Wait, Pavel, the expat spread his hands in a conciliatory gesture. I understand you perfectly and appreciate your product, you are working on the cutting edge of technology...",
            "zh": "等等，帕维尔，外派高管调解地摊开双手。我完全理解你，也欣赏你们的产品，你们正处于技术前沿……",
            "ja": "待ってください、パーヴェル、と外国人は和解的に手を広げた。あなたのことはよく理解していますし、製品も高く評価しています。技術の最前線で仕事をされている……"
        },
        {
            "id": 7,
            "ru": "Продолжал он, краем глаза фиксируя, что гений вернулся на стул, сбросил бейсболку, быстрым движением пригладил черные волосы и водрузил кепку обратно.",
            "en": "He continued, catching out of the corner of his eye that the genius had returned to his chair, tossed off his baseball cap, quickly smoothed his black hair, and put the cap back on.",
            "zh": "他继续说道，余光瞥见那个天才已经回到椅子上，摘下棒球帽，快速抚平黑发，又把帽子戴了回去。",
            "ja": "彼は続けながら、目の端で天才が椅子に戻り、野球帽を脱いで、素早く黒い髪を整え、また帽子をかぶったのを捉えた。"
        },
        {
            "id": 8,
            "ru": "Удивительно, что за два часа у этого человека несколько раз тасовались, как карты, личности.",
            "en": "Amazingly, over two hours, this person's personalities had shuffled like cards several times.",
            "zh": "令人惊讶的是，两个小时内，这个人的人格像洗牌一样变换了好几次。",
            "ja": "驚くべきことに、この2時間で、この人物の人格はトランプのように何度もシャッフルされていた。"
        },
        {
            "id": 9,
            "ru": "Первая – подросток, глядящий черными глазами куда-то вбок, растерянный; подбирает слова; неестественность, выпирающие углы жестов, то плавных, то стремительных, выдают тлеющее внутри безумие.",
            "en": "The first - a teenager, looking somewhere to the side with black eyes, confused; choosing words; the unnaturalness, the protruding angles of gestures, now smooth, now swift, betray the madness smoldering inside.",
            "zh": "第一种——一个少年，黑色的眼睛望向一边，一副茫然的样子；在斟酌用词；那不自然的感觉，时而流畅时而迅猛的手势中突兀的棱角，暴露了内心深处燃烧的疯狂。",
            "ja": "一つ目は、黒い目でどこか横を見ている困惑した少年。言葉を選んでいる。不自然さ、時に滑らかで時に素早いジェスチャーの突き出た角が、内に燻っている狂気を裏切っている。"
        },
        {
            "id": 10,
            "ru": "Вторая – нагловатый бизнесмен.",
            "en": "The second - a somewhat impudent businessman.",
            "zh": "第二种——一个有点傲慢的商人。",
            "ja": "二つ目は、やや厚かましいビジネスマン。"
        },
        {
            "id": 11,
            "ru": "Третья – интеллигент, с лету разбирающийся в проблеме и способах ее решения.",
            "en": "The third - an intellectual, immediately grasping the problem and ways to solve it.",
            "zh": "第三种——一个知识分子，能即刻理解问题并找到解决方案。",
            "ja": "三つ目は、問題とその解決方法を即座に理解するインテリ。"
        },
        {
            "id": 12,
            "ru": "Об этом человеке говорили, что выше всего он ценит кодеров, а остальных людей в компании считает вторым сортом.",
            "en": "About this person, it was said that he valued coders above all else, and considered everyone else in the company second-rate.",
            "zh": "据说这个人最看重程序员，把公司里其他人都当作二等公民。",
            "ja": "この人物について言われていたのは、コーダーを何よりも重視し、会社の他の人間は二流だと考えているということだった。"
        },
        {
            "id": 13,
            "ru": "Впрочем, много что рассказывали про его социальную сеть.",
            "en": "However, many things were said about his social network.",
            "zh": "不过，关于他的社交网络有很多传闻。",
            "ja": "もっとも、彼のソーシャルネットワークについては多くのことが語られていた。"
        },
        {
            "id": 14,
            "ru": "Что нигде нет программистов такого класса, чтобы тридцать человек поддерживали сложную архитектуру серверов и присутствие десятков миллионов юзеров.",
            "en": "That nowhere else are there programmers of such a class that thirty people support complex server architecture and the presence of tens of millions of users.",
            "zh": "据说没有哪里能找到这种级别的程序员，三十个人就能维护复杂的服务器架构和数千万用户的访问。",
            "ja": "こんなレベルのプログラマーは他にはいない、30人で複雑なサーバーアーキテクチャと数千万ユーザーの存在を支えている、と。"
        },
        {
            "id": 15,
            "ru": "Что ВКонтакте создали масоны. Или, наоборот, чекисты, а Павел Дуров – выдуманный персонаж.",
            "en": "That VKontakte was created by Masons. Or, on the contrary, by secret police agents, and Pavel Durov is a fictional character.",
            "zh": "有人说VKontakte是共济会创建的。或者相反，是克格勃创建的，而帕维尔·杜罗夫是个虚构人物。",
            "ja": "VKontakteはフリーメイソンが作った、とか。あるいは逆に、秘密警察が作り、パーヴェル・ドゥーロフは架空の人物だ、とか。"
        },
        {
            "id": 16,
            "ru": "Экспат взял себя в руки, отбросил иррациональную симпатию, которую вызывал нахальный противник, и аргументировал: наша компания тоже высокотехнологичная, но бизнес-резоны одинаковы для любой отрасли.",
            "en": "The expat pulled himself together, threw off the irrational sympathy that the impudent opponent evoked, and argued: our company is also high-tech, but business reasons are the same for any industry.",
            "zh": "外派高管稳住了自己，抛开对这个无礼对手产生的非理性好感，开始辩论：我们公司也是高科技企业，但商业逻辑对任何行业都是一样的。",
            "ja": "外国人は気を取り直し、この生意気な相手が引き起こす非合理的な好感を振り払い、議論した：我々の会社もハイテクだが、ビジネスの論理はどの業界でも同じだ。"
        },
        {
            "id": 17,
            "ru": "Переговорщик кивал. Буря эго стихла. Можно повторить насчет 5 %.",
            "en": "The negotiator nodded. The ego storm had subsided. He could repeat about the 5%.",
            "zh": "谈判者点点头。自尊风暴平息了。可以再提5%的事了。",
            "ja": "交渉人は頷いた。エゴの嵐は収まった。5%の話を繰り返せるかもしれない。"
        },
        {
            "id": 18,
            "ru": "Но Дуров опять подскочил: Вы считаете, будто мы набиваем себе цену. Вы просто тратите наше время.",
            "en": "But Durov jumped up again: You think we're just trying to drive up our price. You're just wasting our time.",
            "zh": "但杜罗夫又跳了起来：你以为我们只是在抬高身价。你只是在浪费我们的时间。",
            "ja": "しかしドゥーロフはまた飛び上がった：あなたは私たちが値段を吊り上げていると思っている。あなたは私たちの時間を無駄にしているだけだ。"
        },
        {
            "id": 19,
            "ru": "Два часа я слушаю вас, хотя мы могли бы договориться и запустить эксперимент. Хватит!",
            "en": "For two hours I've been listening to you, when we could have come to an agreement and launched the experiment. Enough!",
            "zh": "我听你说了两个小时，本来我们早就可以达成协议、启动实验了。够了！",
            "ja": "2時間もあなたの話を聞いているが、合意して実験を始められたはずだ。もう十分だ！"
        },
        {
            "id": 20,
            "ru": "И опять направился к двери.",
            "en": "And again headed for the door.",
            "zh": "然后又朝门口走去。",
            "ja": "そしてまたドアに向かった。"
        },
        {
            "id": 21,
            "ru": "В мозгу экспата столкнулись и заискрили несколько соображений.",
            "en": "In the expat's brain, several considerations collided and sparked.",
            "zh": "外派高管的脑海里几个想法碰撞在一起，擦出火花。",
            "ja": "外国人の頭の中で、いくつかの考えがぶつかり合い、火花を散らした。"
        },
        {
            "id": 22,
            "ru": "Эксперимент по-любому выгоден, а если безумец оборвет переговоры, то более сговорчивые конкуренты быстро заключат с ним контракт.",
            "en": "The experiment is profitable anyway, and if the madman breaks off negotiations, more cooperative competitors will quickly sign a contract with him.",
            "zh": "实验无论如何都有利可图，如果这个疯子中断谈判，更配合的竞争对手会很快和他签约。",
            "ja": "実験はどちらにせよ有益だし、この狂人が交渉を打ち切れば、より協調的な競合がすぐに契約を結ぶだろう。"
        },
        {
            "id": 23,
            "ru": "Проклятые программисты, возомнили о себе черт знает что.",
            "en": "Damn programmers, they think they're god knows what.",
            "zh": "该死的程序员，自以为了不起。",
            "ja": "忌まわしいプログラマーども、自分を何様だと思っているんだ。"
        },
        {
            "id": 24,
            "ru": "А как отреагируют на объяснения о разрыве договоренности насчет сделки мои акционеры?",
            "en": "And how will my shareholders react to explanations about the deal falling through?",
            "zh": "我的股东们听到交易破裂的解释会怎么反应？",
            "ja": "そして私の株主たちは、取引破綻の説明にどう反応するだろうか？"
        },
        {
            "id": 25,
            "ru": "Павел, подождите! – закричал экспат устремившейся к дверям фигуре в черном.",
            "en": "Pavel, wait! the expat shouted at the figure in black heading for the doors.",
            "zh": "帕维尔，等等！外派高管对着那个冲向门口的黑衣身影喊道。",
            "ja": "パーヴェル、待って！外国人はドアに向かう黒い姿に叫んだ。"
        },
        {
            "id": 26,
            "ru": "У меня есть предложение, я согласен, вы правы!",
            "en": "I have a proposal, I agree, you're right!",
            "zh": "我有个提议，我同意，你是对的！",
            "ja": "提案がある、同意する、あなたは正しい！"
        },
        {
            "id": 27,
            "ru": "Мы сейчас разгорячились, а это вредно для бизнеса.",
            "en": "We've gotten heated right now, and that's bad for business.",
            "zh": "我们现在太激动了，这对生意不利。",
            "ja": "今私たちは熱くなっている、それはビジネスに悪い。"
        },
        {
            "id": 28,
            "ru": "Предлагаю договориться в общих чертах, а конкретизировать условия приглашаю вас, Илью и Андрея в мое шале в Швейцарии.",
            "en": "I propose we agree on the general terms, and to specify the conditions I invite you, Ilya and Andrey to my chalet in Switzerland.",
            "zh": "我建议我们先达成总体协议，具体条款的话，我邀请你、伊利亚和安德烈去我在瑞士的别墅商谈。",
            "ja": "大まかな条件で合意することを提案する。詳細を詰めるために、あなた、イリヤ、アンドレイを私のスイスのシャレーに招待する。"
        },
        {
            "id": 29,
            "ru": "Встреча, отдых – все на мне. Мы спокойно посидим…",
            "en": "Meeting, relaxation - all on me. We'll sit calmly...",
            "zh": "会面、休息——全算我的。我们可以轻松地坐下来……",
            "ja": "ミーティング、休暇——すべて私持ちだ。落ち着いて座って……"
        },
        {
            "id": 30,
            "ru": "Экспат прервался, потому что увидел, как переговорщик смеется.",
            "en": "The expat broke off because he saw the negotiator laughing.",
            "zh": "外派高管停了下来，因为他看到谈判者在笑。",
            "ja": "外国人は言葉を止めた、交渉人が笑っているのを見たからだ。"
        },
        {
            "id": 31,
            "ru": "Программист тоже улыбался, а предводитель шайки молчал, внезапно успокоившись, будто и не бегал к двери.",
            "en": "The programmer was also smiling, and the gang leader was silent, suddenly calm, as if he hadn't been running to the door.",
            "zh": "程序员也在微笑，而这帮人的头目沉默着，突然平静下来，仿佛刚才从未冲向门口。",
            "ja": "プログラマーも微笑んでいて、このグループのリーダーは黙っていた、突然落ち着いて、まるでドアに向かって走っていなかったかのように。"
        },
        {
            "id": 32,
            "ru": "Наконец Дуров любопытно наклонил голову и произнес: А вы еще и коррупционер.",
            "en": "Finally Durov tilted his head curiously and said: And you're also corrupt.",
            "zh": "最后杜罗夫好奇地歪了歪头说道：原来你还是个腐败分子。",
            "ja": "ついにドゥーロフは興味深そうに首を傾げて言った：それにあなたは腐敗した人間でもあるんだな。"
        },
        {
            "id": 33,
            "ru": "Интересно. Мы из вашей Швейцарии два дня назад прилетели и полетим еще, когда захотим.",
            "en": "Interesting. We flew back from your Switzerland two days ago and will fly again whenever we want.",
            "zh": "有意思。我们两天前刚从你说的瑞士飞回来，想什么时候去就什么时候去。",
            "ja": "面白い。私たちは2日前にあなたのスイスから飛んで帰ってきたし、行きたい時にまた行く。"
        },
        {
            "id": 34,
            "ru": "Экспат вздохнул и быстро сказал: ОК, давайте зафиксируем ваши условия.",
            "en": "The expat sighed and quickly said: OK, let's lock in your terms.",
            "zh": "外派高管叹了口气，快速说道：好吧，按你们的条件来。",
            "ja": "外国人はため息をついて素早く言った：OK、あなたたちの条件で決めよう。"
        },
        {
            "id": 35,
            "ru": "Гостя проводили по ковровой дорожке до лифта, чья золоченая клетка наводила на мысль, что программисты сняли этаж у реликтового министерства.",
            "en": "The guest was escorted along a carpet runner to the elevator, whose gilded cage suggested that the programmers had rented a floor from some relic ministry.",
            "zh": "他们沿着地毯送客人到电梯，电梯那镀金的轿厢让人觉得程序员们租了某个遗留部委的一层楼。",
            "ja": "客はカーペットに沿ってエレベーターまで案内された。その金メッキの籠は、プログラマーたちが遺物のような省庁からフロアを借りたことを連想させた。"
        },
        {
            "id": 36,
            "ru": "Затем переговорщики прошли в залу с анфиладой кабинетов.",
            "en": "Then the negotiators walked into a hall with a suite of offices.",
            "zh": "然后谈判者们走进了一间有连排办公室的大厅。",
            "ja": "それから交渉人たちは一連のオフィスが並ぶホールに入った。"
        },
        {
            "id": 37,
            "ru": "Троица так громко хохотала и обсуждала окаменевшую физиономию иностранца, что на смех начали сходиться странные люди.",
            "en": "The trio laughed so loudly and discussed the foreigner's petrified face that strange people began to gather at the laughter.",
            "zh": "三人大声笑着讨论那个外国人僵住的表情，笑声引来了一些奇怪的人。",
            "ja": "3人は外国人の凍りついた表情について大声で笑いながら話していたので、笑い声を聞いて奇妙な人々が集まり始めた。"
        },
        {
            "id": 38,
            "ru": "Они выползали из кабинетов с магнитными досками, где литерами были набраны таблички...",
            "en": "They crawled out of offices with magnetic boards, where signs were spelled out in letters...",
            "zh": "他们从有磁性白板的办公室里爬出来，白板上用字母拼着标牌……",
            "ja": "彼らは磁気ボードのあるオフィスから這い出してきた、そこには文字で看板が綴られていた……"
        }
    ],
    "translator_notes": [
        "attack dog - aggressive negotiator (English term used in original)",
        "плохой следователь - bad cop (from good cop/bad cop routine)",
        "чекисты - Chekists, reference to FSB/KGB secret police",
        "масоны - Freemasons (conspiracy theory reference)",
        "шале - chalet (Swiss vacation home)",
        "Revelation of Durov's multiple 'personalities' during negotiations"
    ],
    "research_used": [
        "VK negotiation tactics",
        "Russian conspiracy theories about tech companies",
        "Singer Building elevator description"
    ]
}

with open('/workspace/translations/raw/page_008.json', 'w', encoding='utf-8') as f:
    json.dump(page_data, f, ensure_ascii=False, indent=2)

print("Page 8 JSON created successfully")
