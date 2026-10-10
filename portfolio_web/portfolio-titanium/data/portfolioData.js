/* ============================================================
   ВСІ ДАНІ САЙТУ. Верстку чіпати не треба.
   Нова робота = один новий рядок у works.
   img: "assets/works/назва.jpg"  (16:9, 1280x720). Порожній рядок = темна заглушка.
   Підключено як звичайний <script>, тому працює і без сервера.
   ============================================================ */
window.PORTFOLIO = {
  site: {
    // Куди веде кнопка "Замовити прев'ю"
    order: "#contact"
  },

  // Цифри для Bento-сітки (зараз приклади, постав свої реальні)
  stats: { ctr: "+13.4%", views: "30M+", speed: "24" },

  // Lottie для Bento-клітинки. Шлях до .lottie або .json з IconScout. "" = порожня рамка
  lottie: { bento: "" },

  // Софт у Bento. icon: шлях до .svg / .lottie з IconScout. "" = буквений значок
  tools: [
    { name: "Photoshop",     short: "Ps", icon: "" }
  ],

  // cat створює таб автоматично. views: приклади, заміни на реальні
  works: [
    { title: "Our New Golf Course",                                             cat: "IRL / Vlogs",     views: "1.2M", img: "assets/irl_1.jpg" },
    { title: "...",                                                             cat: "IRL / Vlogs",     views: "1.7M", img: "assets/after_2.jpg" },
    { title: "...",                                                             cat: "IRL / Vlogs",     views: "800K", img: "assets/after_3.jpg" },
    { title: "NEVER Say THIS When Pulled Over By Police!",                      cat: "IRL / Vlogs",     views: "860K", img: "assets/irl_2.jpg" },
    { title: "I Tried the New Gordon Ramsay Hell's Kitchen Restaurant",         cat: "IRL / Vlogs",     views: "540K", img: "assets/irl_3.png" },
    { title: "The Most Dangerous Robot Ever Created",                           cat: "IRL / Vlogs",     views: "1.1M", img: "assets/irl_4.jpg" },
    { title: "My drone filmed Rumi from Kpop Demon Hunters vs Squishy Dumpling in real life!",                    cat: "IRL / Vlogs",     views: "720K", img: "assets/irl_5.jpg" },
    { title: "Do Not Squeeze Squishies at 3am",                                 cat: "IRL / Vlogs",     views: "1.5m", img: "assets/irl_6.jpg" },
    { title: "I Ate at Chaiiwala Every Day for 1 Week",                         cat: "IRL / Vlogs",     views: "450K", img: "assets/irl_7.jpg" },
    { title: "...",                                                             cat: "IRL / Vlogs",     views: "550K", img: "assets/after_1.jpg" },
    { title: "...",            cat: "IRL / Vlogs",     views: "660K", img: "assets/irl_8.jpg" },
    { title: "I spent 7,000 hours looking at charts",       cat: "Business & Crypto", views: "980K", img: "assets/fin_1.jpg" },
    { title: "...",             cat: "Business & Crypto", views: "720K", img: "assets/fin_4.jpg" },
    { title: "...",             cat: "Business & Crypto", views: "360K", img: "assets/fin_3.jpg" },
    { title: "...",             cat: "Business & Crypto", views: "170K", img: "assets/fin_5.jpg" },
    { title: "...",                    cat: "Business & Crypto", views: "270K", img: "assets/fin_2.jpg" }
  ],

  // Пари До / Після (показується 3). before = сирий вихідник, after = готове прев'ю
  compare: [
    { title: "IRL / Vlogs",            before: "assets/before_4.png", after: "assets/irl_8.jpg" },
    { title: "IRL / Vlogs",       before: "assets/before_2.jpg", after: "assets/after_2.jpg" },
    { title: "IRL / Vlogs", before: "assets/before_3.jpg", after: "assets/after_3.jpg" }
  ],

  // handle копіюється кнопкою. Заміни Discord на свій
  socials: [
    { name: "Telegram",  url: "https://t.me/obla0chko",                   handle: "@obla0chko" },
    { name: "Twitter",   url: "https://x.com/obla0chko",       handle: "@obla0chko" },
    { name: "Instagram", url: "https://www.instagram.com/obla0chko.dsgn/",    handle: "@obla0chko.dsgn" },
    { name: "Behance",   url: "https://www.behance.net/def70fbe",         handle: "def70fbe" }
  ]
};
