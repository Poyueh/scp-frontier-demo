# SCP Frontier — 失聯的第九哨站

[開始試玩](https://poyueh.github.io/scp-frontier-demo/) · [公開企劃書](https://poyueh.github.io/scp-frontier-demo/spec/) · [操作指南](https://poyueh.github.io/scp-frontier-demo/guide.html) · [v0.0.2 下載與紀錄](https://github.com/Poyueh/scp-frontier-demo/releases/tag/v0.0.2)

你是重建指揮官。啟動前哨、安排工程師、沿訊號探索廊道，取回脈衝裝置，再觀察並重新隔離 SCP-280。

v0.0.6 是「失聯的第九哨站」試玩版：直接載入遊戲主選單，從運輸車抵達、領取裝備與停電調查展開新開場；提供鍵盤、滑鼠與手機觸控操作。遊戲企劃規格、玩家圖文指南及來源授權可獨立閱讀。手機實機效能與畫面手感仍需驗測。

A／D 移動，同向雙按並按住衝刺；J／左鍵連斬；E 互動與投入能源晶；K 技能；Esc 暫停。手機使用畫面觸控區。進度保存在目前瀏覽器和網站；清除網站資料會刪除紀錄。

[舊版 v0.0.4 存檔入口](https://poyueh.github.io/scp-frontier-demo/legacy/v0.0.4/) 僅供選擇回到先前的試玩版。新版使用獨立存檔目錄，不覆寫舊版資料；未承諾跨版本自動遷移或已驗證舊存檔在所有瀏覽器均可讀取。

## 來源與授權

SCP Frontier © 2026 Poyueh。本次公開的 SCP 衍生遊戲依 [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) 分享，包括成品中的自有編譯遊戲程式、原創像素表現、合成音效與指南；Godot 及字型保留各自授權。詳見 [LICENSE.txt](LICENSE.txt) 及成品隨附完整聲明。本庫的最小部署工具亦依 CC BY-SA 3.0 分享。

本作改編自 [SCP-280，Dr Gears，SCP Wiki](https://scp-wiki.wikidot.com/scp-280) 及 SCP Wiki 作者群的基金會概念，採 CC BY-SA 3.0；沒有使用條目照片或基金會標誌。定向光、暗室和外側控制柱為遊戲化場景，未模擬原文全部能力。本作為非官方作品。

## 版本成品

Release 提供完整 Web ZIP 與 SHA-256 校驗碼。解壓後需透過網站或本機 HTTP 服務開啟；不能直接雙擊遊戲 HTML。此倉庫維護公開成品、玩家文件與部署設定，開發來源維持於獨立私有倉庫。

## 驗測版部署

`trial/current.json` 固定公開成品及基底 Release 的 SHA-256 與大小。部署只重建已測試的完整匯出成品；任何基底、片段或最終檔案不符即停止，不使用降級或寬鬆備援。歷史 Release ZIP 與授權聲明保留；線上試玩更新不代表同時新增可下載 Release ZIP。

部署沿用既有唯讀 contents 與 Pages 發佈權限。公開 `/spec/` 為隨版本產生並檢查同步的遊戲企劃書；不發布私有原始碼、開發歷史或內部驗測文件。
