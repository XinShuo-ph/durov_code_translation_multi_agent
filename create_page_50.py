import json

page_content = {
  "page": 50,
  "chapter": 3,
  "chapter_title": "Глава 3",
  "sentences": [
    {
      "id": 1,
      "ru": "Дуров не придал сведениям о ревности Гришина большого значения, так как считал конкуренцию благотворной.",
      "en": "Durov did not attach much importance to the information about Grishin's jealousy, as he considered competition beneficial.",
      "zh": "杜罗夫并没有太在意关于格里申嫉妒的消息，因为他认为竞争是有益的。",
      "ja": "ドゥーロフは、競争は有益だと考えていたため、グリシンの嫉妬に関する情報にはあまり重要性を認めなかった。"
    },
    {
      "id": 2,
      "ru": "Но однажды он сопоставил даты визитов Мильнера и атак на сайт.",
      "en": "But one day he compared the dates of Milner's visits and the attacks on the site.",
      "zh": "但有一天，他对比了米尔纳来访的日期和网站受攻击的日期。",
      "ja": "しかしある日、彼はミルナーの訪問日とサイトへの攻撃日を照らし合わせてみた。"
    },
    {
      "id": 3,
      "ru": "Выяснилось, что они практически совпадают.",
      "en": "It turned out that they practically coincide.",
      "zh": "结果发现，它们几乎完全吻合。",
      "ja": "すると、それらはほぼ一致していることが判明した。"
    },
    {
      "id": 4,
      "ru": "Впрочем, железных доказательств версии, что инвестор таким образом санкционировал проверку «ВКонтакте» через своего менеджера, Дурову заполучить не удалось.",
      "en": "However, Durov failed to obtain ironclad evidence for the version that the investor thus sanctioned the verification of VKontakte through his manager.",
      "zh": "不过，杜罗夫没能找到确凿的证据来证明这位投资者通过这种方式授意其经理对VKontakte进行“测试”这一说法。",
      "ja": "とはいえ、投資家がマネージャーを通じてこのようにVKontakteの「テスト」を承認したという説を裏付ける、決定的な証拠をドゥーロフが入手することはできなかった。"
    },
    {
      "id": 5,
      "ru": "Первая встреча закончилась безоблачно.",
      "en": "The first meeting ended cloudlessly.",
      "zh": "第一次会面愉快地结束了。",
      "ja": "最初の会談は平穏に終わった。"
    },
    {
      "id": 6,
      "ru": "Дуров понравился Мильнеру.",
      "en": "Milner liked Durov.",
      "zh": "米尔纳喜欢杜罗夫。",
      "ja": "ミルナーはドゥーロフを気に入った。"
    },
    {
      "id": 7,
      "ru": "Человек в черном сознавал, как интернет меняет человеческую жизнь, какие потребности он может удовлетворить, и не стремился быстрее накосить денег.",
      "en": "The man in black realized how the Internet changes human life, what needs it can satisfy, and did not strive to mow down money faster.",
      "zh": "这个黑衣人意识到互联网如何改变人类生活，它能满足什么需求，并且不急于快速敛财。",
      "ja": "黒衣の男（ドゥーロフ）は、インターネットが人間の生活をどう変えるか、どのようなニーズを満たせるかを理解しており、手っ取り早く金を稼ぐことには執着していなかった。"
    },
    {
      "id": 8,
      "ru": "Последнее выглядело важным, так как Мильнер сознавал: проекты, выжимающие копейку, рано или поздно начинают бесить пользователя.",
      "en": "The latter looked important, as Milner realized: projects squeezing a penny sooner or later begin to infuriate the user.",
      "zh": "这一点看起来很重要，因为米尔纳明白：榨取每一分钱的项目迟早会惹恼用户。",
      "ja": "後者は重要だった。なぜならミルナーは、小銭を搾り取るようなプロジェクトは遅かれ早かれユーザーを激怒させることになるとわかっていたからだ。"
    },
    {
      "id": 9,
      "ru": "Летом речь зашла уже о конкретных условиях.",
      "en": "In the summer, the conversation turned to specific conditions.",
      "zh": "夏天，谈话已经涉及具体条件。",
      "ja": "夏には、具体的な条件についての話になった。"
    },
    {
      "id": 10,
      "ru": "Мильнер оценил «ВКонтакте» в 40 млн долларов.",
      "en": "Milner valued VKontakte at $40 million.",
      "zh": "米尔纳给VKontakte的估值是4000万美元。",
      "ja": "ミルナーはVKontakteを4000万ドルと評価した。"
    },
    {
      "id": 11,
      "ru": "Стороны начали торговлю – здесь на первый план вышел Слава.",
      "en": "The parties began bargaining – here Slava came to the fore.",
      "zh": "双方开始讨价还价——此时斯拉瓦出场了。",
      "ja": "双方は交渉を始めた――ここでスラヴァが前面に出てきた。"
    },
    {
      "id": 12,
      "ru": "Он заявил, что соцсеть стоит 60 млн.",
      "en": "He stated that the social network is worth 60 million.",
      "zh": "他宣称社交网络值6000万美元。",
      "ja": "彼は、ソーシャルネットワークには6000万ドルの価値があると主張した。"
    },
    {
      "id": 13,
      "ru": "Свои позиции он оборонял настолько яростно, что Мильнер согласился отдать 15 млн за 24,99 %.",
      "en": "He defended his positions so furiously that Milner agreed to give 15 million for 24.99%.",
      "zh": "他如此猛烈地捍卫自己的立场，以至于米尔纳同意出1500万美元换取24.99%的股份。",
      "ja": "彼があまりにも激しく自説を曲げなかったため、ミルナーは24.99%に対して1500万ドルを出すことに同意した。"
    },
    {
      "id": 14,
      "ru": "При этом капиталист выбил себе право на увеличение доли до 49 %.",
      "en": "At the same time, the capitalist secured the right to increase the share to 49%.",
      "zh": "同时，这位资本家为自己争取到了将股份增至49%的权利。",
      "ja": "同時に、この資本家はシェアを49%まで増やす権利を確保した。"
    },
    {
      "id": 15,
      "ru": "Сделку оформили быстро – изящный договор в стиле DST Deal был подписан в июле.",
      "en": "The deal was completed quickly – an elegant contract in the DST Deal style was signed in July.",
      "zh": "交易很快敲定——一份优雅的DST风格合同于七月签署。",
      "ja": "取引は迅速にまとめられた――DSTディール・スタイルの優雅な契約書が7月に署名された。"
    },
    {
      "id": 16,
      "ru": "Если бы теперь Перекопский спросил Дурова, где заработанный миллион, тот предъявил бы ему счета.",
      "en": "If Perekopsky now asked Durov where the earned million was, he would present him with the accounts.",
      "zh": "如果现在佩列科普斯基问杜罗夫赚到的一百万在哪里，他可以把账单拿给他看。",
      "ja": "もし今ペレコプスキーがドゥーロフに、稼いだ100万はどこにあるのかと尋ねたら、彼は口座を見せることができただろう。"
    },
    {
      "id": 17,
      "ru": "Но Перекопский вспомнил о споре нескоро – перспективы, нарисовавшиеся после альянса с Мильнером, ослепляли своим блеском сильнее золота.",
      "en": "But Perekopsky remembered the dispute not soon – the prospects that loomed after the alliance with Milner dazzled with their brilliance stronger than gold.",
      "zh": "但佩列科普斯基很久之后才想起这个赌约——与米尔纳结盟后展现出的前景，其光芒比黄金更耀眼。",
      "ja": "しかしペレコプスキーがその賭けのことを思い出したのは、ずいぶん後のことだった――ミルナーとの提携後に描かれた展望は、金よりも強くその輝きで目をくらませたからだ。"
    }
  ],
  "translator_notes": [
    "Durov's suspicion linking Milner's visits to DDoS attacks adds a layer of corporate intrigue.",
    "The valuation negotiation (40m vs 60m) shows Slava Mirilashvili's business acumen complementing Durov's vision.",
    "24.99% is a strategic number – just under a blocking stake (25%+1 share), keeping control with founders.",
    "The option to increase to 49% foreshadows future control battles.",
    "This chapter concludes the initial startup phase and sets the stage for scaling."
  ],
  "total_sentences": 17,
  "page_type": "narrative"
}

with open("translations/page_050.json", "w", encoding="utf-8") as f:
    json.dump(page_content, f, indent=2, ensure_ascii=False)
