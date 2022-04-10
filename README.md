# 捷運大富翁
一個老少咸宜的團康遊戲
> 拜託鞭小力一點q-q

[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=flat-square&logo=github&logoColor=white)](https://github.com/Forever-CodingNoob/metro-game) 
[![](https://img.shields.io/website?style=flat-square&url=https%3A%2F%2Fmetro-game.herokuapp.com%2F)](https://metro-game.herokuapp.com/)
[![](https://img.shields.io/github/v/release/Forever-CodingNoob/metro-game?style=flat-square)]()
[![Flask](https://img.shields.io/badge/made%20with-flask-%23000.svg?style=flat-square&logo=flask)]()
[![Redis](https://img.shields.io/badge/made%20with-redis-%23DD0031.svg?style=flat-square&logo=redis)]()
[![Postgres](https://img.shields.io/badge/made%20with-postgres-%23316192.svg?style=flat-square&logo=postgresql)]()
[![Heroku](https://img.shields.io/badge/deployed%20on-heroku-%23430098.svg?style=flat-square&logo=heroku)]()


## [遊戲規則](https://hackmd.io/@ForeverIdiot/metro-game)
## TODO
* [ ] 增加題目提交與審核功能
* [ ] 建立admin帳號
* [ ] 實作卡牌功能
* [ ] 使用 google api偵測玩家位置，以便確保玩家真的到達了站點
* [ ] 自訂遊戲參數(如遊玩時間、隱藏軌開放時間等等)
* [ ] 將隊隨工作自動化
* [ ] 實作車站組合紀錄
* [ ] 防範sql injection   
* [ ] 找到時間做上面這些目標

## 注意
* 使用redislab提供的redis資料庫儲存session
* 使用heroku提供的postgresql server(aws)儲存遊玩資料