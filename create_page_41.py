import json

page_content = {
  "page": 41,
  "chapter": 3,
  "chapter_title": "Глава 3",
  "sentences": [
    {
      "id": 1,
      "ru": "...одна идея – как прокормить семью или купить себе ранчо.",
      "en": "...one idea – how to feed a family or buy oneself a ranch.",
      "zh": "……一个想法——如何养家糊口或给自己买个牧场。",
      "ja": "……一つのアイデア――家族をどう養うか、あるいは自分の牧場を買うか。"
    },
    {
      "id": 2,
      "ru": "Это масштаб малого бизнеса – достойного, важного, социального.",
      "en": "This is the scale of small business – worthy, important, social.",
      "zh": "这是小企业的规模——体面、重要、具有社会意义。",
      "ja": "これは中小企業の規模だ――立派で、重要で、社会的な。"
    },
    {
      "id": 3,
      "ru": "Но не того, кто запускает проект, – тот не должен думать о том, сколько денег он „поднимет“; только о том, как он изменит мир.",
      "en": "But not for someone launching a project – he shouldn't think about how much money he will 'raise'; only about how he will change the world.",
      "zh": "但这不适合发起大项目的人——他不应考虑能“圈”多少钱；而只应考虑如何改变世界。",
      "ja": "しかし、プロジェクトを立ち上げる人にとっては違う――彼はいくら金を「調達」できるかなど考えるべきではない。世界をどう変えるか、それだけを考えるべきだ。"
    },
    {
      "id": 4,
      "ru": "И мир, возможно, ему потом заплатит».",
      "en": "And the world, possibly, will pay him later.'",
      "zh": "而世界，也许以后会回报他。’",
      "ja": "そうすれば、世界はおそらく、後で彼に報いるだろう』。"
    },
    {
      "id": 5,
      "ru": "Архитектора подмывало разом избавиться от житейских проблем, но ему хватило выдержки, и он предпочел стратегическую выгоду сиюминутной.",
      "en": "The Architect was tempted to get rid of life's problems at once, but he had enough restraint, and he preferred strategic advantage to momentary gain.",
      "zh": "这位“架构师”很想一下子摆脱生活琐事的困扰，但他有足够的定力，选择了战略利益而非眼前的一时之利。",
      "ja": "「建築家」（ドゥーロフ）は、生活の問題を一気に解決したいという衝動に駆られたが、彼には十分な自制心があり、目先の利益よりも戦略的な利益を選んだ。"
    },
    {
      "id": 6,
      "ru": "Дуров верил, что стоимость его сети будет исчисляться в миллионах долларов.",
      "en": "Durov believed that the value of his network would be calculated in millions of dollars.",
      "zh": "杜罗夫相信，他的网络的价值将以数百万美元计算。",
      "ja": "ドゥーロフは、自分のネットワークの価値が数百万ドル規模になると信じていた。"
    },
    {
      "id": 7,
      "ru": "Мысль о том, что он, архитектор и творец, станет бесправным менеджером для своего детища, казалась невыносимой.",
      "en": "The thought that he, the architect and creator, would become a powerless manager for his brainchild seemed unbearable.",
      "zh": "想到自己作为架构师和创造者，却要成为自己心血结晶的无权管理者，这似乎让他无法忍受。",
      "ja": "建築家であり創造者である自分が、自ら生み出したもののために権利のないマネージャーになるという考えは、耐え難いものに思えた。"
    },
    {
      "id": 8,
      "ru": "Друзья обговорили детали.",
      "en": "The friends discussed the details.",
      "zh": "朋友们商讨了细节。",
      "ja": "友人たちは詳細を話し合った。"
    },
    {
      "id": 9,
      "ru": "По 20 % – Дурову, Мирилашвили и Левиеву.",
      "en": "20% each to Durov, Mirilashvili, and Leviev.",
      "zh": "杜罗夫、米里拉什维利和列夫各占20%。",
      "ja": "ドゥーロフ、ミリラシヴィリ、レヴィエフにそれぞれ20％。"
    },
    {
      "id": 10,
      "ru": "40 % – Славиному деду, компании которого обеспечивали бэк-офис и тыл на случай приключений.",
      "en": "40% to Slava's grandfather, whose companies provided the back office and rear support in case of adventures.",
      "zh": "40%归斯拉瓦的祖父，他的公司提供后勤办公室和应对突发事件的后盾支持。",
      "ja": "40％はスラヴァの祖父へ。彼の会社はバックオフィスと、トラブルが起きたときのための後ろ盾を提供していた。"
    },
    {
      "id": 11,
      "ru": "Дуров – гендиректор с фактическим правом вето.",
      "en": "Durov – CEO with actual veto power.",
      "zh": "杜罗夫任总经理，拥有实际否决权。",
      "ja": "ドゥーロフは、事実上の拒否権を持つCEO（最高経営責任者）となる。"
    },
    {
      "id": 12,
      "ru": "Последнее пригодилось почти сразу.",
      "en": "The latter came in handy almost immediately.",
      "zh": "这一点几乎立刻就派上了用场。",
      "ja": "後者はすぐに役立つことになった。"
    },
    {
      "id": 13,
      "ru": "Управляя проектом, Дуров с самого начала блокировал различные идеи Славы и Льва, которые, например, хотели присоединить к соцсети интернет-магазины – коммерцию, создававшую cash flow.",
      "en": "Managing the project, Durov from the very beginning blocked various ideas of Slava and Lev, who, for example, wanted to attach online stores to the social network – commerce that created cash flow.",
      "zh": "在管理项目时，杜罗夫从一开始就否决了斯拉瓦和列夫的各种想法，例如他们想在社交网络中加入网店——这种能产生现金流的商业模式。",
      "ja": "プロジェクトを運営する中で、ドゥーロフは最初からスラヴァとレフの様々なアイデアをブロックした。例えば彼らは、キャッシュフローを生み出すビジネスとして、ソーシャルネットワークにオンラインストアを組み込みたがっていた。"
    },
    {
      "id": 14,
      "ru": "Хотя Перекопский, который был в курсе перемен, предложил привязать к соцсети рекрутинговый сервис ВКадре.ру и получил одобрение.",
      "en": "Although Perekopsky, who was aware of the changes, proposed linking the recruiting service VKadre.ru to the social network and received approval.",
      "zh": "尽管了解变局的佩列科普斯基（Perekopsky）提议将招聘服务VKadre.ru连接到社交网络并获得了批准。",
      "ja": "もっとも、変化を把握していたペレコプスキーが、リクルートサービスのVKadre.ruをソーシャルネットワークと連携させることを提案したときは、承認が得られたが。"
    },
    {
      "id": 15,
      "ru": "Через год Дуров пожалел об этом решении и уничтожил непопулярный сервис.",
      "en": "A year later, Durov regretted this decision and destroyed the unpopular service.",
      "zh": "一年后，杜罗夫后悔了这个决定，并关停了这个不受欢迎的服务。",
      "ja": "1年後、ドゥーロフはこの決定を後悔し、人気のないそのサービスを抹消した。"
    },
    {
      "id": 16,
      "ru": "Стратегию тройка основателей определила сразу: никакой монетизации и, в частности, рекламы первые несколько лет.",
      "en": "The trio of founders defined the strategy immediately: no monetization and, in particular, advertising for the first few years.",
      "zh": "三位创始人立即确定了战略：头几年不进行货币化，特别是（不接）广告。",
      "ja": "創業者の3人はすぐに戦略を決定した。最初の数年間はマネタイズを行わず、特に広告は一切なしとする。"
    },
    {
      "id": 17,
      "ru": "За год предстоит набрать миллион пользователей.",
      "en": "The goal is to recruit a million users in a year.",
      "zh": "目标是在一年内获得一百万用户。",
      "ja": "1年で100万人のユーザーを獲得することを目指す。"
    },
    {
      "id": 18,
      "ru": "Все усилия надо приложить к тому, чтобы дать людям удобный инструмент коммуникации, чтобы они тащили в сеть друзей и превратили ее в доминирующее средство общения в интернете.",
      "en": "All efforts must be applied to giving people a convenient communication tool so that they drag friends into the network and turn it into the dominant means of communication on the Internet.",
      "zh": "必须尽一切努力为人们提供便捷的交流工具，让他们把朋友拉进网络，使其成为互联网上主导的交流方式。",
      "ja": "あらゆる努力を払って人々に便利なコミュニケーションツールを提供し、彼らが友人をネットワークに引き込み、インターネット上の主要な通信手段へと変えるようにしなければならない。"
    },
    {
      "id": 19,
      "ru": "Слава взял кредит у отцовской фирмы и вложил в дело 30 000 долларов.",
      "en": "Slava took a loan from his father's firm and invested $30,000 in the business.",
      "zh": "斯拉瓦从父亲的公司贷款，向这门生意投资了3万美元。",
      "ja": "スラヴァは父親の会社から融資を受け、3万ドルを事業に投資した。"
    },
    {
      "id": 20,
      "ru": "Еще летом Дуров взял скопленные за три года деньги и купил сервер для будущих проектов.",
      "en": "Back in the summer, Durov took the money saved over three years and bought a server for future projects.",
      "zh": "早在夏天，杜罗夫就拿出了三年攒下的积蓄，为未来的项目购买了一台服务器。",
      "ja": "夏のうちに、ドゥーロフは3年間貯めたお金を使い、将来のプロジェクトのためにサーバーを購入していた。"
    },
    {
      "id": 21,
      "ru": "Так стартап обеспечил себя мощностями.",
      "en": "Thus the startup secured capacity for itself.",
      "zh": "就这样，这家初创公司确保了自己的计算能力。",
      "ja": "こうしてスタートアップは自らのための能力（容量）を確保した。"
    },
    {
      "id": 22,
      "ru": "Оставалось придумать название, а затем написать код.",
      "en": "It remained to come up with a name, and then write the code.",
      "zh": "剩下的就是想个名字，然后编写代码。",
      "ja": "あとは名前を考え、コードを書くだけだった。"
    },
    {
      "id": 23,
      "ru": "Тотем Петербургского университета поступил наоборот.",
      "en": "The Totem of St. Petersburg University did the opposite.",
      "zh": "这位圣彼得堡大学的图腾人物却反其道而行之。",
      "ja": "サンクトペテルブルク大学のトーテム（象徴的存在）は、逆のことを行った。"
    },
    {
      "id": 24,
      "ru": "Лабораторию института математики Макса Планка огласило пиликанье телефона.",
      "en": "The laboratory of the Max Planck Institute for Mathematics was filled with the ringing of a telephone.",
      "zh": "马克斯·普朗克数学研究所的实验室里响起了电话铃声。",
      "ja": "マックス・プランク数学研究所の研究室に、電話の呼び出し音が響き渡った。"
    },
    {
      "id": 25,
      "ru": "За окном медитативно падали листья и играли оркестры – население Бонна угорало по классической музыке на фестивале памяти Бетховена.",
      "en": "Outside the window, leaves fell meditatively and orchestras played – the population of Bonn was going wild for classical music at the Beethoven memorial festival.",
      "zh": "窗外落叶冥想般飘落，管弦乐队在演奏——波恩的居民正沉浸在贝多芬纪念音乐节的古典音乐狂热中。",
      "ja": "窓の外では瞑想するように葉が落ち、オーケストラが演奏していた――ボンの住民は、ベートーヴェン記念フェスティバルでクラシック音楽に熱狂していたのだ。"
    },
    {
      "id": 26,
      "ru": "Телефон пропиликал еще несколько раз, пока появившийся аспирант не взял трубку.",
      "en": "The phone rang a few more times until a graduate student appeared and picked up the receiver.",
      "zh": "电话又响了几声，直到一名研究生出现并拿起了听筒。",
      "ja": "電話はさらに数回鳴り、現れた大学院生が受話器を取った。"
    },
    {
      "id": 27,
      "ru": "Мужской голос спросил Николая Дурова.",
      "en": "A male voice asked for Nikolai Durov.",
      "zh": "一个男人的声音要找尼古拉·杜罗夫。",
      "ja": "男の声がニコライ・ドゥーロフを求めた。"
    },
    {
      "id": 28,
      "ru": "«Его нет, – вздохнул аспирант. – Когда придет, сказать не могу. Он не появляется в какое-то определенное время».",
      "en": "'He's not here,' sighed the graduate student. 'I can't say when he'll come. He doesn't appear at any specific time.'",
      "zh": "“他不在，”研究生叹了口气，“我不知道他什么时候来。他出现的时间不固定。”",
      "ja": "「彼はいません」と大学院生はため息をついた。「いつ来るかは言えません。彼は決まった時間には現れないので」。"
    },
    {
      "id": 29,
      "ru": "За четыре года, которые Николай занимался высшей алгеброй в Германии и готовил диссертацию на петербургский матмех, родственники привыкли, что дозвониться до него трудно.",
      "en": "Over the four years that Nikolai had been studying higher algebra in Germany and preparing a dissertation for the St. Petersburg Math-Mech Faculty, relatives had gotten used to the fact that it was hard to reach him.",
      "zh": "尼古拉在德国研究高等代数并为圣彼得堡数力系准备论文的这四年里，亲戚们已经习惯了很难联系上他。",
      "ja": "ニコライがドイツで高等代数学に取り組み、サンクトペテルブルク大学数学力学部への論文を準備していた4年間で、親戚たちは彼に連絡がつかないことに慣れてしまっていた。"
    },
    {
      "id": 30,
      "ru": "Мобильная связь была дорога, и мать пользовалась международной телефонной карточкой.",
      "en": "Mobile communication was expensive, and his mother used an international calling card.",
      "zh": "移动通信很贵，母亲使用的是国际电话卡。",
      "ja": "携帯電話の通話料は高く、母は国際電話カードを使っていた。"
    },
    {
      "id": 31,
      "ru": "Под аккомпанемент струнных коллеги уведомили Николая, что ему звонили, и, когда после очередной нетерпеливой трели он поднял трубку, там оказался брат.",
      "en": "Accompanied by strings, colleagues notified Nikolai that someone had called him, and when, after another impatient trill, he picked up the receiver, it was his brother.",
      "zh": "在弦乐的伴奏下，同事们通知尼古拉有人给他打过电话，当又一阵急促的铃声响起，他拿起听筒时，那边是他的弟弟。",
      "ja": "弦楽器の伴奏の中で、同僚たちはニコライに電話があったことを伝えた。そして、またしても短気な呼び出し音が鳴り響き、彼が受話器を取ると、そこにいたのは弟だった。"
    },
    {
      "id": 32,
      "ru": "«Я занялся новым проектом», – без преамбулы сообщил Дуров и выдал параметры.",
      "en": "'I've started a new project,' Durov announced without preamble and gave the parameters.",
      "zh": "“我搞了个新项目，”杜罗夫开门见山地说道，并给出了参数。",
      "ja": "「新しいプロジェクトを始めた」とドゥーロフは前置きなしに告げ、パラメータ（要件）を提示した。"
    },
    {
      "id": 33,
      "ru": "Социальная сеть для студентов, профиль, стена, на которой отображается личная активность, сообщения, фотозагрузчик и альбомы.",
      "en": "Social network for students, profile, wall displaying personal activity, messages, photo uploader, and albums.",
      "zh": "面向学生的社交网络，个人资料，显示个人动态的墙，消息，照片上传器和相册。",
      "ja": "学生のためのソーシャルネットワーク。プロフィール、個人のアクティビティが表示されるウォール、メッセージ、写真アップローダー、そしてアルバム。"
    },
    {
      "id": 34,
      "ru": "Плюс важнейшее – поиск людей не только по институтам-школам и годам обучения, но и по факультетам.",
      "en": "Plus the most important thing – searching for people not only by institutes/schools and years of study, but also by faculties.",
      "zh": "最重要的是——不仅可以通过学院/学校和入学年份找人，还可以通过系别查找。",
      "ja": "加えて最も重要なのは、大学・学校や学年だけでなく、学部でも人を検索できることだ。"
    },
    {
      "id": 35,
      "ru": "«С чего лучше начинать?»",
      "en": "'Where is it better to start?'",
      "zh": "“从哪儿开始比较好？”",
      "ja": "「何から始めるのがいい？」"
    },
    {
      "id": 36,
      "ru": "Николай не особенно удивился.",
      "en": "Nikolai wasn't particularly surprised.",
      "zh": "尼古拉并没有感到特别惊讶。",
      "ja": "ニコライは特に驚かなかった。"
    },
    {
      "id": 37,
      "ru": "Он помогал брату с первого написанного им куска кода.",
      "en": "He had been helping his brother since the first piece of code he wrote.",
      "zh": "从弟弟写第一段代码起，他就一直在帮忙。",
      "ja": "彼は弟が最初に書いたコードの断片からずっと手助けをしていた。"
    },
    {
      "id": 38,
      "ru": "Программа рисовала Сатурн и посередине Солнце – планета вращалась вокруг него почему-то по прямоугольной орбите.",
      "en": "The program drew Saturn and the Sun in the middle – the planet revolved around it for some reason in a rectangular orbit.",
      "zh": "那个程序画出了土星和中间的太阳——不知为何，行星是沿着矩形轨道绕着太阳转的。",
      "ja": "そのプログラムは土星と真ん中に太陽を描いていたが、なぜか惑星は長方形の軌道でその周りを回っていた。"
    },
    {
      "id": 39,
      "ru": "Когда брат придумал форум университета, он улучшал его движок InVision, правил php-код, добавлял новые функции.",
      "en": "When his brother invented the university forum, he improved its InVision engine, edited the PHP code, and added new functions.",
      "zh": "当弟弟构想出大学论坛时，他改进了InVision引擎，修改了PHP代码，添加了新功能。",
      "ja": "弟が大学のフォーラムを考案したとき、彼はそのInVisionエンジンを改良し、phpコードを修正し、新しい機能を追加した。"
    },
    {
      "id": 40,
      "ru": "Форум превратился в проект...",
      "en": "The forum turned into a project...",
      "zh": "论坛变成了一个项目……",
      "ja": "フォーラムはプロジェクトへと変わった……"
    }
  ],
  "translator_notes": [
    "Page 41 details the initial equity split: 20% each to founders, 40% to the investor (Mirilashvili Sr.).",
    "'The Totem of St. Petersburg University' likely refers to Durov (or Perekopsky), contrasting the usual 'name then code' process.",
    "The narrative shifts to Nikolai Durov in Bonn at the Max Planck Institute.",
    "Mentions of 'InVision' and 'PHP' highlight the technical origins of VK's predecessor."
  ],
  "total_sentences": 40,
  "page_type": "narrative"
}

with open("translations/page_041.json", "w", encoding="utf-8") as f:
    json.dump(page_content, f, indent=2, ensure_ascii=False)
