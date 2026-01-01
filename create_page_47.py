import json

page_content = {
  "page": 47,
  "chapter": 3,
  "chapter_title": "Глава 3",
  "sentences": [
    {
      "id": 1,
      "ru": "Консультант «подкрутил параметры», и первая версия запустилась.",
      "en": "The consultant 'tweaked the parameters', and the first version was launched.",
      "zh": "顾问“调整了参数”，第一版就这样上线了。",
      "ja": "コンサルタントが「パラメータを微調整」し、最初のバージョンが起動した。"
    },
    {
      "id": 2,
      "ru": "«Дуровы все быстро поняли и через три месяца перестали советоваться, – резюмировал Бунин.",
      "en": "'The Durovs understood everything quickly and after three months stopped asking for advice,' Bunin summarized.",
      "zh": "“杜罗夫兄弟学得很快，三个月后就不再来咨询了，”布宁总结道。",
      "ja": "「ドゥーロフ兄弟はすぐにすべてを理解し、3ヶ月後には相談に来なくなった」とブニンは総括した。"
    },
    {
      "id": 3,
      "ru": "– Мы показали, куда копать, и они перекопали нас».",
      "en": "'We showed them where to dig, and they out-dug us.'",
      "zh": "“我们指给他们哪里可以挖掘，结果他们挖得比我们还深。”",
      "ja": "「私たちが掘るべき場所を示したら、彼らは私たち以上に掘り進めてしまった」"
    },
    {
      "id": 4,
      "ru": "Мы встретились на конференции HighLoad-2011.",
      "en": "We met at the HighLoad-2011 conference.",
      "zh": "我们在2011年的HighLoad大会上见了面。",
      "ja": "私たちはHighLoad-2011カンファレンスで会った。"
    },
    {
      "id": 5,
      "ru": "«ВКонтакте» прислала разработчика Андрея Илларионова, и набитый битком зал задавал ему недоуменные вопросы по их системе распределения нагрузок.",
      "en": "VKontakte sent developer Andrey Illarionov, and the packed hall asked him puzzled questions about their load distribution system.",
      "zh": "VKontakte派出了开发人员安德烈·伊拉里奥诺夫（Andrey Illarionov），挤得水泄不通的大厅向他提出了关于负载分配系统的困惑问题。",
      "ja": "VKontakteは開発者のアンドレイ・イラリオノフを派遣し、超満員の会場は彼らの負荷分散システムについて困惑した質問を投げかけていた。"
    },
    {
      "id": 6,
      "ru": "Некоторые решения не то что не приходили никому в голову – даже после выступления не стало яснее, как они работают.",
      "en": "Some solutions not only hadn't occurred to anyone – even after the presentation, it didn't become clearer how they worked.",
      "zh": "有些解决方案不仅以前没人想到过——甚至在演讲结束后，大家也没搞清楚它们到底是怎么运作的。",
      "ja": "いくつかのソリューションは、誰も思いつかなかったというだけでなく、講演後もどう機能しているのか判然としなかった。"
    },
    {
      "id": 7,
      "ru": "«Когда общаешься с обычным человеком, почти всегда представляешь, что он ответит, – говорил Бунин.",
      "en": "'When you communicate with an ordinary person, you almost always imagine what he will answer,' said Bunin.",
      "zh": "“当你和普通人交流时，你几乎总是能想象出他会怎么回答，”布宁说。",
      "ja": "「普通の人と話していると、相手がどう答えるか大体想像がつくものです」とブニンは言った。"
    },
    {
      "id": 8,
      "ru": "– Павел постоянно думал по-другому и масштабно.",
      "en": "'Pavel constantly thought differently and on a large scale.",
      "zh": "“帕维尔总是以不同的方式思考，而且格局很大。",
      "ja": "「パーヴェルは常に人と違う考え方をし、スケールが大きかった。"
    },
    {
      "id": 9,
      "ru": "Знаете, как Цукерберг в фильме „Социальная сеть“ – когда девушка его отвергла, приятель хочет посочувствовать, а он уже думает о своей сети: „Пора расширяться“.",
      "en": "You know, like Zuckerberg in the movie \"The Social Network\" – when the girl rejected him, his friend wants to sympathize, but he is already thinking about his network: \"It's time to expand.\"",
      "zh": "你知道，就像电影《社交网络》里的扎克伯格——当女孩拒绝了他，朋友想安慰他时，他却已经在想他的网络了：‘是时候扩张了’。",
      "ja": "映画『ソーシャル・ネットワーク』のザッカーバーグみたいにね。女の子に振られたとき、友人が同情しようとしているのに、彼はもう自分のネットワークのことを考えている。『拡大する時だ』って。"
    },
    {
      "id": 10,
      "ru": "Дуров – такой же».",
      "en": "Durov is the same.'",
      "zh": "杜罗夫也是这样。”",
      "ja": "ドゥーロフも同じですよ」"
    },
    {
      "id": 11,
      "ru": "Это наблюдение Бунина повторяли разные деятели рунета.",
      "en": "Different figures of the Runet repeated this observation of Bunin.",
      "zh": "俄罗斯互联网界的各路人士都重复过布宁的这个观察。",
      "ja": "ブニンのこの観察は、ロシアのネット界の様々な人物によって繰り返された。"
    },
    {
      "id": 12,
      "ru": "Способность думать иначе стала краеугольным камнем для дуровской команды, спровоцировала изменения личности ее участников и привела к неминуемому конфликту с окружающей реальностью.",
      "en": "The ability to think differently became the cornerstone for Durov's team, provoked personality changes in its members, and led to an inevitable conflict with the surrounding reality.",
      "zh": "这种“不同凡响”的思考能力成为了杜罗夫团队的基石，引发了成员个性的改变，并导致了与周围现实不可避免的冲突。",
      "ja": "「違う考え方をする」能力はドゥーロフ・チームの礎となり、メンバーの人格的変化を引き起こし、周囲の現実との避けられない対立を招いた。"
    },
    {
      "id": 13,
      "ru": "Но тогда, первой зимой «ВКонтакте», сентенции Дурова выдавали лишь оригинальный ум.",
      "en": "But then, in the first winter of VKontakte, Durov's maxims betrayed only an original mind.",
      "zh": "但在当时，在VKontakte的第一个冬天，杜罗夫的格言警句只显示出他独特的头脑。",
      "ja": "しかし当時、VKontakteの最初の冬には、ドゥーロフの警句は単に独創的な精神を示すに過ぎなかった。"
    },
    {
      "id": 14,
      "ru": "Для интернет-тусовки соцсеть выглядела не более чем любопытным проектом с пассионарным основателем, уверенным, что выведет сайт в топ популярных ресурсов.",
      "en": "For the Internet crowd, the social network looked like nothing more than a curious project with a passionate founder, confident that he would bring the site to the top of popular resources.",
      "zh": "对于互联网圈子来说，这个社交网络看起来不过是一个有趣的项目，拥有一个充满激情的创始人，坚信自己能把网站带入热门资源的前列。",
      "ja": "インターネット界隈にとって、そのソーシャルネットワークは、サイトを人気リソースのトップに押し上げると確信している情熱的な創設者による、興味深いプロジェクトに過ぎないように見えた。"
    },
    {
      "id": 15,
      "ru": "Дуровы советовались с консультантами, но вызывали их все реже.",
      "en": "The Durovs consulted with advisors, but called them less and less often.",
      "zh": "杜罗夫兄弟会咨询顾问，但召见他们的次数越来越少。",
      "ja": "ドゥーロフ兄弟はコンサルタントに相談していたが、彼らを呼ぶ頻度は減っていった。"
    },
    {
      "id": 16,
      "ru": "«Какие-то вещи я сразу сделал, как считал нужным, – рассказывал Николай.",
      "en": "'Some things I did immediately as I saw fit,' Nikolai said.",
      "zh": "“有些事情我直接按我认为正确的方式去做了，”尼古拉说。",
      "ja": "「いくつかのことは、すぐに自分が必要だと思う通りにやりました」とニコライは語った。"
    },
    {
      "id": 17,
      "ru": "– Например, Бунин советовал хранить фотографии на одном домене и пропускать все через один сервер.",
      "en": "'For example, Bunin advised storing photos on one domain and passing everything through one server.",
      "zh": "“例如，布宁建议将照片存储在一个域名上，并通过一台服务器传输所有内容。",
      "ja": "「例えばブニンは、写真を1つのドメインに保存し、すべてを1つのサーバー経由にするよう助言しました。"
    },
    {
      "id": 18,
      "ru": "А я предложил отдавать фото с того сервера, где они находятся».",
      "en": "But I suggested serving photos from the server where they are located.'",
      "zh": "而我提议直接从照片所在的服务器分发照片。”",
      "ja": "でも僕は、写真があるサーバーから直接配信することを提案したんです」"
    },
    {
      "id": 19,
      "ru": "Счетчик посещаемости крутился как бешеный, пока однажды февральским вечером Павел Дуров не набил в браузере vkontakte.ru и не обнаружил вместо соцсети «ошибку 502».",
      "en": "The attendance counter spun like mad until one February evening Pavel Durov typed vkontakte.ru in the browser and discovered 'error 502' instead of the social network.",
      "zh": "访问量计数器疯狂转动，直到二月的一个晚上，帕维尔·杜罗夫在浏览器中输入vkontakte.ru，发现显示的不是社交网络，而是“502错误”。",
      "ja": "アクセス数は狂ったように回っていたが、ある2月の夜、パーヴェル・ドゥーロフがブラウザにvkontakte.ruと打ち込むと、ソーシャルネットワークの代わりに「エラー502」が表示された。"
    },
    {
      "id": 20,
      "ru": "Вход на сайт для пользователей оказался закрыт.",
      "en": "Entrance to the site for users turned out to be closed.",
      "zh": "用户无法进入网站。",
      "ja": "ユーザーのサイトへの入り口は閉ざされていた。"
    },
    {
      "id": 21,
      "ru": "Дуров набрал телефон хостинг-провайдера.",
      "en": "Durov dialed the hosting provider's phone number.",
      "zh": "杜罗夫拨通了托管服务提供商的电话。",
      "ja": "ドゥーロフはホスティングプロバイダーに電話をかけた。"
    },
    {
      "id": 22,
      "ru": "Трубку взял дежурный инженер.",
      "en": "The duty engineer picked up the phone.",
      "zh": "值班工程师接了电话。",
      "ja": "当直のエンジニアが電話に出た。"
    },
    {
      "id": 23,
      "ru": "– Алло, привет. Мы висим.",
      "en": "- Hello, hi. We are hanging.",
      "zh": "——喂，你好。我们挂了（网站卡死了）。",
      "ja": "「もしもし。サイトが固まってるんだ」"
    },
    {
      "id": 24,
      "ru": "– Привет, сейчас разберемся. (Пауза.) Так. Идет огромный поток запросов к сайту, волна полтора гигабита. Канал забился.",
      "en": "- Hi, we'll sort it out now. (Pause.) So. There is a huge stream of requests to the site, a wave of one and a half gigabits. The channel is clogged.",
      "zh": "——你好，我们马上查。（停顿）好了。有一股巨大的请求流涌向网站，1.5Gbps的浪潮。通道堵塞了。",
      "ja": "「どうも。今調べます。（沈黙）そうですね。サイトへのリクエストがものすごい勢いで来てます。1.5ギガビットの波です。回線がパンクしてます」"
    },
    {
      "id": 25,
      "ru": "– Есть идеи, что делать?",
      "en": "- Any ideas what to do?",
      "zh": "——有主意该怎么办吗？",
      "ja": "「どうすればいいか案はある？」"
    },
    {
      "id": 26,
      "ru": "– Если честно, нет.",
      "en": "- To be honest, no.",
      "zh": "——老实说，没有。",
      "ja": "「正直なところ、ありません」"
    },
    {
      "id": 27,
      "ru": "Звонить в Бонн поздно, брат наверняка ушел из лаборатории.",
      "en": "It's too late to call Bonn, his brother surely left the laboratory.",
      "zh": "给波恩打电话太晚了，哥哥肯定已经离开实验室了。",
      "ja": "ボンに電話するには遅すぎる。兄はきっともう研究室を出ただろう。"
    },
    {
      "id": 28,
      "ru": "Пальто, штиблеты, ключ, деньги, такси.",
      "en": "Coat, boots, key, money, taxi.",
      "zh": "大衣，靴子，钥匙，钱，出租车。",
      "ja": "コート、靴、鍵、金、タクシー。"
    },
    {
      "id": 29,
      "ru": "Дуров ворвался в прохладную комнату со стеклянными стеллажами, нашел свои сервера и перезагрузил их.",
      "en": "Durov burst into the cool room with glass shelves, found his servers, and rebooted them.",
      "zh": "杜罗夫冲进有着玻璃架的凉爽房间，找到自己的服务器并重启了它们。",
      "ja": "ドゥーロフはガラス棚のある涼しい部屋に飛び込み、自分のサーバーを見つけ、再起動した。"
    },
    {
      "id": 30,
      "ru": "Волна шла из Китая, Южной Америки, Украины.",
      "en": "The wave came from China, South America, Ukraine.",
      "zh": "攻击浪潮来自中国、南美、乌克兰。",
      "ja": "波は中国、南米、ウクライナから来ていた。"
    },
    {
      "id": 31,
      "ru": "Даже если передать провайдерам списки IP-адресов, участвовавших в атаке, чтобы те их заблокировали, – все равно шансы на успех мизерны.",
      "en": "Even if you pass the lists of IP addresses participating in the attack to the providers so that they block them – the chances of success are still meager.",
      "zh": "即使把参与攻击的IP地址列表交给供应商让他们封锁——成功的几率依然渺茫。",
      "ja": "攻撃に参加しているIPアドレスのリストをプロバイダーに渡してブロックしてもらったとしても、成功する確率はごくわずかだ。"
    },
    {
      "id": 32,
      "ru": "Соперник не идиот, атакует с других компьютеров.",
      "en": "The opponent is not an idiot, he attacks from other computers.",
      "zh": "对手不是白痴，会换其他电脑攻击。",
      "ja": "相手は馬鹿ではない。別のコンピュータから攻撃してくる。"
    },
    {
      "id": 33,
      "ru": "Утром Дуров известил брата, и они начали суматошно перебирать способы защиты.",
      "en": "In the morning, Durov notified his brother, and they began to frantically sort through methods of protection.",
      "zh": "早上，杜罗夫通知了哥哥，他们开始疯狂地寻找防御方法。",
      "ja": "翌朝、ドゥーロフは兄に知らせ、二人は大慌てで防御策を検討し始めた。"
    },
    {
      "id": 34,
      "ru": "Сначала арендовали маршрутизатор, который идентифицирует врага.",
      "en": "First, they rented a router that identifies the enemy.",
      "zh": "首先，他们租用了一个能识别敌人的路由器。",
      "ja": "まず、敵を識別するルーターをレンタルした。"
    },
    {
      "id": 35,
      "ru": "Зная провайдера, можно его блокировать – но, опять же, провайдеров-то тысячи.",
      "en": "Knowing the provider, you can block him – but, again, there are thousands of providers.",
      "zh": "知道供应商就可以封锁它——但话又说回来，供应商有成千上万个。",
      "ja": "プロバイダーがわかればブロックできるが、やはりプロバイダーは何千とある。"
    },
    {
      "id": 36,
      "ru": "Ночами они с Николаем, который еще не дописал диссер, созванивались и ломали головы, что бы предпринять.",
      "en": "At night, he and Nikolai, who had not yet finished his dissertation, called each other and racked their brains over what to do.",
      "zh": "在还没写完论文的尼古拉的陪伴下，他们夜里通电话，绞尽脑汁想办法。",
      "ja": "まだ論文を書き終えていないニコライと夜通し電話をし、どうすべきか頭を悩ませた。"
    },
    {
      "id": 37,
      "ru": "Атаки продолжались – их старались заваливать запросами ближе к ночи.",
      "en": "The attacks continued – they tried to overwhelm them with requests closer to the night.",
      "zh": "攻击仍在继续——对手试图在深夜用请求淹没他们。",
      "ja": "攻撃は続いた――夜になるとリクエスト攻めにしてダウンさせようとしてきた。"
    },
    {
      "id": 38,
      "ru": "Особой популярностью пользовался вечер пятницы, когда в офисе провайдера оставался только дежурный.",
      "en": "Friday evening was especially popular, when only the duty officer remained in the provider's office.",
      "zh": "周五晚上尤其受（攻击者）欢迎，因为那时供应商办公室只剩下值班人员。",
      "ja": "特に金曜日の夜は人気があった。プロバイダーのオフィスには当直しか残っていないからだ。"
    },
    {
      "id": 39,
      "ru": "На форуме СПбГУ жаловались, что «ВКонтакте» лежит, сочувствовали, но ничего посоветовать не могли.",
      "en": "On the St. Petersburg State University forum, they complained that VKontakte was down, sympathized, but could not advise anything.",
      "zh": "在圣彼得堡国立大学的论坛上，人们抱怨VKontakte挂了，虽然表示同情，但也给不出什么建议。",
      "ja": "サンクトペテルブルク大学のフォーラムでは、VKontakteがダウンしているという不満が出たり、同情されたりしたが、誰も助言はできなかった。"
    },
    {
      "id": 40,
      "ru": "Слава и Лев вели свое расследование, и им даже слили переписку с исполнителями атаки, однако установить заказчика не удалось.",
      "en": "Slava and Lev conducted their own investigation, and they were even leaked correspondence with the perpetrators of the attack, but the customer could not be identified.",
      "zh": "斯拉瓦和列夫进行了自己的调查，甚至有人把与攻击执行者的通信泄露给了他们，但没能查出幕后主使。",
      "ja": "スラヴァとレフは独自の調査を行い、実行犯とのやり取りを入手することさえできたが、依頼主を特定することはできなかった。"
    },
    {
      "id": 41,
      "ru": "Дуров написал письмо юзерам:",
      "en": "Durov wrote a letter to the users:",
      "zh": "杜罗夫给用户写了一封信：",
      "ja": "ドゥーロフはユーザーに手紙を書いた："
    },
    {
      "id": 42,
      "ru": "«В течение прошедшего дня (18.02.2007) активность доходила до фантастической отметки в 2 млн запросов в минуту.",
      "en": "'During the past day (18.02.2007), activity reached a fantastic mark of 2 million requests per minute.",
      "zh": "“在过去的一天（2007年2月18日），活跃度达到了每分钟200万次请求的惊人水平。",
      "ja": "「昨日（2007年2月18日）一日で、アクティビティは毎分200万リクエストという驚異的な数値に達しました。"
    },
    {
      "id": 43,
      "ru": "Это позволило предположить, что весомая доля запросов была создана искусственно для...",
      "en": "This allowed us to assume that a significant share of requests was created artificially for...",
      "zh": "这让我们推测，很大一部分请求是人为制造的，目的是……",
      "ja": "これは、リクエストのかなりの部分が人為的に作られたものであることを示唆しています……"
    }
  ],
  "translator_notes": [
    "The chapter discusses the first major DDoS attack on VKontakte in Feb 2007.",
    "Bunin's comment about the Durovs 'out-digging' the consultants highlights their rapid learning curve.",
    "HighLoad is a major professional conference for backend developers.",
    "The 502 Bad Gateway error became a familiar sight during these attacks.",
    "The attack origin (China, S. America, Ukraine) indicates a botnet."
  ],
  "total_sentences": 43,
  "page_type": "narrative"
}

with open("translations/page_047.json", "w", encoding="utf-8") as f:
    json.dump(page_content, f, indent=2, ensure_ascii=False)
