import json

page_content = {
  "page": 51,
  "chapter": 4,
  "chapter_title": "Сок черешни (Cherry Juice)",
  "sentences": [
    {
      "id": 1,
      "ru": "Это была странная квартира.",
      "en": "It was a strange apartment.",
      "zh": "那是一间奇怪的公寓。",
      "ja": "それは奇妙なアパートだった。"
    },
    {
      "id": 2,
      "ru": "Едва не в полтораста квадратных метров, с четырьмя комнатами, глядящими узкими вытянутыми окнами во двор-колодец.",
      "en": "Nearly one hundred and fifty square meters, with four rooms looking out through narrow elongated windows into a courtyard-well.",
      "zh": "将近一百五十平方米，有四个房间，狭长的窗户对着天井。",
      "ja": "150平方メートル近くあり、4つの部屋の細長い窓からは井戸のような中庭（コートヤード・ウェル）が見えた。"
    },
    {
      "id": 3,
      "ru": "Со стороны фасада шумел и клокотал человеческий трафик Невского.",
      "en": "From the facade side, the human traffic of Nevsky bustled and bubbled.",
      "zh": "在临街的一面，涅瓦大街的人流喧嚣沸腾。",
      "ja": "ファサード側からは、ネフスキー大通りの人の波がざわめき、沸き立っていた。"
    },
    {
      "id": 4,
      "ru": "Население квартиры менялось от одного до десяти постояльцев.",
      "en": "The population of the apartment varied from one to ten inhabitants.",
      "zh": "公寓的住户人数从一人到十人不等。",
      "ja": "アパートの住人は1人から10人と変動した。"
    },
    {
      "id": 5,
      "ru": "Средоточием жизни служила тесная комнатушка.",
      "en": "A cramped little room served as the center of life.",
      "zh": "生活的中心是一个狭窄的小房间。",
      "ja": "生活の中心は狭い小部屋だった。"
    },
    {
      "id": 6,
      "ru": "За сдвинутыми столами стучали клавишами люди, останавливаясь лишь в шесть утра, когда по провайдерскому обыкновению падала сеть.",
      "en": "People tapped keys at pushed-together tables, stopping only at six in the morning when, according to provider custom, the network went down.",
      "zh": "人们坐在拼在一起的桌子旁敲击键盘，直到早上六点才停下来，那是网络按照供应商惯例会断掉的时候。",
      "ja": "寄せ集めたテーブルに向かって人々はキーを叩き続け、プロバイダーの慣例でネットワークが落ちる朝6時になってようやく手を止めた。"
    },
    {
      "id": 7,
      "ru": "Тогда люди обсуждали богословские вопросы типа: «Какой должна быть платформа для разработчиков?» или «Что хотят люди от соцсети?»",
      "en": "Then people discussed theological questions like: 'What should the platform for developers be like?' or 'What do people want from a social network?'",
      "zh": "那时，人们会讨论神学问题，比如：“开发者平台应该是什么样的？”或者“人们想要从社交网络中得到什么？”",
      "ja": "その時、人々は神学的な問いを議論した。「開発者向けプラットフォームはどうあるべきか？」「人々はソーシャルネットワークに何を求めているのか？」といった類のものだ。"
    },
    {
      "id": 8,
      "ru": "Затем, утомленные кодом и схоластикой, валились на кровати и спали до часа дня.",
      "en": "Then, exhausted by code and scholasticism, they fell onto beds and slept until one in the afternoon.",
      "zh": "然后，被代码和经院哲学弄得精疲力竭的他们倒在床上，一直睡到下午一点。",
      "ja": "そして、コードとスコラ哲学に疲れ果て、ベッドに倒れ込んで午後1時まで眠るのだった。"
    },
    {
      "id": 9,
      "ru": "Чтобы попасть во двор, Лев свернул с проспекта в подворотню с дверями неясного назначения и крадущимися по стенам проводами.",
      "en": "To get into the courtyard, Lev turned from the avenue into an archway with doors of unclear purpose and wires creeping along the walls.",
      "zh": "为了进入院子，列夫从大街拐进一个拱门通道，那里有用途不明的门和沿着墙壁爬行的电线。",
      "ja": "中庭に入るために、レフは大通りからアーチ道へと曲がった。そこには用途不明のドアがあり、壁には配線が這っていた。"
    },
    {
      "id": 10,
      "ru": "Раньше дом занимали контора и квартиры банкира Блокка, который реконструировал здание и воздвиг на фасаде аллегории Правосудия и Адвокатуры.",
      "en": "Previously, the house was occupied by the office and apartments of banker Block, who reconstructed the building and erected allegories of Justice and Advocacy on the facade.",
      "zh": "以前，这栋房子是银行家布洛克（Block）的办公室和公寓，他重建了这座建筑，并在正面上竖立了正义和辩护的寓言雕像。",
      "ja": "以前この家は、建物を改築し、ファサードに「正義」と「弁護」の寓意像を建てた銀行家ブロックの事務所とアパートとして使われていた。"
    },
    {
      "id": 11,
      "ru": "Дуров питал слабость к символике, и наличие аллегорий сыграло роль в выборе квартиры, к которой, гулко топая по лестнице, поднимался акционер его компании, нагруженный коробками.",
      "en": "Durov had a weakness for symbolism, and the presence of allegories played a role in the choice of the apartment, to which, stomping loudly on the stairs, the shareholder of his company, loaded with boxes, was ascending.",
      "zh": "杜罗夫对象征主义情有独钟，寓言雕像的存在对他选择这间公寓起到了作用，此时，他公司的股东正抱着箱子，脚步沉重地爬上楼梯走向那里。",
      "ja": "ドゥーロフはシンボリズムに弱く、寓意像の存在はこのアパートを選ぶ上で一役買っていた。そして今、彼の会社の株主が箱を抱え、階段を大きな音を立てて上っていた。"
    },
    {
      "id": 12,
      "ru": "Часто ночами одна из теней отвлекалась от ноутбука и бросала клич: «Кто за суши?»",
      "en": "Often at night, one of the shadows would distract from the laptop and issue a call: 'Who's up for sushi?'",
      "zh": "夜晚，常有一个黑影从笔记本电脑前抬起头，喊一声：“谁想吃寿司？”",
      "ja": "夜中、影の一つがラップトップから目を離し、「寿司を食べたい奴は？」と声を上げることがよくあった。"
    },
    {
      "id": 13,
      "ru": "Коллеги неохотно отрывались от экранов и выдвигались в сторону двери и вниз по лестнице – к бару на углу Фонтанки и Невского.",
      "en": "Colleagues reluctantly tore themselves away from screens and moved towards the door and down the stairs – to the bar on the corner of Fontanka and Nevsky.",
      "zh": "同事们不情愿地把视线从屏幕上移开，走向门口，下楼——去丰坦卡河和涅瓦大街拐角处的酒吧。",
      "ja": "同僚たちは渋々スクリーンから離れ、ドアの方へ向かい、階段を下りて、フォンタンカ川とネフスキー大通りの角にあるバーへと向かった。"
    },
    {
      "id": 14,
      "ru": "Но в эту ночь они были заняты настолько, что Дуров набрал номер Льва и попросил привезти еды.",
      "en": "But that night they were so busy that Durov dialed Lev's number and asked to bring food.",
      "zh": "但这天晚上他们太忙了，杜罗夫只好拨通列夫的电话，让他带点吃的来。",
      "ja": "しかしその夜、彼らはあまりに忙しく、ドゥーロフはレフに電話をかけて食事を持ってきてくれるよう頼んだ。"
    },
    {
      "id": 15,
      "ru": "Лев добрался до двери, перевел дыхание.",
      "en": "Lev got to the door, caught his breath.",
      "zh": "列夫到了门口，喘了口气。",
      "ja": "レフはドアにたどり着き、息を整えた。"
    },
    {
      "id": 16,
      "ru": "Позвонил.",
      "en": "Rang the bell.",
      "zh": "按了门铃。",
      "ja": "ベルを鳴らした。"
    },
    {
      "id": 17,
      "ru": "Шаги.",
      "en": "Footsteps.",
      "zh": "脚步声。",
      "ja": "足音。"
    },
    {
      "id": 18,
      "ru": "«Пи-иццу заказывали?» – крикнул он.",
      "en": "'Did you order pi-izza?' he shouted.",
      "zh": "“叫了披——萨吗？”他喊道。",
      "ja": "「ピザをご注文ですか？」と彼は叫んだ。"
    },
    {
      "id": 19,
      "ru": "Дверь отворил Дуров и, улыбаясь, отошел в сторону.",
      "en": "Durov opened the door and, smiling, stepped aside.",
      "zh": "杜罗夫开了门，微笑着闪到一边。",
      "ja": "ドゥーロフがドアを開け、微笑みながら脇にどいた。"
    },
    {
      "id": 20,
      "ru": "Лев, хоть и не впервые заглядывал сюда, с удивлением осмотрел пустующую квартиру.",
      "en": "Lev, although not visiting here for the first time, looked around the empty apartment with surprise.",
      "zh": "列夫虽然不是第一次来这里，但还是惊讶地环顾了一下空荡荡的公寓。",
      "ja": "レフはここに来るのが初めてではなかったが、驚いて空っぽのアパートを見回した。"
    },
    {
      "id": 21,
      "ru": "Его приход будто не заметили.",
      "en": "His arrival seemed unnoticed.",
      "zh": "他的到来似乎没人注意。",
      "ja": "彼の到着は気づかれていないようだった。"
    },
    {
      "id": 22,
      "ru": "Программисты сгрудились в каком-то чулане.",
      "en": "The programmers huddled in some closet.",
      "zh": "程序员们挤在一个储藏室里。",
      "ja": "プログラマーたちはどこかの物置部屋に密集していた。"
    },
    {
      "id": 23,
      "ru": "Николай восседал в кресле и стучал по клавиатуре, время от времени прикладываясь к шоколадному батончику.",
      "en": "Nikolai sat in an armchair and tapped on the keyboard, occasionally taking a bite of a chocolate bar.",
      "zh": "尼古拉坐在扶手椅上敲击键盘，不时咬一口巧克力棒。",
      "ja": "ニコライは肘掛け椅子に座り、時折チョコレートバーをかじりながらキーボードを叩いていた。"
    },
    {
      "id": 24,
      "ru": "За самым большим из сдвинутых столов согнулся кто-то худой и растрепанный.",
      "en": "Someone thin and disheveled was bent over the largest of the pushed-together tables.",
      "zh": "在拼起来的最大的桌子旁，一个瘦削、头发蓬乱的人正弯着腰。",
      "ja": "寄せ集めたテーブルの中で一番大きなものに、痩せて髪の乱れた誰かが前かがみになっていた。"
    },
    {
      "id": 25,
      "ru": "Некоторые из аутистов все-таки поздоровались, но, взяв еду, вернулись к коду.",
      "en": "Some of the autists did say hello, but, taking the food, returned to the code.",
      "zh": "有些“自闭症患者”还是打了招呼，但拿了食物后就回到了代码中。",
      "ja": "「自閉症児」たちの何人かは挨拶をしたが、食事を受け取るとコードに戻っていった。"
    },
    {
      "id": 26,
      "ru": "Лев поговорил с предводителем, по которому было видно, что он тоже не прочь уткнуться в десктоп.",
      "en": "Lev spoke with the leader, from whom it was clear that he, too, would not mind burying himself in the desktop.",
      "zh": "列夫和头儿聊了几句，看得出来，他也想一头扎进电脑里。",
      "ja": "レフはリーダーと話したが、彼もまたデスクトップに没頭したくてうずうずしているのが見て取れた。"
    },
    {
      "id": 27,
      "ru": "Впрочем, Дуров, как всегда, был вежлив и прохладно приветлив.",
      "en": "However, Durov, as always, was polite and coolly welcoming.",
      "zh": "不过，杜罗夫一如既往地礼貌且冷淡地友好。",
      "ja": "もっとも、ドゥーロフはいつものように礼儀正しく、冷ややかに愛想がよかった。"
    },
    {
      "id": 28,
      "ru": "Висело ощущение шабаша, на который заглянула человеческая душа.",
      "en": "There was a feeling of a coven, into which a human soul had looked.",
      "zh": "有一种像是人类灵魂闯入了女巫集会的感觉。",
      "ja": "まるで魔女の集会に人間の魂が迷い込んだような感覚が漂っていた。"
    },
    {
      "id": 29,
      "ru": "Лев чувствовал себя не совсем уютно.",
      "en": "Lev didn't feel quite comfortable.",
      "zh": "列夫感觉不太自在。",
      "ja": "レフはあまり居心地が良くなかった。"
    },
    {
      "id": 30,
      "ru": "После сделки с Мильнером осенью 2007 года Дуров получил на счет деньги и с помощью матери, устроившейся риелтором, вложил их в квартиры – одну купил недалеко от дома, другую как офис, в сердце города.",
      "en": "After the deal with Milner in the fall of 2007, Durov received money in his account and, with the help of his mother, who got a job as a realtor, invested them in apartments – he bought one not far from home, another as an office, in the heart of the city.",
      "zh": "2007年秋天与米尔纳达成交易后，杜罗夫的账户收到了钱，在他做房地产经纪人的母亲的帮助下，他把钱投资了公寓——一套买在离家不远的地方，另一套作为办公室，位于市中心。",
      "ja": "2007年秋のミルナーとの取引後、ドゥーロフは口座に金を受け取り、不動産業者として働き始めた母の助けを借りて、それをアパートに投資した。1つは自宅の近くに、もう1つはオフィスのために市の中心部に購入した。"
    },
    {
      "id": 31,
      "ru": "Николай вернулся в Петербург, и вот они с братом осматривали анфиладу комнат – две спальни, гостиная, подобие чулана для прислуги, кухня.",
      "en": "Nikolai returned to St. Petersburg, and here he and his brother inspected the enfilade of rooms – two bedrooms, a living room, a semblance of a closet for servants, a kitchen.",
      "zh": "尼古拉回到了圣彼得堡，他和弟弟一起查看这一连串的房间——两间卧室、客厅、一个像仆人储藏室的地方、厨房。",
      "ja": "ニコライはサンクトペテルブルクに戻り、兄と共に部屋の並び（アンフィラード）を見て回った――2つの寝室、リビング、使用人用の物置のような部屋、そしてキッチン。"
    },
    {
      "id": 32,
      "ru": "Дуров как истинный петербуржец привык жить в декорациях к историческим спектаклям, хотя, впрочем, признавал, что в последнее время репертуар измельчал и театр пробавляется одноактными оперетками про весенние сосули.",
      "en": "Durov, as a true Petersburger, was accustomed to living in the scenery for historical performances, although, however, he admitted that lately the repertoire had become shallow and the theater was getting by with one-act operettas about spring icicles.",
      "zh": "作为一个真正的圣彼得堡人，杜罗夫习惯了生活在历史剧的布景中，尽管他也承认，最近剧目变得肤浅了，剧院靠关于春季冰柱的独幕轻歌剧度日。",
      "ja": "真のサンクトペテルブルク人として、ドゥーロフは歴史劇の舞台セットの中で暮らすことに慣れていた。もっとも、最近はレパートリーが陳腐化し、劇場は春のつららに関する一幕物のオペレッタで食いつないでいることは認めていたが。"
    },
    {
      "id": 33,
      "ru": "Команда расширялась, и вскоре в девятиметровом пенале за сдвинутыми столами толкались четыре человека.",
      "en": "The team was expanding, and soon four people were jostling at pushed-together tables in a nine-meter pencil case.",
      "zh": "团队在扩大，很快，四个人挤在这个九米长的“铅笔盒”里拼桌工作。",
      "ja": "チームは拡大し、やがて9メートルの細長い部屋（ペンケース）で、寄せ集めたテーブルに4人がひしめき合うようになった。"
    },
    {
      "id": 34,
      "ru": "Изредка кто-то уходил на кухню и кодил за столом для готовки.",
      "en": "Occasionally someone went to the kitchen and coded at the cooking table.",
      "zh": "偶尔有人去厨房，在做饭的桌子上写代码。",
      "ja": "時折誰かがキッチンに行き、調理台でコードを書いた。"
    },
    {
      "id": 35,
      "ru": "Прочие метры оставались невостребованными.",
      "en": "The other meters remained unclaimed.",
      "zh": "其他空间则闲置着。",
      "ja": "残りのスペースは使われないままだった。"
    },
    {
      "id": 36,
      "ru": "Четырьмя годами позже я сел в лифт, напоминавший золоченую клетку, устланную коврами в духе советского министерства тяжелой промышленности, и поднялся на один из двух этажей «ВКонтакте» в доме Зингера.",
      "en": "Four years later, I sat in an elevator resembling a gilded cage, covered with carpets in the spirit of the Soviet Ministry of Heavy Industry, and went up to one of the two floors of VKontakte in the Singer House.",
      "zh": "四年后，我坐进了一部像镀金笼子的电梯，里面铺着苏联重工业部风格的地毯，升到了辛格大厦里VKontakte所在的两个楼层之一。",
      "ja": "4年後、私はソ連の重工業省のようなカーペットが敷かれた金色の檻を思わせるエレベーターに乗り、ジンガーハウスにあるVKontakteの2つのフロアのうちの1つへと上がった。"
    },
    {
      "id": 37,
      "ru": "Перед дуровской бандой здесь обитали юристы,",
      "en": "Before Durov's gang, lawyers lived here,",
      "zh": "在杜罗夫帮派之前，这里住着律师，",
      "ja": "ドゥーロフの一味が入る前、ここには弁護士たちがいた。"
    }
  ],
  "translator_notes": [
    "Chapter 4 'Cherry Juice' begins, focusing on the team's move to a rented apartment on Nevsky Prospekt.",
    "'Courtyard-well' (двор-колодец) is a typical St. Petersburg architectural feature.",
    "'Theological questions' refers to high-level architectural/ideological debates about the platform.",
    "The 'allegories of Justice and Advocacy' on the facade add a symbolic layer to their 'pirate' operations.",
    "Lev Leviev bringing pizza highlights the startup atmosphere: intense work, no time for food, investors helping with basics.",
    "The mention of 'spring icicles' (сосули) refers to a specific St. Petersburg meme/problem where the governor Valentina Matvienko proposed using lasers to cut down dangerous icicles.",
    "The chapter contrasts the cramped first apartment with the later grandeur of the Singer House HQ."
  ],
  "total_sentences": 37,
  "page_type": "narrative"
}

with open("translations/page_051.json", "w", encoding="utf-8") as f:
    json.dump(page_content, f, indent=2, ensure_ascii=False)
