const sites = [
  {
    name: "syxuanan.cn",
    home: "https://www.syxuanan.cn/",
    sitemap: "https://www.syxuanan.cn/sitemap.xml",
    categories: [
      { title: "okdoc-t1", url: "https://www.syxuanan.cn/okdoc/t1.html" },
      { title: "okdoc-t2", url: "https://www.syxuanan.cn/okdoc/t2.html" },
      { title: "okdoc-t3", url: "https://www.syxuanan.cn/okdoc/t3.html" },
      { title: "okdoc-t4", url: "https://www.syxuanan.cn/okdoc/t4.html" }
    ],
    content: {
      dir: "yeslookx", // 内容页目录
      min: 1,           // 最小 ID
      max: 84450       // 最大 ID
    }
  },
  {
    name: "newsite.com",
    home: "https://www.newsite.com/",
    sitemap: "https://www.newsite.com/sitemap.xml",
    categories: [
      { title: "category1", url: "https://www.newsite.com/category1.html" },
      { title: "category2", url: "https://www.newsite.com/category2.html" }
    ],
    content: {
      dir: "newsite_content", // 内容页目录
      min: 1,
      max: 10000
    }
  }
  // 可以继续添加其他站点
];
