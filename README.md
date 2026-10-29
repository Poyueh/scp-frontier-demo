# SCP Frontier — 林緣失聯前哨

[開始試玩](https://poyueh.github.io/scp-frontier-demo/) · [操作指南](https://poyueh.github.io/scp-frontier-demo/guide.html) · [v0.0.2 下載與紀錄](https://github.com/Poyueh/scp-frontier-demo/releases/tag/v0.0.2)

你是重建指揮官。啟動前哨、安排工程師、沿訊號探索廊道，取回脈衝裝置，再觀察並重新隔離 SCP-280。

v0.0.3 是視覺一致性驗測版，含繁體中文、简体中文與 English；統一角色、SCP-280、物件、互動提示與 UI 的像素視覺規範。建議電腦鍵盤遊玩；手機觸控、效能與新玩家盲測仍需驗證。

A／D 移動，同向雙按並按住衝刺；J／左鍵攻擊；E 互動與投入物資；K 脈衝；F 定向照明；Esc 暫停。進度儲存在目前瀏覽器和網站；清除網站資料會刪除紀錄。

## 來源與授權

SCP Frontier © 2026 Poyueh。本次公開的 SCP 衍生遊戲依 [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) 分享，包括成品中的自有編譯遊戲程式、原創像素表現、合成音效與指南；Godot 及字型保留各自授權。詳見 [LICENSE.txt](LICENSE.txt) 及成品隨附完整聲明。本庫的最小部署工具亦依 CC BY-SA 3.0 分享。

本作改編自 [SCP-280，Dr Gears，SCP Wiki](https://scp-wiki.wikidot.com/scp-280) 及 SCP Wiki 作者群的基金會概念，採 CC BY-SA 3.0；沒有使用條目照片或基金會標誌。定向光、暗室和外側控制柱為遊戲化場景，未模擬原文全部能力。本作為非官方作品。

## 版本成品

Release 提供完整 Web ZIP 與 SHA-256 校驗碼。解壓後需透過網站或本機 HTTP 服務開啟；不能直接雙擊遊戲 HTML。此倉庫維護公開成品、玩家文件與部署設定，開發來源維持於獨立私有倉庫。

## 驗測版部署

v0.0.3 線上驗測版以 `trial/current.json` 固定全部公開執行檔的 SHA-256 與大小；以已發佈的 v0.0.2 成品為基底，重建後必須逐檔符合完整匯出成品，否則停止部署。這是成品傳輸格式，不是在部署時修改遊戲原始碼。舊 Release ZIP 保留供下載；線上驗測版不代表已新增同版 Release ZIP。

部署仍僅使用既有的唯讀 contents 與 Pages 發佈權限。手動選擇舊 Release 的部署路徑維持不變；推送新的驗測版 manifest 才會觸發驗測成品部署。
