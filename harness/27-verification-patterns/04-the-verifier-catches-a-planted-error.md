---
type: task
title: "The verifier catches a planted error"
minutes: 10
---

## Set up

`incident.log` is the search service's log from the morning of the incident. `summary.json` is what an agent produced from it:

```json
{"first_error": "09:11:00", "error_count": 312, "peak_latency_ms": 4888, "deploy": "v2.3.1"}
```

One of those four values is wrong - planted on purpose.

```bash
mkdir -p /root/harness-lab/27-verify
cd /root/harness-lab/27-verify
cat > incident.log <<'EOF'
2026-03-14T08:30:00Z INFO deploy: search v2.3.0 rolled out
2026-03-14T09:00:00Z INFO search: GET /api/items/0 200 20ms
2026-03-14T09:00:03Z INFO search: GET /api/items/1 200 21ms
2026-03-14T09:00:06Z INFO search: GET /api/items/2 200 22ms
2026-03-14T09:00:09Z INFO search: GET /api/items/3 200 23ms
2026-03-14T09:00:12Z INFO search: GET /api/items/4 200 24ms
2026-03-14T09:00:15Z INFO search: GET /api/items/5 200 25ms
2026-03-14T09:00:18Z INFO search: GET /api/items/6 200 26ms
2026-03-14T09:00:21Z INFO search: GET /api/items/7 200 27ms
2026-03-14T09:00:24Z INFO search: GET /api/items/8 200 28ms
2026-03-14T09:00:27Z INFO search: GET /api/items/9 200 29ms
2026-03-14T09:00:30Z INFO search: GET /api/items/10 200 30ms
2026-03-14T09:00:33Z INFO search: GET /api/items/11 200 31ms
2026-03-14T09:00:36Z INFO search: GET /api/items/12 200 32ms
2026-03-14T09:00:39Z INFO search: GET /api/items/13 200 33ms
2026-03-14T09:00:42Z INFO search: GET /api/items/14 200 34ms
2026-03-14T09:00:45Z INFO search: GET /api/items/15 200 35ms
2026-03-14T09:00:48Z INFO search: GET /api/items/16 200 36ms
2026-03-14T09:00:51Z INFO search: GET /api/items/17 200 37ms
2026-03-14T09:00:54Z INFO search: GET /api/items/18 200 38ms
2026-03-14T09:00:57Z INFO search: GET /api/items/19 200 39ms
2026-03-14T09:01:00Z INFO search: GET /api/items/20 200 40ms
2026-03-14T09:01:03Z INFO search: GET /api/items/21 200 41ms
2026-03-14T09:01:06Z INFO search: GET /api/items/22 200 42ms
2026-03-14T09:01:09Z INFO search: GET /api/items/23 200 43ms
2026-03-14T09:01:12Z INFO search: GET /api/items/24 200 44ms
2026-03-14T09:01:15Z INFO search: GET /api/items/25 200 45ms
2026-03-14T09:01:18Z INFO search: GET /api/items/26 200 46ms
2026-03-14T09:01:21Z INFO search: GET /api/items/27 200 47ms
2026-03-14T09:01:24Z INFO search: GET /api/items/28 200 48ms
2026-03-14T09:01:27Z INFO search: GET /api/items/29 200 49ms
2026-03-14T09:01:30Z INFO search: GET /api/items/30 200 50ms
2026-03-14T09:01:33Z INFO search: GET /api/items/31 200 51ms
2026-03-14T09:01:36Z INFO search: GET /api/items/32 200 52ms
2026-03-14T09:01:39Z INFO search: GET /api/items/33 200 53ms
2026-03-14T09:01:42Z INFO search: GET /api/items/34 200 54ms
2026-03-14T09:01:45Z INFO search: GET /api/items/35 200 55ms
2026-03-14T09:01:48Z INFO search: GET /api/items/36 200 56ms
2026-03-14T09:01:51Z INFO search: GET /api/items/37 200 57ms
2026-03-14T09:01:54Z INFO search: GET /api/items/38 200 58ms
2026-03-14T09:01:57Z INFO search: GET /api/items/39 200 59ms
2026-03-14T09:02:00Z INFO search: GET /api/items/40 200 20ms
2026-03-14T09:02:03Z INFO search: GET /api/items/41 200 21ms
2026-03-14T09:02:06Z INFO search: GET /api/items/42 200 22ms
2026-03-14T09:02:09Z INFO search: GET /api/items/43 200 23ms
2026-03-14T09:02:12Z INFO search: GET /api/items/44 200 24ms
2026-03-14T09:02:15Z INFO search: GET /api/items/45 200 25ms
2026-03-14T09:02:18Z INFO search: GET /api/items/46 200 26ms
2026-03-14T09:02:21Z INFO search: GET /api/items/47 200 27ms
2026-03-14T09:02:24Z INFO search: GET /api/items/48 200 28ms
2026-03-14T09:02:27Z INFO search: GET /api/items/49 200 29ms
2026-03-14T09:02:30Z INFO search: GET /api/items/50 200 30ms
2026-03-14T09:02:33Z INFO search: GET /api/items/51 200 31ms
2026-03-14T09:02:36Z INFO search: GET /api/items/52 200 32ms
2026-03-14T09:02:39Z INFO search: GET /api/items/53 200 33ms
2026-03-14T09:02:42Z INFO search: GET /api/items/54 200 34ms
2026-03-14T09:02:45Z INFO search: GET /api/items/55 200 35ms
2026-03-14T09:02:48Z INFO search: GET /api/items/56 200 36ms
2026-03-14T09:02:51Z INFO search: GET /api/items/57 200 37ms
2026-03-14T09:02:54Z INFO search: GET /api/items/58 200 38ms
2026-03-14T09:02:57Z INFO search: GET /api/items/59 200 39ms
2026-03-14T09:03:00Z INFO search: GET /api/items/60 200 40ms
2026-03-14T09:03:03Z INFO search: GET /api/items/61 200 41ms
2026-03-14T09:03:06Z INFO search: GET /api/items/62 200 42ms
2026-03-14T09:03:09Z INFO search: GET /api/items/63 200 43ms
2026-03-14T09:03:12Z INFO search: GET /api/items/64 200 44ms
2026-03-14T09:03:15Z INFO search: GET /api/items/65 200 45ms
2026-03-14T09:03:18Z INFO search: GET /api/items/66 200 46ms
2026-03-14T09:03:21Z INFO search: GET /api/items/67 200 47ms
2026-03-14T09:03:24Z INFO search: GET /api/items/68 200 48ms
2026-03-14T09:03:27Z INFO search: GET /api/items/69 200 49ms
2026-03-14T09:03:30Z INFO search: GET /api/items/70 200 50ms
2026-03-14T09:03:33Z INFO search: GET /api/items/71 200 51ms
2026-03-14T09:03:36Z INFO search: GET /api/items/72 200 52ms
2026-03-14T09:03:39Z INFO search: GET /api/items/73 200 53ms
2026-03-14T09:03:42Z INFO search: GET /api/items/74 200 54ms
2026-03-14T09:03:45Z INFO search: GET /api/items/75 200 55ms
2026-03-14T09:03:48Z INFO search: GET /api/items/76 200 56ms
2026-03-14T09:03:51Z INFO search: GET /api/items/77 200 57ms
2026-03-14T09:03:54Z INFO search: GET /api/items/78 200 58ms
2026-03-14T09:03:57Z INFO search: GET /api/items/79 200 59ms
2026-03-14T09:04:00Z INFO search: GET /api/items/80 200 20ms
2026-03-14T09:04:03Z INFO search: GET /api/items/81 200 21ms
2026-03-14T09:04:06Z INFO search: GET /api/items/82 200 22ms
2026-03-14T09:04:09Z INFO search: GET /api/items/83 200 23ms
2026-03-14T09:04:12Z INFO search: GET /api/items/84 200 24ms
2026-03-14T09:04:15Z INFO search: GET /api/items/85 200 25ms
2026-03-14T09:04:18Z INFO search: GET /api/items/86 200 26ms
2026-03-14T09:04:21Z INFO search: GET /api/items/87 200 27ms
2026-03-14T09:04:24Z INFO search: GET /api/items/88 200 28ms
2026-03-14T09:04:27Z INFO search: GET /api/items/89 200 29ms
2026-03-14T09:04:30Z INFO search: GET /api/items/90 200 30ms
2026-03-14T09:04:33Z INFO search: GET /api/items/91 200 31ms
2026-03-14T09:04:36Z INFO search: GET /api/items/92 200 32ms
2026-03-14T09:04:39Z INFO search: GET /api/items/93 200 33ms
2026-03-14T09:04:42Z INFO search: GET /api/items/94 200 34ms
2026-03-14T09:04:45Z INFO search: GET /api/items/95 200 35ms
2026-03-14T09:04:48Z INFO search: GET /api/items/96 200 36ms
2026-03-14T09:04:51Z INFO search: GET /api/items/97 200 37ms
2026-03-14T09:04:54Z INFO search: GET /api/items/98 200 38ms
2026-03-14T09:04:57Z INFO search: GET /api/items/99 200 39ms
2026-03-14T09:05:00Z INFO deploy: search v2.3.1 rolled out
2026-03-14T09:05:00Z INFO search: GET /api/items/100 200 40ms
2026-03-14T09:05:03Z INFO search: GET /api/items/101 200 41ms
2026-03-14T09:05:06Z INFO search: GET /api/items/102 200 42ms
2026-03-14T09:05:09Z INFO search: GET /api/items/103 200 43ms
2026-03-14T09:05:12Z INFO search: GET /api/items/104 200 44ms
2026-03-14T09:05:15Z INFO search: GET /api/items/105 200 45ms
2026-03-14T09:05:18Z INFO search: GET /api/items/106 200 46ms
2026-03-14T09:05:21Z INFO search: GET /api/items/107 200 47ms
2026-03-14T09:05:24Z INFO search: GET /api/items/108 200 48ms
2026-03-14T09:05:27Z INFO search: GET /api/items/109 200 49ms
2026-03-14T09:05:30Z INFO search: GET /api/items/110 200 50ms
2026-03-14T09:05:33Z INFO search: GET /api/items/111 200 51ms
2026-03-14T09:05:36Z INFO search: GET /api/items/112 200 52ms
2026-03-14T09:05:39Z INFO search: GET /api/items/113 200 53ms
2026-03-14T09:05:42Z INFO search: GET /api/items/114 200 54ms
2026-03-14T09:05:45Z INFO search: GET /api/items/115 200 55ms
2026-03-14T09:05:48Z INFO search: GET /api/items/116 200 56ms
2026-03-14T09:05:51Z INFO search: GET /api/items/117 200 57ms
2026-03-14T09:05:54Z INFO search: GET /api/items/118 200 58ms
2026-03-14T09:05:57Z INFO search: GET /api/items/119 200 59ms
2026-03-14T09:06:00Z INFO search: GET /api/items/120 200 20ms
2026-03-14T09:06:03Z INFO search: GET /api/items/121 200 21ms
2026-03-14T09:06:06Z INFO search: GET /api/items/122 200 22ms
2026-03-14T09:06:09Z INFO search: GET /api/items/123 200 23ms
2026-03-14T09:06:12Z INFO search: GET /api/items/124 200 24ms
2026-03-14T09:06:15Z INFO search: GET /api/items/125 200 25ms
2026-03-14T09:06:18Z INFO search: GET /api/items/126 200 26ms
2026-03-14T09:06:21Z INFO search: GET /api/items/127 200 27ms
2026-03-14T09:06:24Z INFO search: GET /api/items/128 200 28ms
2026-03-14T09:06:27Z INFO search: GET /api/items/129 200 29ms
2026-03-14T09:06:30Z INFO search: GET /api/items/130 200 30ms
2026-03-14T09:06:33Z INFO search: GET /api/items/131 200 31ms
2026-03-14T09:06:36Z INFO search: GET /api/items/132 200 32ms
2026-03-14T09:06:39Z INFO search: GET /api/items/133 200 33ms
2026-03-14T09:06:42Z INFO search: GET /api/items/134 200 34ms
2026-03-14T09:06:45Z INFO search: GET /api/items/135 200 35ms
2026-03-14T09:06:48Z INFO search: GET /api/items/136 200 36ms
2026-03-14T09:06:51Z INFO search: GET /api/items/137 200 37ms
2026-03-14T09:06:54Z INFO search: GET /api/items/138 200 38ms
2026-03-14T09:06:57Z INFO search: GET /api/items/139 200 39ms
2026-03-14T09:07:00Z INFO search: GET /api/items/140 200 40ms
2026-03-14T09:07:03Z INFO search: GET /api/items/141 200 41ms
2026-03-14T09:07:06Z INFO search: GET /api/items/142 200 42ms
2026-03-14T09:07:09Z INFO search: GET /api/items/143 200 43ms
2026-03-14T09:07:12Z INFO search: GET /api/items/144 200 44ms
2026-03-14T09:07:15Z INFO search: GET /api/items/145 200 45ms
2026-03-14T09:07:18Z INFO search: GET /api/items/146 200 46ms
2026-03-14T09:07:21Z INFO search: GET /api/items/147 200 47ms
2026-03-14T09:07:24Z INFO search: GET /api/items/148 200 48ms
2026-03-14T09:07:27Z INFO search: GET /api/items/149 200 49ms
2026-03-14T09:07:30Z INFO search: GET /api/items/150 200 50ms
2026-03-14T09:07:33Z INFO search: GET /api/items/151 200 51ms
2026-03-14T09:07:36Z INFO search: GET /api/items/152 200 52ms
2026-03-14T09:07:39Z INFO search: GET /api/items/153 200 53ms
2026-03-14T09:07:42Z INFO search: GET /api/items/154 200 54ms
2026-03-14T09:07:45Z INFO search: GET /api/items/155 200 55ms
2026-03-14T09:07:48Z INFO search: GET /api/items/156 200 56ms
2026-03-14T09:07:51Z INFO search: GET /api/items/157 200 57ms
2026-03-14T09:07:54Z INFO search: GET /api/items/158 200 58ms
2026-03-14T09:07:57Z INFO search: GET /api/items/159 200 59ms
2026-03-14T09:08:00Z INFO search: GET /api/items/160 200 20ms
2026-03-14T09:08:03Z INFO search: GET /api/items/161 200 21ms
2026-03-14T09:08:06Z INFO search: GET /api/items/162 200 22ms
2026-03-14T09:08:09Z INFO search: GET /api/items/163 200 23ms
2026-03-14T09:08:12Z INFO search: GET /api/items/164 200 24ms
2026-03-14T09:08:15Z INFO search: GET /api/items/165 200 25ms
2026-03-14T09:08:18Z INFO search: GET /api/items/166 200 26ms
2026-03-14T09:08:21Z INFO search: GET /api/items/167 200 27ms
2026-03-14T09:08:24Z INFO search: GET /api/items/168 200 28ms
2026-03-14T09:08:27Z INFO search: GET /api/items/169 200 29ms
2026-03-14T09:08:30Z INFO search: GET /api/items/170 200 30ms
2026-03-14T09:08:33Z INFO search: GET /api/items/171 200 31ms
2026-03-14T09:08:36Z INFO search: GET /api/items/172 200 32ms
2026-03-14T09:08:39Z INFO search: GET /api/items/173 200 33ms
2026-03-14T09:08:42Z INFO search: GET /api/items/174 200 34ms
2026-03-14T09:08:45Z INFO search: GET /api/items/175 200 35ms
2026-03-14T09:08:48Z INFO search: GET /api/items/176 200 36ms
2026-03-14T09:08:51Z INFO search: GET /api/items/177 200 37ms
2026-03-14T09:08:54Z INFO search: GET /api/items/178 200 38ms
2026-03-14T09:08:57Z INFO search: GET /api/items/179 200 39ms
2026-03-14T09:09:00Z INFO search: GET /api/items/180 200 40ms
2026-03-14T09:09:03Z INFO search: GET /api/items/181 200 41ms
2026-03-14T09:09:06Z INFO search: GET /api/items/182 200 42ms
2026-03-14T09:09:09Z INFO search: GET /api/items/183 200 43ms
2026-03-14T09:09:12Z INFO search: GET /api/items/184 200 44ms
2026-03-14T09:09:15Z INFO search: GET /api/items/185 200 45ms
2026-03-14T09:09:18Z INFO search: GET /api/items/186 200 46ms
2026-03-14T09:09:21Z INFO search: GET /api/items/187 200 47ms
2026-03-14T09:09:24Z INFO search: GET /api/items/188 200 48ms
2026-03-14T09:09:27Z INFO search: GET /api/items/189 200 49ms
2026-03-14T09:09:30Z INFO search: GET /api/items/190 200 50ms
2026-03-14T09:09:33Z INFO search: GET /api/items/191 200 51ms
2026-03-14T09:09:36Z INFO search: GET /api/items/192 200 52ms
2026-03-14T09:09:39Z INFO search: GET /api/items/193 200 53ms
2026-03-14T09:09:42Z INFO search: GET /api/items/194 200 54ms
2026-03-14T09:09:45Z INFO search: GET /api/items/195 200 55ms
2026-03-14T09:09:48Z INFO search: GET /api/items/196 200 56ms
2026-03-14T09:09:51Z INFO search: GET /api/items/197 200 57ms
2026-03-14T09:09:54Z INFO search: GET /api/items/198 200 58ms
2026-03-14T09:09:57Z INFO search: GET /api/items/199 200 59ms
2026-03-14T09:10:00Z INFO search: GET /api/items/200 200 20ms
2026-03-14T09:10:03Z INFO search: GET /api/items/201 200 21ms
2026-03-14T09:10:06Z INFO search: GET /api/items/202 200 22ms
2026-03-14T09:10:09Z INFO search: GET /api/items/203 200 23ms
2026-03-14T09:10:12Z INFO search: GET /api/items/204 200 24ms
2026-03-14T09:10:15Z INFO search: GET /api/items/205 200 25ms
2026-03-14T09:10:18Z INFO search: GET /api/items/206 200 26ms
2026-03-14T09:10:21Z INFO search: GET /api/items/207 200 27ms
2026-03-14T09:10:24Z INFO search: GET /api/items/208 200 28ms
2026-03-14T09:10:27Z INFO search: GET /api/items/209 200 29ms
2026-03-14T09:10:30Z INFO search: GET /api/items/210 200 30ms
2026-03-14T09:10:33Z INFO search: GET /api/items/211 200 31ms
2026-03-14T09:10:36Z INFO search: GET /api/items/212 200 32ms
2026-03-14T09:10:39Z INFO search: GET /api/items/213 200 33ms
2026-03-14T09:10:42Z INFO search: GET /api/items/214 200 34ms
2026-03-14T09:10:45Z INFO search: GET /api/items/215 200 35ms
2026-03-14T09:10:48Z INFO search: GET /api/items/216 200 36ms
2026-03-14T09:10:51Z INFO search: GET /api/items/217 200 37ms
2026-03-14T09:10:54Z INFO search: GET /api/items/218 200 38ms
2026-03-14T09:10:57Z INFO search: GET /api/items/219 200 39ms
2026-03-14T09:11:00Z ERROR search: GET /api/items/220 500 1040ms
2026-03-14T09:11:03Z ERROR search: GET /api/items/221 500 1077ms
2026-03-14T09:11:06Z ERROR search: GET /api/items/222 500 1114ms
2026-03-14T09:11:09Z ERROR search: GET /api/items/223 500 1151ms
2026-03-14T09:11:12Z ERROR search: GET /api/items/224 500 1188ms
2026-03-14T09:11:15Z ERROR search: GET /api/items/225 500 1225ms
2026-03-14T09:11:18Z ERROR search: GET /api/items/226 500 1262ms
2026-03-14T09:11:21Z ERROR search: GET /api/items/227 500 1299ms
2026-03-14T09:11:24Z ERROR search: GET /api/items/228 500 1336ms
2026-03-14T09:11:27Z ERROR search: GET /api/items/229 500 1373ms
2026-03-14T09:11:30Z ERROR search: GET /api/items/230 500 1410ms
2026-03-14T09:11:33Z ERROR search: GET /api/items/231 500 1447ms
2026-03-14T09:11:36Z ERROR search: GET /api/items/232 500 1484ms
2026-03-14T09:11:39Z ERROR search: GET /api/items/233 500 1521ms
2026-03-14T09:11:42Z ERROR search: GET /api/items/234 500 1558ms
2026-03-14T09:11:45Z ERROR search: GET /api/items/235 500 1595ms
2026-03-14T09:11:48Z ERROR search: GET /api/items/236 500 1632ms
2026-03-14T09:11:51Z ERROR search: GET /api/items/237 500 1669ms
2026-03-14T09:11:54Z ERROR search: GET /api/items/238 500 1706ms
2026-03-14T09:11:57Z ERROR search: GET /api/items/239 500 1743ms
2026-03-14T09:12:00Z ERROR search: GET /api/items/240 500 1780ms
2026-03-14T09:12:03Z ERROR search: GET /api/items/241 500 1817ms
2026-03-14T09:12:06Z ERROR search: GET /api/items/242 500 1854ms
2026-03-14T09:12:09Z ERROR search: GET /api/items/243 500 1891ms
2026-03-14T09:12:12Z ERROR search: GET /api/items/244 500 1928ms
2026-03-14T09:12:15Z ERROR search: GET /api/items/245 500 1965ms
2026-03-14T09:12:18Z ERROR search: GET /api/items/246 500 2002ms
2026-03-14T09:12:21Z ERROR search: GET /api/items/247 500 2039ms
2026-03-14T09:12:24Z ERROR search: GET /api/items/248 500 2076ms
2026-03-14T09:12:27Z ERROR search: GET /api/items/249 500 2113ms
2026-03-14T09:12:30Z ERROR search: GET /api/items/250 500 2150ms
2026-03-14T09:12:33Z ERROR search: GET /api/items/251 500 2187ms
2026-03-14T09:12:36Z ERROR search: GET /api/items/252 500 2224ms
2026-03-14T09:12:39Z ERROR search: GET /api/items/253 500 2261ms
2026-03-14T09:12:42Z ERROR search: GET /api/items/254 500 2298ms
2026-03-14T09:12:45Z ERROR search: GET /api/items/255 500 2335ms
2026-03-14T09:12:48Z ERROR search: GET /api/items/256 500 2372ms
2026-03-14T09:12:51Z ERROR search: GET /api/items/257 500 2409ms
2026-03-14T09:12:54Z ERROR search: GET /api/items/258 500 2446ms
2026-03-14T09:12:57Z ERROR search: GET /api/items/259 500 2483ms
2026-03-14T09:13:00Z ERROR search: GET /api/items/260 500 2520ms
2026-03-14T09:13:03Z ERROR search: GET /api/items/261 500 2557ms
2026-03-14T09:13:06Z ERROR search: GET /api/items/262 500 2594ms
2026-03-14T09:13:09Z ERROR search: GET /api/items/263 500 2631ms
2026-03-14T09:13:12Z ERROR search: GET /api/items/264 500 2668ms
2026-03-14T09:13:15Z ERROR search: GET /api/items/265 500 2705ms
2026-03-14T09:13:18Z ERROR search: GET /api/items/266 500 2742ms
2026-03-14T09:13:21Z ERROR search: GET /api/items/267 500 2779ms
2026-03-14T09:13:24Z ERROR search: GET /api/items/268 500 2816ms
2026-03-14T09:13:27Z ERROR search: GET /api/items/269 500 2853ms
2026-03-14T09:13:30Z ERROR search: GET /api/items/270 500 2890ms
2026-03-14T09:13:33Z ERROR search: GET /api/items/271 500 2927ms
2026-03-14T09:13:36Z ERROR search: GET /api/items/272 500 2964ms
2026-03-14T09:13:39Z ERROR search: GET /api/items/273 500 3001ms
2026-03-14T09:13:42Z ERROR search: GET /api/items/274 500 3038ms
2026-03-14T09:13:45Z ERROR search: GET /api/items/275 500 3075ms
2026-03-14T09:13:48Z ERROR search: GET /api/items/276 500 3112ms
2026-03-14T09:13:51Z ERROR search: GET /api/items/277 500 3149ms
2026-03-14T09:13:54Z ERROR search: GET /api/items/278 500 3186ms
2026-03-14T09:13:57Z ERROR search: GET /api/items/279 500 3223ms
2026-03-14T09:14:00Z ERROR search: GET /api/items/280 500 3260ms
2026-03-14T09:14:03Z ERROR search: GET /api/items/281 500 3297ms
2026-03-14T09:14:06Z ERROR search: GET /api/items/282 500 3334ms
2026-03-14T09:14:09Z ERROR search: GET /api/items/283 500 3371ms
2026-03-14T09:14:12Z ERROR search: GET /api/items/284 500 3408ms
2026-03-14T09:14:15Z ERROR search: GET /api/items/285 500 3445ms
2026-03-14T09:14:18Z ERROR search: GET /api/items/286 500 3482ms
2026-03-14T09:14:21Z ERROR search: GET /api/items/287 500 3519ms
2026-03-14T09:14:24Z ERROR search: GET /api/items/288 500 3556ms
2026-03-14T09:14:27Z ERROR search: GET /api/items/289 500 3593ms
2026-03-14T09:14:30Z ERROR search: GET /api/items/290 500 3630ms
2026-03-14T09:14:33Z ERROR search: GET /api/items/291 500 3667ms
2026-03-14T09:14:36Z ERROR search: GET /api/items/292 500 3704ms
2026-03-14T09:14:39Z ERROR search: GET /api/items/293 500 3741ms
2026-03-14T09:14:42Z ERROR search: GET /api/items/294 500 3778ms
2026-03-14T09:14:45Z ERROR search: GET /api/items/295 500 3815ms
2026-03-14T09:14:48Z ERROR search: GET /api/items/296 500 3852ms
2026-03-14T09:14:51Z ERROR search: GET /api/items/297 500 3889ms
2026-03-14T09:14:54Z ERROR search: GET /api/items/298 500 3926ms
2026-03-14T09:14:57Z ERROR search: GET /api/items/299 500 3963ms
2026-03-14T09:15:00Z ERROR search: GET /api/items/300 500 4000ms
2026-03-14T09:15:03Z ERROR search: GET /api/items/301 500 4037ms
2026-03-14T09:15:06Z ERROR search: GET /api/items/302 500 4074ms
2026-03-14T09:15:09Z ERROR search: GET /api/items/303 500 4111ms
2026-03-14T09:15:12Z ERROR search: GET /api/items/304 500 4148ms
2026-03-14T09:15:15Z ERROR search: GET /api/items/305 500 4185ms
2026-03-14T09:15:18Z ERROR search: GET /api/items/306 500 4222ms
2026-03-14T09:15:21Z ERROR search: GET /api/items/307 500 4259ms
2026-03-14T09:15:24Z ERROR search: GET /api/items/308 500 4296ms
2026-03-14T09:15:27Z ERROR search: GET /api/items/309 500 4333ms
2026-03-14T09:15:30Z ERROR search: GET /api/items/310 500 4370ms
2026-03-14T09:15:33Z ERROR search: GET /api/items/311 500 4407ms
2026-03-14T09:15:36Z ERROR search: GET /api/items/312 500 4444ms
2026-03-14T09:15:39Z ERROR search: GET /api/items/313 500 4481ms
2026-03-14T09:15:42Z ERROR search: GET /api/items/314 500 4518ms
2026-03-14T09:15:45Z ERROR search: GET /api/items/315 500 4555ms
2026-03-14T09:15:48Z ERROR search: GET /api/items/316 500 4592ms
2026-03-14T09:15:51Z ERROR search: GET /api/items/317 500 4629ms
2026-03-14T09:15:54Z ERROR search: GET /api/items/318 500 4666ms
2026-03-14T09:15:57Z ERROR search: GET /api/items/319 500 4703ms
2026-03-14T09:16:00Z ERROR search: GET /api/items/320 500 4740ms
2026-03-14T09:16:03Z ERROR search: GET /api/items/321 500 4777ms
2026-03-14T09:16:06Z ERROR search: GET /api/items/322 500 4814ms
2026-03-14T09:16:09Z ERROR search: GET /api/items/323 500 4851ms
2026-03-14T09:16:12Z ERROR search: GET /api/items/324 500 4888ms
2026-03-14T09:16:15Z ERROR search: GET /api/items/325 500 925ms
2026-03-14T09:16:18Z ERROR search: GET /api/items/326 500 962ms
2026-03-14T09:16:21Z ERROR search: GET /api/items/327 500 999ms
2026-03-14T09:16:24Z ERROR search: GET /api/items/328 500 1036ms
2026-03-14T09:16:27Z ERROR search: GET /api/items/329 500 1073ms
2026-03-14T09:16:30Z ERROR search: GET /api/items/330 500 1110ms
2026-03-14T09:16:33Z ERROR search: GET /api/items/331 500 1147ms
2026-03-14T09:16:36Z ERROR search: GET /api/items/332 500 1184ms
2026-03-14T09:16:39Z ERROR search: GET /api/items/333 500 1221ms
2026-03-14T09:16:42Z ERROR search: GET /api/items/334 500 1258ms
2026-03-14T09:16:45Z ERROR search: GET /api/items/335 500 1295ms
2026-03-14T09:16:48Z ERROR search: GET /api/items/336 500 1332ms
2026-03-14T09:16:51Z ERROR search: GET /api/items/337 500 1369ms
2026-03-14T09:16:54Z ERROR search: GET /api/items/338 500 1406ms
2026-03-14T09:16:57Z ERROR search: GET /api/items/339 500 1443ms
2026-03-14T09:17:00Z ERROR search: GET /api/items/340 500 1480ms
2026-03-14T09:17:03Z ERROR search: GET /api/items/341 500 1517ms
2026-03-14T09:17:06Z ERROR search: GET /api/items/342 500 1554ms
2026-03-14T09:17:09Z ERROR search: GET /api/items/343 500 1591ms
2026-03-14T09:17:12Z ERROR search: GET /api/items/344 500 1628ms
2026-03-14T09:17:15Z ERROR search: GET /api/items/345 500 1665ms
2026-03-14T09:17:18Z ERROR search: GET /api/items/346 500 1702ms
2026-03-14T09:17:21Z ERROR search: GET /api/items/347 500 1739ms
2026-03-14T09:17:24Z ERROR search: GET /api/items/348 500 1776ms
2026-03-14T09:17:27Z ERROR search: GET /api/items/349 500 1813ms
2026-03-14T09:17:30Z ERROR search: GET /api/items/350 500 1850ms
2026-03-14T09:17:33Z ERROR search: GET /api/items/351 500 1887ms
2026-03-14T09:17:36Z ERROR search: GET /api/items/352 500 1924ms
2026-03-14T09:17:39Z ERROR search: GET /api/items/353 500 1961ms
2026-03-14T09:17:42Z ERROR search: GET /api/items/354 500 1998ms
2026-03-14T09:17:45Z ERROR search: GET /api/items/355 500 2035ms
2026-03-14T09:17:48Z ERROR search: GET /api/items/356 500 2072ms
2026-03-14T09:17:51Z ERROR search: GET /api/items/357 500 2109ms
2026-03-14T09:17:54Z ERROR search: GET /api/items/358 500 2146ms
2026-03-14T09:17:57Z ERROR search: GET /api/items/359 500 2183ms
2026-03-14T09:18:00Z ERROR search: GET /api/items/360 500 2220ms
2026-03-14T09:18:03Z ERROR search: GET /api/items/361 500 2257ms
2026-03-14T09:18:06Z ERROR search: GET /api/items/362 500 2294ms
2026-03-14T09:18:09Z ERROR search: GET /api/items/363 500 2331ms
2026-03-14T09:18:12Z ERROR search: GET /api/items/364 500 2368ms
2026-03-14T09:18:15Z ERROR search: GET /api/items/365 500 2405ms
2026-03-14T09:18:18Z ERROR search: GET /api/items/366 500 2442ms
2026-03-14T09:18:21Z ERROR search: GET /api/items/367 500 2479ms
2026-03-14T09:18:24Z ERROR search: GET /api/items/368 500 2516ms
2026-03-14T09:18:27Z ERROR search: GET /api/items/369 500 2553ms
2026-03-14T09:18:30Z ERROR search: GET /api/items/370 500 2590ms
2026-03-14T09:18:33Z ERROR search: GET /api/items/371 500 2627ms
2026-03-14T09:18:36Z ERROR search: GET /api/items/372 500 2664ms
2026-03-14T09:18:39Z ERROR search: GET /api/items/373 500 2701ms
2026-03-14T09:18:42Z ERROR search: GET /api/items/374 500 2738ms
2026-03-14T09:18:45Z ERROR search: GET /api/items/375 500 2775ms
2026-03-14T09:18:48Z ERROR search: GET /api/items/376 500 2812ms
2026-03-14T09:18:51Z ERROR search: GET /api/items/377 500 2849ms
2026-03-14T09:18:54Z ERROR search: GET /api/items/378 500 2886ms
2026-03-14T09:18:57Z ERROR search: GET /api/items/379 500 2923ms
2026-03-14T09:19:00Z ERROR search: GET /api/items/380 500 2960ms
2026-03-14T09:19:03Z ERROR search: GET /api/items/381 500 2997ms
2026-03-14T09:19:06Z ERROR search: GET /api/items/382 500 3034ms
2026-03-14T09:19:09Z ERROR search: GET /api/items/383 500 3071ms
2026-03-14T09:19:12Z ERROR search: GET /api/items/384 500 3108ms
2026-03-14T09:19:15Z ERROR search: GET /api/items/385 500 3145ms
2026-03-14T09:19:18Z ERROR search: GET /api/items/386 500 3182ms
2026-03-14T09:19:21Z ERROR search: GET /api/items/387 500 3219ms
2026-03-14T09:19:24Z ERROR search: GET /api/items/388 500 3256ms
2026-03-14T09:19:27Z ERROR search: GET /api/items/389 500 3293ms
2026-03-14T09:19:30Z ERROR search: GET /api/items/390 500 3330ms
2026-03-14T09:19:33Z ERROR search: GET /api/items/391 500 3367ms
2026-03-14T09:19:36Z ERROR search: GET /api/items/392 500 3404ms
2026-03-14T09:19:39Z ERROR search: GET /api/items/393 500 3441ms
2026-03-14T09:19:42Z ERROR search: GET /api/items/394 500 3478ms
2026-03-14T09:19:45Z ERROR search: GET /api/items/395 500 3515ms
2026-03-14T09:19:48Z ERROR search: GET /api/items/396 500 3552ms
2026-03-14T09:19:51Z ERROR search: GET /api/items/397 500 3589ms
2026-03-14T09:19:54Z ERROR search: GET /api/items/398 500 3626ms
2026-03-14T09:19:57Z ERROR search: GET /api/items/399 500 3663ms
2026-03-14T09:20:00Z ERROR search: GET /api/items/0 500 3700ms
2026-03-14T09:20:03Z ERROR search: GET /api/items/1 500 3737ms
2026-03-14T09:20:06Z ERROR search: GET /api/items/2 500 3774ms
2026-03-14T09:20:09Z ERROR search: GET /api/items/3 500 3811ms
2026-03-14T09:20:12Z ERROR search: GET /api/items/4 500 3848ms
2026-03-14T09:20:15Z ERROR search: GET /api/items/5 500 3885ms
2026-03-14T09:20:18Z ERROR search: GET /api/items/6 500 3922ms
2026-03-14T09:20:21Z ERROR search: GET /api/items/7 500 3959ms
2026-03-14T09:20:24Z ERROR search: GET /api/items/8 500 3996ms
2026-03-14T09:20:27Z ERROR search: GET /api/items/9 500 4033ms
2026-03-14T09:20:30Z ERROR search: GET /api/items/10 500 4070ms
2026-03-14T09:20:33Z ERROR search: GET /api/items/11 500 4107ms
2026-03-14T09:20:36Z ERROR search: GET /api/items/12 500 4144ms
2026-03-14T09:20:39Z ERROR search: GET /api/items/13 500 4181ms
2026-03-14T09:20:42Z ERROR search: GET /api/items/14 500 4218ms
2026-03-14T09:20:45Z ERROR search: GET /api/items/15 500 4255ms
2026-03-14T09:20:48Z ERROR search: GET /api/items/16 500 4292ms
2026-03-14T09:20:51Z ERROR search: GET /api/items/17 500 4329ms
2026-03-14T09:20:54Z ERROR search: GET /api/items/18 500 4366ms
2026-03-14T09:20:57Z ERROR search: GET /api/items/19 500 4403ms
2026-03-14T09:21:00Z ERROR search: GET /api/items/20 500 4440ms
2026-03-14T09:21:03Z ERROR search: GET /api/items/21 500 4477ms
2026-03-14T09:21:06Z ERROR search: GET /api/items/22 500 4514ms
2026-03-14T09:21:09Z ERROR search: GET /api/items/23 500 4551ms
2026-03-14T09:21:12Z ERROR search: GET /api/items/24 500 4588ms
2026-03-14T09:21:15Z ERROR search: GET /api/items/25 500 4625ms
2026-03-14T09:21:18Z ERROR search: GET /api/items/26 500 4662ms
2026-03-14T09:21:21Z ERROR search: GET /api/items/27 500 4699ms
2026-03-14T09:21:24Z ERROR search: GET /api/items/28 500 4736ms
2026-03-14T09:21:27Z ERROR search: GET /api/items/29 500 4773ms
2026-03-14T09:21:30Z ERROR search: GET /api/items/30 500 4810ms
2026-03-14T09:21:33Z ERROR search: GET /api/items/31 500 4847ms
2026-03-14T09:21:36Z ERROR search: GET /api/items/32 500 4884ms
2026-03-14T09:21:39Z INFO search: GET /api/items/33 200 53ms
2026-03-14T09:21:42Z INFO search: GET /api/items/34 200 54ms
2026-03-14T09:21:45Z INFO search: GET /api/items/35 200 55ms
2026-03-14T09:21:48Z INFO search: GET /api/items/36 200 56ms
2026-03-14T09:21:51Z INFO search: GET /api/items/37 200 57ms
2026-03-14T09:21:54Z INFO search: GET /api/items/38 200 58ms
2026-03-14T09:21:57Z INFO search: GET /api/items/39 200 59ms
2026-03-14T09:22:00Z INFO search: GET /api/items/40 200 20ms
2026-03-14T09:22:03Z INFO search: GET /api/items/41 200 21ms
2026-03-14T09:22:06Z INFO search: GET /api/items/42 200 22ms
2026-03-14T09:22:09Z INFO search: GET /api/items/43 200 23ms
2026-03-14T09:22:12Z INFO search: GET /api/items/44 200 24ms
2026-03-14T09:22:15Z INFO search: GET /api/items/45 200 25ms
2026-03-14T09:22:18Z INFO search: GET /api/items/46 200 26ms
2026-03-14T09:22:21Z INFO search: GET /api/items/47 200 27ms
2026-03-14T09:22:24Z INFO search: GET /api/items/48 200 28ms
2026-03-14T09:22:27Z INFO search: GET /api/items/49 200 29ms
2026-03-14T09:22:30Z INFO search: GET /api/items/50 200 30ms
2026-03-14T09:22:33Z INFO search: GET /api/items/51 200 31ms
2026-03-14T09:22:36Z INFO search: GET /api/items/52 200 32ms
2026-03-14T09:22:39Z INFO search: GET /api/items/53 200 33ms
2026-03-14T09:22:42Z INFO search: GET /api/items/54 200 34ms
2026-03-14T09:22:45Z INFO search: GET /api/items/55 200 35ms
2026-03-14T09:22:48Z INFO search: GET /api/items/56 200 36ms
2026-03-14T09:22:51Z INFO search: GET /api/items/57 200 37ms
2026-03-14T09:22:54Z INFO search: GET /api/items/58 200 38ms
2026-03-14T09:22:57Z INFO search: GET /api/items/59 200 39ms
2026-03-14T09:23:00Z INFO search: GET /api/items/60 200 40ms
2026-03-14T09:23:03Z INFO search: GET /api/items/61 200 41ms
2026-03-14T09:23:06Z INFO search: GET /api/items/62 200 42ms
2026-03-14T09:23:09Z INFO search: GET /api/items/63 200 43ms
2026-03-14T09:23:12Z INFO search: GET /api/items/64 200 44ms
2026-03-14T09:23:15Z INFO search: GET /api/items/65 200 45ms
2026-03-14T09:23:18Z INFO search: GET /api/items/66 200 46ms
2026-03-14T09:23:21Z INFO search: GET /api/items/67 200 47ms
2026-03-14T09:23:24Z INFO search: GET /api/items/68 200 48ms
2026-03-14T09:23:27Z INFO search: GET /api/items/69 200 49ms
2026-03-14T09:23:30Z INFO search: GET /api/items/70 200 50ms
2026-03-14T09:23:33Z INFO search: GET /api/items/71 200 51ms
2026-03-14T09:23:36Z INFO search: GET /api/items/72 200 52ms
2026-03-14T09:23:39Z INFO search: GET /api/items/73 200 53ms
2026-03-14T09:23:42Z INFO search: GET /api/items/74 200 54ms
2026-03-14T09:23:45Z INFO search: GET /api/items/75 200 55ms
2026-03-14T09:23:48Z INFO search: GET /api/items/76 200 56ms
2026-03-14T09:23:51Z INFO search: GET /api/items/77 200 57ms
2026-03-14T09:23:54Z INFO search: GET /api/items/78 200 58ms
2026-03-14T09:23:57Z INFO search: GET /api/items/79 200 59ms
2026-03-14T09:24:00Z INFO search: GET /api/items/80 200 20ms
2026-03-14T09:24:03Z INFO search: GET /api/items/81 200 21ms
2026-03-14T09:24:06Z INFO search: GET /api/items/82 200 22ms
2026-03-14T09:24:09Z INFO search: GET /api/items/83 200 23ms
2026-03-14T09:24:12Z INFO search: GET /api/items/84 200 24ms
2026-03-14T09:24:15Z INFO search: GET /api/items/85 200 25ms
2026-03-14T09:24:18Z INFO search: GET /api/items/86 200 26ms
2026-03-14T09:24:21Z INFO search: GET /api/items/87 200 27ms
2026-03-14T09:24:24Z INFO search: GET /api/items/88 200 28ms
2026-03-14T09:24:27Z INFO search: GET /api/items/89 200 29ms
2026-03-14T09:24:30Z INFO search: GET /api/items/90 200 30ms
2026-03-14T09:24:33Z INFO search: GET /api/items/91 200 31ms
2026-03-14T09:24:36Z INFO search: GET /api/items/92 200 32ms
2026-03-14T09:24:39Z INFO search: GET /api/items/93 200 33ms
2026-03-14T09:24:42Z INFO search: GET /api/items/94 200 34ms
2026-03-14T09:24:45Z INFO search: GET /api/items/95 200 35ms
2026-03-14T09:24:48Z INFO search: GET /api/items/96 200 36ms
2026-03-14T09:24:51Z INFO search: GET /api/items/97 200 37ms
2026-03-14T09:24:54Z INFO search: GET /api/items/98 200 38ms
2026-03-14T09:24:57Z INFO search: GET /api/items/99 200 39ms
2026-03-14T09:25:00Z INFO search: GET /api/items/100 200 40ms
2026-03-14T09:25:03Z INFO search: GET /api/items/101 200 41ms
2026-03-14T09:25:06Z INFO search: GET /api/items/102 200 42ms
2026-03-14T09:25:09Z INFO search: GET /api/items/103 200 43ms
2026-03-14T09:25:12Z INFO search: GET /api/items/104 200 44ms
2026-03-14T09:25:15Z INFO search: GET /api/items/105 200 45ms
2026-03-14T09:25:18Z INFO search: GET /api/items/106 200 46ms
2026-03-14T09:25:21Z INFO search: GET /api/items/107 200 47ms
2026-03-14T09:25:24Z INFO search: GET /api/items/108 200 48ms
2026-03-14T09:25:27Z INFO search: GET /api/items/109 200 49ms
2026-03-14T09:25:30Z INFO search: GET /api/items/110 200 50ms
2026-03-14T09:25:33Z INFO search: GET /api/items/111 200 51ms
2026-03-14T09:25:36Z INFO search: GET /api/items/112 200 52ms
2026-03-14T09:25:39Z INFO search: GET /api/items/113 200 53ms
2026-03-14T09:25:42Z INFO search: GET /api/items/114 200 54ms
2026-03-14T09:25:45Z INFO search: GET /api/items/115 200 55ms
2026-03-14T09:25:48Z INFO search: GET /api/items/116 200 56ms
2026-03-14T09:25:51Z INFO search: GET /api/items/117 200 57ms
2026-03-14T09:25:54Z INFO search: GET /api/items/118 200 58ms
2026-03-14T09:25:57Z INFO search: GET /api/items/119 200 59ms
2026-03-14T09:26:00Z INFO search: GET /api/items/120 200 20ms
2026-03-14T09:26:03Z INFO search: GET /api/items/121 200 21ms
2026-03-14T09:26:06Z INFO search: GET /api/items/122 200 22ms
2026-03-14T09:26:09Z INFO search: GET /api/items/123 200 23ms
2026-03-14T09:26:12Z INFO search: GET /api/items/124 200 24ms
2026-03-14T09:26:15Z INFO search: GET /api/items/125 200 25ms
2026-03-14T09:26:18Z INFO search: GET /api/items/126 200 26ms
2026-03-14T09:26:21Z INFO search: GET /api/items/127 200 27ms
2026-03-14T09:26:24Z INFO search: GET /api/items/128 200 28ms
2026-03-14T09:26:27Z INFO search: GET /api/items/129 200 29ms
2026-03-14T09:26:30Z INFO search: GET /api/items/130 200 30ms
2026-03-14T09:26:33Z INFO search: GET /api/items/131 200 31ms
2026-03-14T09:26:36Z INFO search: GET /api/items/132 200 32ms
2026-03-14T09:26:39Z INFO search: GET /api/items/133 200 33ms
2026-03-14T09:26:42Z INFO search: GET /api/items/134 200 34ms
2026-03-14T09:26:45Z INFO search: GET /api/items/135 200 35ms
2026-03-14T09:26:48Z INFO search: GET /api/items/136 200 36ms
2026-03-14T09:26:51Z INFO search: GET /api/items/137 200 37ms
2026-03-14T09:26:54Z INFO search: GET /api/items/138 200 38ms
2026-03-14T09:26:57Z INFO search: GET /api/items/139 200 39ms
2026-03-14T09:27:00Z INFO search: GET /api/items/140 200 40ms
2026-03-14T09:27:03Z INFO search: GET /api/items/141 200 41ms
2026-03-14T09:27:06Z INFO search: GET /api/items/142 200 42ms
2026-03-14T09:27:09Z INFO search: GET /api/items/143 200 43ms
2026-03-14T09:27:12Z INFO search: GET /api/items/144 200 44ms
2026-03-14T09:27:15Z INFO search: GET /api/items/145 200 45ms
2026-03-14T09:27:18Z INFO search: GET /api/items/146 200 46ms
2026-03-14T09:27:21Z INFO search: GET /api/items/147 200 47ms
2026-03-14T09:27:24Z INFO search: GET /api/items/148 200 48ms
2026-03-14T09:27:27Z INFO search: GET /api/items/149 200 49ms
2026-03-14T09:27:30Z INFO search: GET /api/items/150 200 50ms
2026-03-14T09:27:33Z INFO search: GET /api/items/151 200 51ms
2026-03-14T09:27:36Z INFO search: GET /api/items/152 200 52ms
2026-03-14T09:27:39Z INFO search: GET /api/items/153 200 53ms
2026-03-14T09:27:42Z INFO search: GET /api/items/154 200 54ms
2026-03-14T09:27:45Z INFO search: GET /api/items/155 200 55ms
2026-03-14T09:27:48Z INFO search: GET /api/items/156 200 56ms
2026-03-14T09:27:51Z INFO search: GET /api/items/157 200 57ms
2026-03-14T09:27:54Z INFO search: GET /api/items/158 200 58ms
2026-03-14T09:27:57Z INFO search: GET /api/items/159 200 59ms
2026-03-14T09:28:00Z INFO search: GET /api/items/160 200 20ms
2026-03-14T09:28:03Z INFO search: GET /api/items/161 200 21ms
2026-03-14T09:28:06Z INFO search: GET /api/items/162 200 22ms
2026-03-14T09:28:09Z INFO search: GET /api/items/163 200 23ms
2026-03-14T09:28:12Z INFO search: GET /api/items/164 200 24ms
2026-03-14T09:28:15Z INFO search: GET /api/items/165 200 25ms
2026-03-14T09:28:18Z INFO search: GET /api/items/166 200 26ms
2026-03-14T09:28:21Z INFO search: GET /api/items/167 200 27ms
2026-03-14T09:28:24Z INFO search: GET /api/items/168 200 28ms
2026-03-14T09:28:27Z INFO search: GET /api/items/169 200 29ms
2026-03-14T09:28:30Z INFO search: GET /api/items/170 200 30ms
2026-03-14T09:28:33Z INFO search: GET /api/items/171 200 31ms
2026-03-14T09:28:36Z INFO search: GET /api/items/172 200 32ms
2026-03-14T09:28:39Z INFO search: GET /api/items/173 200 33ms
2026-03-14T09:28:42Z INFO search: GET /api/items/174 200 34ms
2026-03-14T09:28:45Z INFO search: GET /api/items/175 200 35ms
2026-03-14T09:28:48Z INFO search: GET /api/items/176 200 36ms
2026-03-14T09:28:51Z INFO search: GET /api/items/177 200 37ms
2026-03-14T09:28:54Z INFO search: GET /api/items/178 200 38ms
2026-03-14T09:28:57Z INFO search: GET /api/items/179 200 39ms
2026-03-14T09:29:00Z INFO search: GET /api/items/180 200 40ms
2026-03-14T09:29:03Z INFO search: GET /api/items/181 200 41ms
2026-03-14T09:29:06Z INFO search: GET /api/items/182 200 42ms
2026-03-14T09:29:09Z INFO search: GET /api/items/183 200 43ms
2026-03-14T09:29:12Z INFO search: GET /api/items/184 200 44ms
2026-03-14T09:29:15Z INFO search: GET /api/items/185 200 45ms
2026-03-14T09:29:18Z INFO search: GET /api/items/186 200 46ms
2026-03-14T09:29:21Z INFO search: GET /api/items/187 200 47ms
2026-03-14T09:29:24Z INFO search: GET /api/items/188 200 48ms
2026-03-14T09:29:27Z INFO search: GET /api/items/189 200 49ms
2026-03-14T09:29:30Z INFO search: GET /api/items/190 200 50ms
2026-03-14T09:29:33Z INFO search: GET /api/items/191 200 51ms
2026-03-14T09:29:36Z INFO search: GET /api/items/192 200 52ms
2026-03-14T09:29:39Z INFO search: GET /api/items/193 200 53ms
2026-03-14T09:29:42Z INFO search: GET /api/items/194 200 54ms
2026-03-14T09:29:45Z INFO search: GET /api/items/195 200 55ms
2026-03-14T09:29:48Z INFO search: GET /api/items/196 200 56ms
2026-03-14T09:29:51Z INFO search: GET /api/items/197 200 57ms
2026-03-14T09:29:54Z INFO search: GET /api/items/198 200 58ms
2026-03-14T09:29:57Z INFO search: GET /api/items/199 200 59ms
EOF
cat > summary.json <<'EOF'
{
 "first_error": "09:11:00",
 "error_count": 312,
 "peak_latency_ms": 4888,
 "deploy": "v2.3.1"
}
EOF
```

## What to build

Write `/root/harness-lab/27-verify/verify.py`, used as `python verify.py SUMMARY_JSON LOG_FILE`. It recomputes every field from the log **with code**, no model:

| Field | Recomputed as |
|---|---|
| `first_error` | `HH:MM:SS` of the first line containing ` ERROR ` |
| `error_count` | number of ` ERROR ` lines |
| `peak_latency_ms` | the largest `<N>ms` at the end of any line |
| `deploy` | the version (`v...`) on the last ` deploy: ` line at or before the first error |

It prints `{"ok": <bool>, "mismatches": {"<field>": {"claimed": ..., "actual": ...}}}` and exits 0 if every field matches, 1 otherwise. A missing field counts as a mismatch with `claimed: null`.

```bash
cd /root/harness-lab/27-verify
python verify.py summary.json incident.log
```

The checker also plants its own errors in other fields and runs `verify.py` on a different log.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Timestamps are fixed-width, so `line[11:19]` is `HH:MM:SS` and string comparison of `line[:20]` orders them.
- Recompute from the log you're given - never hard-code the expected values.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/27-verify
cat > verify.py <<'EOF'
"""Check an incident summary against the log by recomputing every field. Usage: python verify.py SUMMARY LOG"""
import json
import re
import sys


def recompute(log_text):
    lines = log_text.splitlines()
    errors = [l for l in lines if " ERROR " in l]
    first = errors[0] if errors else None
    deploys = [l for l in lines if " deploy: " in l and (first is None or l[:20] <= first[:20])]
    latencies = [int(m.group(1)) for l in lines if (m := re.search(r" (\d+)ms$", l))]
    return {"first_error": first[11:19] if first else None, "error_count": len(errors),
            "peak_latency_ms": max(latencies) if latencies else None,
            "deploy": re.search(r" (v[\d.]+) ", deploys[-1]).group(1) if deploys else None}


def check(summary, log_text):
    actual = recompute(log_text)
    mismatches = {k: {"claimed": summary.get(k), "actual": v} for k, v in actual.items() if summary.get(k) != v}
    return {"ok": not mismatches, "mismatches": mismatches}


if __name__ == "__main__":
    result = check(json.load(open(sys.argv[1])), open(sys.argv[2]).read())
    print(json.dumps(result, indent=1))
    sys.exit(0 if result["ok"] else 1)

EOF
python verify.py summary.json incident.log || true
```

</details>

## Check your work

```bash
D=/root/harness-lab/27-verify; cd $D 2>/dev/null || echo "❌ create $D"
python - <<'PYEOF'
import json, math, os, subprocess, sys
from pathlib import Path
from openai import OpenAI
_C = OpenAI()
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def E(xs):
    return [d.embedding for d in _C.embeddings.create(model="lab-embed", input=xs).data]
def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def run(*args, cwd=None):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()
sys.path.insert(0, '/opt/harness')
from labmock import MockModel
import tempfile
def runv(summary, log):
    d = Path(tempfile.mkdtemp())
    (d / "s.json").write_text(json.dumps(summary))
    (d / "l.log").write_text(log)
    r = subprocess.run([sys.executable, "verify.py", str(d / "s.json"), str(d / "l.log")], capture_output=True, text=True, timeout=30)
    try:
        return r.returncode, json.loads(r.stdout)
    except ValueError:
        return r.returncode, {"raw": (r.stdout + r.stderr)[-200:]}
log = Path("incident.log").read_text()
truth = json.loads('{"first_error": "09:11:00", "error_count": 213, "peak_latency_ms": 4888, "deploy": "v2.3.1"}')
rc, out = runv(json.load(open("summary.json")), log)
ok(rc == 1 and out.get("ok") is False and list((out.get("mismatches") or {}).keys()) == ["error_count"] and out["mismatches"]["error_count"] == {"claimed": 312, "actual": truth["error_count"]},
   f"verify.py catches the planted error_count (312 claimed, {truth['error_count']} in the log)", f"exit {rc}, output {out}")
rc, out = runv(truth, log)
ok(rc == 0 and out.get("ok") is True and not out.get("mismatches"), "a correct summary passes", f"exit {rc}, output {out}")
missed = []
for field, bad in [("first_error", "09:14:00"), ("peak_latency_ms", 1234), ("deploy", "v2.3.0")]:
    rc, out = runv(dict(truth, **{field: bad}), log)
    if not (rc == 1 and list((out.get("mismatches") or {}).keys()) == [field]):
        missed.append(field)
rc, out = runv({k: v for k, v in truth.items() if k != "deploy"}, log)
if not (rc == 1 and (out.get("mismatches") or {}).get("deploy", {}).get("claimed", "x") is None):
    missed.append("missing deploy")
ok(not missed, "planted errors in every other field are caught, and only that field is flagged", f"not caught correctly: {missed}")
small = "2026-04-02T10:00:00Z INFO deploy: billing v9.1.0 rolled out\n2026-04-02T10:00:05Z INFO billing: POST /pay 200 31ms\n2026-04-02T10:00:09Z ERROR billing: POST /pay 500 777ms\n2026-04-02T10:00:12Z INFO deploy: billing v9.1.1 rolled out\n2026-04-02T10:00:15Z ERROR billing: POST /pay 500 95ms\n"
rc, out = runv({"first_error": "10:00:09", "error_count": 2, "peak_latency_ms": 777, "deploy": "v9.1.0"}, small)
ok(rc == 0 and out.get("ok") is True, "verify.py recomputes from whatever log it's given", f"on a different log the correct summary should pass - got exit {rc}, {out}")
PYEOF
```

## What you learned

- Adversarial checks try to prove the answer wrong, and fail by default.
- When a claim can be recomputed from the source, check it with code instead of a model.
- Plant an error in every field to prove the checker catches it - and keep those as tests.
